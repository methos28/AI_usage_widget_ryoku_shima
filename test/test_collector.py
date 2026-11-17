#!/usr/bin/env python3
"""Fixture tests for the OpenCode collector.

Runs the collector against throwaway stores and a temp cache; the real
~/.cache/opencode-usage.json is never touched.

    python3 test/test_collector.py
"""
import fcntl
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path

COLLECTOR = Path(os.environ.get('OPENCODE_USAGE_TEST_COLLECTOR',
                              Path(__file__).resolve().parent.parent / "collector" / "opencode-usage-v2"))


def now_ms() -> int:
    return int(time.time() * 1000)


def write_v2_store(data_dir: Path, cache_read: int = 40000) -> None:
    db = sqlite3.connect(data_dir / "opencode.db")
    db.execute(
        "create table session_message("
        "session_id text, type text, time_created integer, data text)")
    db.execute(
        "create table session_v2("
        "id text, title text, directory text, model text, "
        "tokens_input integer, tokens_output integer, tokens_reasoning integer, "
        "tokens_cache_read integer, tokens_cache_write integer, cost real, "
        "time_created integer, time_updated integer, time_idle integer, time_busy integer)")
    stamp = now_ms()
    message = {
        "role": "assistant",
        "tokens": {
            "input": 5000, "output": 1200, "reasoning": 80,
            "cache": {"read": cache_read, "write": 10},
        },
        "model": {"id": "gpt-5.5", "providerID": "openai"},
        "time": {"created": stamp - 60000, "completed": stamp - 30000},
        "cost": 0.42,
    }
    db.execute(
        "insert into session_message values(?,?,?,?)",
        ("ses_1", "assistant", stamp - 30000, json.dumps(message)))
    db.execute(
        "insert into session_v2 values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("ses_1", "Fixture session", "/tmp/work",
         json.dumps({"id": "gpt-5.5", "providerID": "openai"}),
         5000, 1200, 80, cache_read, 10, 0.42,
         stamp - 120000, stamp, stamp - 1000, stamp - 2000))
    db.commit()
    db.close()


def run_collector(data_dir: Path, cache: Path, umask=0o077) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["OPENCODE_DATA_DIR"] = str(data_dir)
    env["HOME"] = str(data_dir.parent)
    return subprocess.run(
        [sys.executable, str(COLLECTOR), "--cache", str(cache)],
        env=env, capture_output=True, text=True, timeout=30, umask=umask)


class CollectorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.data = self.root / "opencode"
        self.data.mkdir()
        self.cache = self.root / "cache.json"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def read_cache(self) -> dict:
        return json.loads(self.cache.read_text())

    def test_private_atomic_publish_does_not_follow_a_temporary_symlink(self):
        write_v2_store(self.data)
        canary = self.root / 'do-not-change'
        canary.write_text('keep')
        self.cache.with_name(self.cache.name + '.tmp').symlink_to(canary)
        result = run_collector(self.data, self.cache, umask=0o022)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(canary.read_text(), 'keep')
        self.assertFalse(self.cache.is_symlink())
        self.assertEqual(self.cache.stat().st_mode & 0o777, 0o600)

    def test_lock_symlink_is_rejected_without_truncating_its_target(self):
        write_v2_store(self.data)
        canary = self.root / 'do-not-change'
        canary.write_text('keep')
        self.cache.with_name(self.cache.name + '.lock').symlink_to(canary)
        result = run_collector(self.data, self.cache)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(canary.read_text(), 'keep')
        self.assertFalse(self.cache.exists())

    def test_non_finite_source_values_do_not_poison_the_cache(self):
        write_v2_store(self.data)
        db = sqlite3.connect(self.data / 'opencode.db')
        row = json.loads(db.execute('select data from session_message').fetchone()[0])
        row['cost'] = float('nan')
        row['tokens']['input'] = float('inf')
        db.execute('update session_message set data=?', (json.dumps(row),))
        db.commit(); db.close()
        result = run_collector(self.data, self.cache)
        self.assertEqual(result.returncode, 0, result.stderr)
        def reject(value):
            raise AssertionError('non-finite JSON value: ' + value)
        json.loads(self.cache.read_text(), parse_constant=reject)

    def test_sqlite_data_paths_with_uri_characters_are_read(self):
        special=self.root/'data #notes?100%'
        special.mkdir()
        write_v2_store(special)
        result=run_collector(special,self.cache)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(self.cache.exists())
        self.assertGreater(self.read_cache()['_today_tokens'],0)

    def test_drifted_schema_without_sql_timestamp_uses_json_time(self):
        stamp=now_ms()
        db=sqlite3.connect(self.data/'opencode.db')
        db.execute('create table session_message(session text, role text, content text)')
        row={'role':'assistant','tokens':{'input':3,'output':2,'cache':{'read':7}},
             'model':{'id':'schema-fixture'},'time':{'created':stamp},'cost':.01}
        db.execute('insert into session_message values(?,?,?)',('s','assistant',json.dumps(row)))
        db.commit();db.close()
        result=run_collector(self.data,self.cache)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.read_cache()['_today_tokens_with_cache_read'],12)

    def test_open_sessions_keep_an_older_busy_session_before_newer_idle_rows(self):
        write_v2_store(self.data)
        db=sqlite3.connect(self.data/'opencode.db')
        stamp=now_ms()
        for index in range(12):
            busy=index==0
            db.execute('insert into session_v2 values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                ('extra-'+str(index),'fixture','/fixture','{}',0,0,0,0,0,0,
                 stamp-30000,stamp-20000 if busy else stamp,
                 stamp-20000 if busy else stamp,stamp-10000))
        db.commit();db.close()
        result=run_collector(self.data,self.cache)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.read_cache()['_sessions'][0]['id'],'extra-0')
        self.assertTrue(self.read_cache()['_sessions'][0]['running'])

    def test_version(self) -> None:
        out = subprocess.run(
            [sys.executable, str(COLLECTOR), "--version"],
            capture_output=True, text=True, check=True)
        self.assertIn(COLLECTOR.name, out.stdout)

    def test_v2_store_fields(self) -> None:
        write_v2_store(self.data)
        proc = run_collector(self.data, self.cache)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = self.read_cache()

        self.assertEqual(data["_source"], os.environ.get('OPENCODE_USAGE_TEST_SOURCE', 'storage+v2'))
        self.assertGreater(data["_today_tokens"], 0)
        self.assertEqual(len(data["_hours"]), 48)
        self.assertIn("today", data["_periods"])
        self.assertIn("all", data["_periods"])
        self.assertGreater(data["_periods"]["all"]["tokens"], 0)
        self.assertTrue(data["_sessions"])
        self.assertTrue(data["_models"])
        self.assertEqual(len(data["_recent_days"]), 7)

        today = datetime.now().strftime("%Y-%m-%d")
        day = next(row for row in data["_days"] if row["date"] == today)
        self.assertGreater(day["tokens"], 0)
        self.assertGreaterEqual(day["cost"], 0.42)
        self.assertEqual(day["cacheRead"], 40000)

    def test_aggregate_residual_is_added_once(self) -> None:
        write_v2_store(self.data)
        db = sqlite3.connect(self.data / "opencode.db")
        db.execute(
            "update session_v2 set tokens_cache_read = tokens_cache_read + 1000")
        db.commit()
        db.close()

        proc = run_collector(self.data, self.cache)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        today = datetime.now().strftime("%Y-%m-%d")
        day = next(row for row in self.read_cache()["_days"] if row["date"] == today)
        self.assertEqual(day["cacheRead"], 41000)

    def test_old_session_lifetime_residual_does_not_enter_recent_usage(self) -> None:
        write_v2_store(self.data)
        expected = run_collector(self.data, self.cache)
        self.assertEqual(expected.returncode, 0, expected.stderr)
        before = self.read_cache()
        with sqlite3.connect(self.data / "opencode.db") as db:
            db.execute("update session_v2 set time_created=?, tokens_input=tokens_input+9000, cost=cost+9",
                       (now_ms() - 731 * 86400000,))
        result = run_collector(self.data, self.cache)
        self.assertEqual(result.returncode, 0, result.stderr)
        after = self.read_cache()
        self.assertEqual(after['_today_tokens'], before['_today_tokens'])
        self.assertEqual(after['_days'], before['_days'])
        self.assertEqual(after['_periods']['7']['cost'], before['_periods']['7']['cost'])

    def test_unknown_session_age_does_not_date_a_lifetime_residual(self) -> None:
        write_v2_store(self.data)
        with sqlite3.connect(self.data / "opencode.db") as db:
            db.execute("update session_v2 set time_created=NULL, tokens_cache_read=41000")
        result = run_collector(self.data, self.cache)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read_cache()['_days'][-1]['cacheRead'], 40000)

    def test_aggregate_only_fallback_requires_history_within_loaded_horizon(self) -> None:
        for age in ('old','unknown','recent'):
            with self.subTest(age=age), tempfile.TemporaryDirectory(dir=self.root) as directory:
                data=Path(directory);cache=data/'usage.json'
                write_v2_store(data)
                created=now_ms()-120000 if age=='recent' else now_ms()-731*86400000 if age=='old' else None
                with sqlite3.connect(data/'opencode.db') as db:
                    db.execute('delete from session_message')
                    db.execute('update session_v2 set time_created=?',(created,))
                result=run_collector(data,cache)
                self.assertEqual(result.returncode,0,result.stderr)
                if age=='recent':
                    self.assertGreater(json.loads(cache.read_text())['_today_tokens'],0)
                else:
                    self.assertFalse(cache.exists())

    def test_stale_recovery_preserves_days_hours_and_freshness_marker(self) -> None:
        write_v2_store(self.data)
        self.assertEqual(run_collector(self.data,self.cache).returncode,0)
        before=self.read_cache();source=before['_source']
        before['_days'][-1]['tokens']+=9000
        before['_hours'][-1]['tokens']+=9000
        self.cache.write_text(json.dumps(before))
        db=self.data/'opencode.db';offline=self.data/'opencode.offline'
        db.rename(offline)
        self.assertEqual(run_collector(self.data,self.cache).returncode,0)
        stale=self.read_cache()
        self.assertEqual(stale['_source'],source)
        self.assertTrue(stale['_stale'])
        offline.rename(db)
        for legacy in (False,True):
            with self.subTest(legacy=legacy):
                snapshot=dict(stale)
                if legacy:
                    snapshot['_source']='stale'
                    snapshot.pop('_stale')
                self.cache.write_text(json.dumps(snapshot))
                self.assertEqual(run_collector(self.data,self.cache).returncode,0)
                recovered=self.read_cache()
                self.assertEqual(recovered['_days'][-1]['tokens'],before['_days'][-1]['tokens'])
                self.assertEqual(recovered['_hours'][-1]['tokens'],before['_hours'][-1]['tokens'])
                self.assertFalse(recovered.get('_stale',False))
                self.assertEqual(recovered['_source'],source)

    def test_day_history_never_decreases(self) -> None:
        write_v2_store(self.data)
        run_collector(self.data, self.cache)
        data = self.read_cache()
        today = datetime.now().strftime("%Y-%m-%d")
        row = next(day for day in data["_days"] if day["date"] == today)
        row["tokens"] = 9_000_000
        self.cache.write_text(json.dumps(data))

        proc = run_collector(self.data, self.cache)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        after = next(day for day in self.read_cache()["_days"] if day["date"] == today)
        self.assertGreaterEqual(after["tokens"], 9_000_000)

    def test_lock_skips_a_concurrent_run(self) -> None:
        write_v2_store(self.data)
        run_collector(self.data, self.cache)
        before = self.cache.read_text()
        lock_path = self.cache.with_name(self.cache.name + ".lock")
        with lock_path.open("w") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            proc = run_collector(self.data, self.cache)
        self.assertEqual(proc.returncode, 75, proc.stderr)
        self.assertEqual(self.cache.read_text(), before)

    def test_file_store_fallback(self) -> None:
        folder = self.data / "storage" / "message" / "ses_2"
        folder.mkdir(parents=True)
        stamp = now_ms()
        (folder / "m1.json").write_text(json.dumps({
            "role": "assistant",
            "modelID": "gpt-5.5",
            "providerID": "openai",
            "tokens": {"input": 700, "output": 300, "reasoning": 0,
                       "cache": {"read": 1200, "write": 0}},
            "time": {"created": stamp - 1000, "completed": stamp - 500},
            "cost": 0.02,
        }))

        proc = run_collector(self.data, self.cache)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = self.read_cache()
        self.assertGreater(data["_today_tokens"], 0)
        self.assertGreater(data["_periods"]["all"]["tokens"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
