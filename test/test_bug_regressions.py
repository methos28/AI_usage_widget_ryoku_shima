"""Isolated regression probes against the committed module; no live writes."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from contextlib import closing
from unittest.mock import patch
import json
import os
import runpy
import sqlite3
import tempfile
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
WIDGET = Path(os.environ.get('AI_USAGE_TEST_WIDGET', ROOT/'ai-usage'))
codex = runpy.run_path(str(ROOT/'test/test_codex_usage.py'))
claude = runpy.run_path(str(ROOT/'test/test_claude_usage.py'))
opencode = runpy.run_path(str(ROOT/'test/test_collector.py'))
widget = runpy.run_path(str(ROOT/'test/test_widget.py'))


class Audit(unittest.TestCase):
    def test_three_store_copies_use_one_native_request_identity(self):
        f = self.opencode_fixture()
        opencode['write_v2_store'](f.data)
        with closing(sqlite3.connect(f.data/'opencode.db')) as connection, connection:
            raw, stamp = connection.execute('select data,time_created from session_message').fetchone()
            current = json.loads(raw)
            current['id'] = 'message-one'
            connection.execute('update session_message set data=?', (json.dumps(current),))
            legacy = dict(current, modelID=current['model']['id'], providerID='openai', sessionID='ses_1')
            connection.execute('create table message(id text, session_id text, time_created integer, time_updated integer, data text)')
            connection.execute('insert into message values(?,?,?,?,?)',
                               ('message-one', 'ses_1', stamp, stamp, json.dumps(legacy)))
        folder = f.data/'storage/message/ses_1'
        folder.mkdir(parents=True)
        (folder/'message-one.json').write_text(json.dumps(legacy))
        result = opencode['run_collector'](f.data, f.cache)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(f.read_cache()['_periods']['all']['tokens'], 6290)

    def test_login_change_during_rpc_does_not_publish_the_old_quota(self):
        f = self.codex_fixture()
        with patch.dict(os.environ, f.env, clear=True):
            module = runpy.run_path(str(codex['COLLECTOR']))
            namespace = module['throttled_rpc'].__globals__
            from unittest.mock import Mock
            context = Mock(side_effect=['before', 'after'])
            with patch.dict(namespace, rpc_context=context,
                            fetch_rpc=lambda: {'rateLimits': {'planType': 'plus'}}):
                result = module['throttled_rpc']()
            self.assertEqual(result['rateLimits'], {})
            self.assertFalse(module['RPC_FILE'].exists())

    def test_unknown_login_context_does_not_reuse_quota_cache(self):
        f = self.codex_fixture()
        env = dict(f.env)
        env.pop('OPENAI_API_KEY', None)
        with patch.dict(os.environ, env, clear=True):
            module = runpy.run_path(str(codex['COLLECTOR']))
            namespace = module['throttled_rpc'].__globals__
            from unittest.mock import Mock
            fetch = Mock(return_value={'source': 'rpc'})
            with patch.dict(namespace, fetch_rpc=fetch):
                module['throttled_rpc']()
                module['throttled_rpc']()
            self.assertEqual(fetch.call_count, 2)

    def test_native_qt_clears_stale_activity_and_failed_parse(self):
        result = subprocess.run([sys.executable, str(ROOT/'test/native_bug_ui.py')],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_overlap_dedup_preserves_distinct_ids_and_request_multiplicity(self):
        f = self.opencode_fixture()
        module = runpy.run_path(str(opencode['COLLECTOR']))
        row = dict(session_id='s', model_id='m', provider_id='', time=1, input=10,
                   output=1, reasoning=0, cache_read=0, cache_write=0, cost=0)
        merge = module['merge_message_stores']
        self.assertEqual(len(merge([dict(row, _message_id='one')],
                                   [dict(row, _message_id='one')])), 1)
        self.assertEqual(len(merge([dict(row, _message_id='one')],
                                   [dict(row, _message_id='two')])), 2)
        self.assertEqual(len(merge([dict(row), dict(row)],
                                   [dict(row), dict(row)])), 2)
        self.assertEqual(len(merge([dict(row)], [dict(row), dict(row)])), 2)

    def test_quota_cache_invalidates_environment_key_changes(self):
        f = self.codex_fixture()
        f.env = f.rpc_fixture()
        self.assertTrue(f.collect()['_windows'])
        f.env.update(RPC_ACCOUNT_TYPE='apiKey', OPENAI_API_KEY='NEW-FAKE-KEY')
        self.assertEqual(f.collect()['_windows'], [])
        saved = f.cache.with_name('usage-rpc.json').read_text()
        self.assertNotIn('NEW-FAKE-KEY', saved)
        self.assertNotIn('FAKE-CREDENTIAL', saved)

    def test_quota_cache_never_reads_credential_file_contents(self):
        f = self.codex_fixture()
        auth = f.sessions.parent/'auth.json'
        auth.write_text('credential canary')
        with patch.dict(os.environ, f.env, clear=True):
            module = runpy.run_path(str(codex['COLLECTOR']))
            with patch.object(Path, 'open', side_effect=AssertionError('Credential contents read')):
                self.assertIsInstance(module['rpc_context'](), str)

    def test_future_codex_request_is_counted_once_after_clock_catches_up(self):
        f = self.codex_fixture()
        f.write(f.path, [f.meta('one'), f.event(1000, 200, 300, 2)])
        self.assertEqual(f.collect()['_periods']['all']['tokens'], 0)
        f.env['CODEX_USAGE_NOW'] = str(f.now+3)
        self.assertEqual(f.collect()['_periods']['all']['tokens'], 800)
        self.assertEqual(f.collect()['_periods']['all']['tokens'], 800)

    def codex_fixture(self):
        fixture = codex['CodexUsageTest']('test_repeat_snapshot_and_unchanged_refresh')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        return fixture

    def claude_fixture(self):
        fixture = claude['ClaudePreviewTest']('test_streaming_max_and_bad_tail')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        return fixture

    def opencode_fixture(self):
        fixture = opencode['CollectorTest']('test_private_atomic_publish_does_not_follow_a_temporary_symlink')
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        return fixture

    def test_01_codex_cached_chatgpt_quota_survives_switch_to_api_key(self):
        f = self.codex_fixture()
        f.env = f.rpc_fixture()
        auth = f.sessions.parent/'auth.json'
        auth.write_text('{"fixture_account":"chatgpt"}')
        first = f.collect()
        self.assertTrue(first['_windows'])
        f.env['RPC_ACCOUNT_TYPE'] = 'apiKey'
        auth.write_text('{"fixture_account":"api-key-login"}')
        f.env['CODEX_USAGE_NOW'] = str(f.now + 1)
        second = f.collect()
        print('account switch:', second['_plan'], second['_windows'], flush=True)
        self.assertEqual(second['_windows'], [], 'API-key login must not retain the prior ChatGPT quota')

    def test_02_codex_malformed_retained_state_should_not_stop_collection(self):
        f = self.codex_fixture()
        f.activity.write_text(json.dumps({'schemaVersion': 5, 'seenTokenEvents': ['broken']}))
        try:
            f.collect()
        except Exception as error:
            self.fail('Collector crashed on malformed retained state: ' + str(getattr(error, 'stderr', error)))

    def test_03_opencode_mixed_stores_should_retain_distinct_sessions(self):
        f = self.opencode_fixture()
        opencode['write_v2_store'](f.data)
        legacy = f.data/'storage/message/legacy-session'
        legacy.mkdir(parents=True)
        (legacy/'message.json').write_text(json.dumps({
            'role': 'assistant', 'sessionID': 'legacy-session', 'modelID': 'legacy-model',
            'tokens': {'input': 2000, 'output': 0, 'cache': {'read': 0, 'write': 0}},
            'time': {'created': opencode['now_ms']()}, 'cost': 0}))
        result = opencode['run_collector'](f.data, f.cache)
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = f.read_cache()['_periods']['all']['tokens']
        print('mixed stores:', actual, 'expected:', 6290+2000, flush=True)
        self.assertEqual(actual, 8290, 'Distinct legacy session vanished when v2 rows existed')

    def test_04_opencode_bad_message_should_not_hide_valid_messages(self):
        f = self.opencode_fixture()
        opencode['write_v2_store'](f.data)
        with closing(sqlite3.connect(f.data/'opencode.db')) as connection, connection:
            bad = {'model': {'id': 'bad-record'}, 'tokens': [1], 'time': {'created': opencode['now_ms']()}}
            connection.execute('insert into session_message values(?,?,?,?)',
                               ('bad', 'assistant', opencode['now_ms'](), json.dumps(bad)))
        result = opencode['run_collector'](f.data, f.cache)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(f.read_cache()['_today_tokens'], 0)

    def test_05_claude_future_usage_should_not_be_counted_today(self):
        f = self.claude_fixture()
        f.event['timestamp'] = (datetime.now(timezone.utc)+timedelta(days=2)).isoformat()
        (f.projects/'future.jsonl').write_text(json.dumps(f.event)+'\n')
        data = f.run_collector()
        print('future Claude:', data['_today_tokens'], '24h:', data['_periods']['24h']['tokens'], flush=True)
        self.assertEqual(data['_today_tokens'], 0, 'Future requests cannot belong to today')

    def test_06_codex_future_usage_should_not_be_counted_today(self):
        f = self.codex_fixture()
        f.write(f.path, [f.meta('one'), f.event(1000, 200, 300, 86400)])
        data = f.collect()
        print('future Codex:', data['_today_tokens'], 'rate:', data['_rate_per_hour'],
              'today period:', data['_periods']['today']['tokens'],
              '24h:', data['_periods']['24h']['tokens'], flush=True)
        self.assertEqual(data['_today_tokens'], 0, 'Future requests cannot belong to today')
        self.assertEqual(data['_rate_per_hour'], 0, 'Future requests cannot belong to the past hour')
        self.assertEqual(data['_periods']['today']['tokens'], 0)

    def test_07_codex_bad_published_hour_should_not_block_fresh_usage(self):
        f = self.codex_fixture()
        f.cache.write_text(json.dumps({'_source': 'rpc', '_hours': [None]}))
        try:
            data = f.collect()
        except Exception as error:
            self.fail('Collector crashed on a malformed published hour: ' + str(getattr(error, 'stderr', error)))
        self.assertEqual(data['_today_tokens'], 3000)

    def test_08_stale_usage_cache_should_not_claim_live_running_session(self):
        source = (WIDGET/'UsageModel.qml').read_text()
        names = ('empty', 'pct', 'normalizeWindows', 'shortName', 'normalizePeriods', 'kmg', 'updateFreshness', 'parse')
        script = widget['SETUP']+'\n'+'\n'.join(widget['function'](source, name) for name in names)
        script += '\nconst root={'+','.join(names)+'}; const switchTimer={stop(){}};'
        script += '''
root.parse(JSON.stringify({_source:'rpc',_sessions:[{id:'old',title:'Old session',running:true}]}),clock/1000-3600);
assert.equal(root.fresh,false);
'''
        expression = source.split('readonly property var runningSessions: ', 1)[1].splitlines()[0]
        script += 'const active='+expression+";\nassert.equal(active.length,0,'Stale session is live');"
        widget['node'](script)

    def test_09_qml_malformed_period_should_not_leave_partial_valid_state(self):
        source = (WIDGET/'UsageModel.qml').read_text()
        names = ('empty', 'pct', 'normalizeWindows', 'shortName', 'normalizePeriods', 'kmg', 'updateFreshness', 'parse')
        script = widget['SETUP']+'\n'+'\n'.join(widget['function'](source, name) for name in names)
        script += '\nconst root={'+','.join(names)+'}; const switchTimer={stop(){}};'
        script += '''
root.parse(JSON.stringify({_source:'rpc',_today_tokens:999,_periods:{today:{models:[null]}}}),clock/1000);
assert.equal(root.has,false,'A failed parse left the card marked valid');
'''
        widget['node'](script)

    def test_10_opencode_future_usage_should_not_be_counted_today(self):
        f = self.opencode_fixture()
        opencode['write_v2_store'](f.data)
        future = opencode['now_ms']() + 2 * 86400000
        with closing(sqlite3.connect(f.data/'opencode.db')) as connection, connection:
            row = {'model': {'id': 'future-record'}, 'tokens': {'input': 1600},
                   'time': {'created': future}}
            connection.execute('insert into session_message values(?,?,?,?)',
                               ('future', 'assistant', future, json.dumps(row)))
        result = opencode['run_collector'](f.data, f.cache)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = f.read_cache()
        print('future OpenCode:', data['_today_tokens'], 'expected:', 6290, flush=True)
        self.assertEqual(data['_today_tokens'], 6290, 'Future requests cannot belong to today')


if __name__ == '__main__':
    unittest.main(verbosity=2)
