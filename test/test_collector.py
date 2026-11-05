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

COLLECTOR = Path(__file__).resolve().parent.parent / "collector" / "opencode-usage-v2"


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


def run_collector(data_dir: Path, cache: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["OPENCODE_DATA_DIR"] = str(data_dir)
    env["HOME"] = str(data_dir.parent)
    return subprocess.run(
        [sys.executable, str(COLLECTOR), "--cache", str(cache)],
        env=env, capture_output=True, text=True, timeout=30)


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

    def test_version(self) -> None:
        out = subprocess.run(
            [sys.executable, str(COLLECTOR), "--version"],
            capture_output=True, text=True, check=True)
        self.assertIn("opencode-usage-v2", out.stdout)

    def test_v2_store_fields(self) -> None:
        write_v2_store(self.data)
        proc = run_collector(self.data, self.cache)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = self.read_cache()

        self.assertEqual(data["_source"], "storage+v2")
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
        self.assertEqual(proc.returncode, 0, proc.stderr)
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
