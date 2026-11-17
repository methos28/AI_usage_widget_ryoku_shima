import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch


HELPER = Path(__file__).resolve().parents[1] / 'ai-usage/bin/claude-sessions.py'
HELPERS = runpy.run_path(str(HELPER))
COLLECT = HELPERS['collect_sessions']
NOW = 1794219000000


class ClaudeSessionsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / 'claude'
        self.projects = self.config / 'projects/project'
        self.projects.mkdir(parents=True)
        (self.config / 'sessions').mkdir()
        self.proc = self.root / 'proc'
        (self.proc / 'self/ns').mkdir(parents=True)
        (self.proc / 'self/ns/pid').symlink_to('pid:[123]')

    def event(self, kind, offset=0, **fields):
        return dict(type=kind, sessionId='session', timestamp=NOW - 10000 + offset,
                    cwd='/fixture', **fields)

    def transcript(self, events, filename='session.jsonl', tail=''):
        (self.projects / filename).write_text(''.join(json.dumps(e) + '\n' for e in events) + tail)

    def native(self, status='working', **fields):
        metadata = dict(sessionId='session', pid=42, procStart='9000', status=status,
                        startedAt=NOW - 20000, updatedAt=NOW - 5000,
                        cwd='/fixture', pidDomain='linux:fixture:pid:[123]')
        metadata.update(fields)
        (self.config / 'sessions/42.json').write_text(json.dumps(metadata))

    def process(self, start='9000', state='S'):
        (self.proc / '42').mkdir(exist_ok=True)
        # Linux stat fields 3..22; comm can contain spaces and parentheses.
        fields = [state] + ['0'] * 18 + [start]
        (self.proc / '42/stat').write_text('42 (Claude (worker)) ' + ' '.join(fields))

    def result(self):
        return COLLECT(self.config, now_ms=NOW, proc_root=self.proc)['session']

    def test_shared_transcript_state_matches_standalone_lifecycle(self):
        events = [self.event('user',message={'content':'fixture'}),
                  self.event('assistant',100,message={'stop_reason':'end_turn'}),
                  self.event('custom-title',200,customTitle='Fixture title')]
        self.transcript(events)
        self.native(status='idle')
        self.process()
        expected=COLLECT(self.config,now_ms=NOW,proc_root=self.proc)
        state=HELPERS['TranscriptState'](NOW)
        path=self.projects/'session.jsonl'
        for index,event in enumerate(events):
            state.observe(event,path,index)
        with patch.object(Path,'rglob',side_effect=AssertionError('transcript rescan')):
            actual=COLLECT(self.config,now_ms=NOW,proc_root=self.proc,transcript_state=state)
        self.assertEqual(actual,expected)

    def test_reused_state_clears_running_when_idle_completed_or_dead(self):
        for ending in ('idle','completed','dead'):
            with self.subTest(ending=ending):
                state=HELPERS['TranscriptState'](NOW)
                state.observe(self.event('user',message={'content':'fixture'}),self.projects/'session.jsonl',0)
                self.native(status='working')
                self.process()
                self.assertTrue(COLLECT(self.config,now_ms=NOW,proc_root=self.proc,transcript_state=state)['session']['running'])
                if ending=='idle':
                    self.native(status='idle')
                elif ending=='completed':
                    state.observe(self.event('assistant',9500,message={'stop_reason':'end_turn'}),self.projects/'session.jsonl',1)
                else:
                    (self.proc/'42/stat').unlink()
                result=COLLECT(self.config,now_ms=NOW,proc_root=self.proc,transcript_state=state)['session']
                self.assertFalse(result['running'])

    def test_user_start_is_visible_before_first_usage_when_native_process_is_working(self):
        self.transcript([self.event('user', message={'content': 'fixture'})])
        self.native()
        self.process()
        row = self.result()
        self.assertTrue(row['running'])
        self.assertEqual(row['activityEvidence'], 'native_working')
        self.assertEqual(row['directory'], '/fixture')
        self.assertEqual(row['started'], NOW - 20000)

    def test_tool_use_and_result_continue_turn_with_live_process(self):
        self.transcript([
            self.event('assistant', message={'stop_reason': 'tool_use'}),
            self.event('user', 100, message={'content': [{'type': 'tool_result', 'content': 'fixture'}]},
                       toolUseResult={}),
        ])
        self.native(status=None)
        self.process()
        self.assertTrue(self.result()['running'])
        self.assertEqual(self.result()['activityEvidence'], 'live_process_unfinished_turn')

    def test_end_turn_completes_even_when_process_remains_open(self):
        self.transcript([self.event('assistant', message={'stop_reason': 'end_turn'})])
        self.native(status=None)
        self.process()
        self.assertFalse(self.result()['running'])
        self.assertEqual(self.result()['activityState'], 'completed')

    def test_native_idle_overrides_unfinished_history(self):
        self.transcript([self.event('api-request')])
        self.native(status='idle')
        self.process()
        self.assertFalse(self.result()['running'])
        self.assertEqual(self.result()['activityEvidence'], 'native_idle')

    def test_native_waiting_is_not_executing(self):
        self.transcript([self.event('api-request')])
        self.native(status='waiting_for_permission')
        self.process()
        self.assertFalse(self.result()['running'])
        self.assertEqual(self.result()['activityState'], 'waiting')

    def test_user_interruption_stops_turn(self):
        self.transcript([self.event('api-request'), self.event('user', 100,
            message={'content': [{'type': 'text', 'text': '[Request interrupted by user]'}]})])
        self.native(status=None)
        self.process()
        self.assertFalse(self.result()['running'])
        self.assertEqual(self.result()['activityState'], 'interrupted')

    def test_stop_hook_summary_ends_turn_unless_hook_prevented_continuation(self):
        self.native(status=None)
        self.process()
        self.transcript([self.event('api-request'), self.event('system', 100,
            subtype='stop_hook_summary', preventedContinuation=False)])
        self.assertFalse(self.result()['running'])
        self.transcript([self.event('api-request'), self.event('system', 100,
            subtype='stop_hook_summary', preventedContinuation=True)])
        self.assertTrue(self.result()['running'])

    def test_recent_and_old_unfinished_transcripts_never_prove_running(self):
        for age in (1, 86400000):
            self.transcript([self.event('api-request', offset=10000-age)])
            self.assertFalse(self.result()['running'])
            self.assertEqual(self.result()['activityState'], 'unknown')

    def test_exited_and_reused_process_reject_active_registry(self):
        self.transcript([self.event('api-request')])
        self.native()
        self.assertFalse(self.result()['running'])
        self.assertEqual(self.result()['processState'], 'dead')
        self.process(start='9999')
        self.assertFalse(self.result()['running'])
        self.assertEqual(self.result()['activityEvidence'], 'process_exited')
        self.process(state='Z')
        self.assertFalse(self.result()['running'])

    def test_hidden_pid_namespace_is_unknown_not_exited(self):
        self.transcript([self.event('api-request')])
        self.native(pidDomain='linux:fixture:pid:[456]')
        self.assertFalse(self.result()['running'])
        self.assertEqual(self.result()['processState'], 'unknown')
        self.assertEqual(self.result()['activityState'], 'unknown')

    def test_partial_tail_and_older_copy_do_not_resurrect_finished_turn(self):
        self.transcript([self.event('assistant', 1000, message={'stop_reason': 'end_turn'})],
                        tail='{"type":"user"')
        self.transcript([self.event('api-request')], filename='z-copy.jsonl')
        self.native(status=None)
        self.process()
        self.assertFalse(self.result()['running'])
        self.assertEqual(self.result()['activityState'], 'completed')

    def test_title_is_local_custom_title_not_prompt_text_and_sidechains_cannot_close_parent(self):
        self.transcript([
            self.event('user', message={'content': 'private prompt'}),
            dict(type='custom-title', sessionId='session', customTitle='  Fixture\n title  '),
            self.event('assistant', 100, isSidechain=True, message={'stop_reason': 'end_turn'}),
        ])
        self.native(status=None)
        self.process()
        self.assertTrue(self.result()['running'])
        self.assertEqual(self.result()['title'], 'Fixture title')
        self.assertNotIn('private prompt', json.dumps(self.result()))

    def test_registry_only_session_and_malformed_registry_are_safe(self):
        self.native(name='Native title')
        self.process()
        (self.config / 'sessions/bad.json').write_text('{')
        self.assertTrue(self.result()['running'])
        self.assertEqual(self.result()['title'], 'Native title')

    def test_future_registry_and_queue_only_do_not_claim_running(self):
        self.transcript([self.event('queue-operation', operation='enqueue')])
        self.native(updatedAt=NOW + 120000)
        self.process()
        self.assertFalse(self.result()['running'])

    def test_malformed_numeric_timestamps_do_not_crash(self):
        self.transcript([dict(type='user', sessionId='session', timestamp=float('inf'))])
        self.native(updatedAt=float('nan'))
        self.assertFalse(self.result()['running'])

    def test_token_limit_closes_request_without_native_working_status(self):
        self.transcript([self.event('api-request'),
            self.event('assistant', 100, message={'stop_reason': 'max_tokens'})])
        self.native(status=None)
        self.process()
        self.assertFalse(self.result()['running'])
        self.assertEqual(self.result()['activityEvidence'], 'assistant_max_tokens')

    def test_newer_completion_or_interruption_overrides_stale_working_status(self):
        self.native(status='working', statusUpdatedAt=NOW - 5000, updatedAt=NOW - 1000)
        self.process()
        terminal_events = [
            self.event('assistant', 6000, message={'stop_reason': 'end_turn'}),
            self.event('system', 6000, subtype='stop_hook_summary', preventedContinuation=False),
            self.event('user', 6000, message={'content': '[Request interrupted by user]'}),
        ]
        for event in terminal_events:
            with self.subTest(event=event['type']):
                self.transcript([self.event('api-request'), event])
                self.assertFalse(self.result()['running'])
                self.assertIn(self.result()['activityState'], ('completed', 'interrupted'))

    def test_newer_user_or_request_overrides_stale_idle_status_with_live_process(self):
        self.native(status='idle', statusUpdatedAt=NOW - 5000, updatedAt=NOW - 1000)
        self.process()
        for kind in ('user', 'api-request'):
            with self.subTest(kind=kind):
                self.transcript([self.event(kind, 6000, message={'content': 'fixture'})])
                self.assertTrue(self.result()['running'])
                self.assertEqual(self.result()['activityEvidence'], 'live_process_unfinished_turn')

    def test_old_boot_registry_cannot_match_reused_pid_and_start_tick(self):
        self.transcript([self.event('api-request')])
        self.native(startedAt=NOW - 200000)
        self.process()
        (self.proc / 'stat').write_text('cpu 0 0 0\nbtime ' + str((NOW - 100000) // 1000) + '\n')
        self.assertFalse(self.result()['running'])
        self.assertEqual(self.result()['processState'], 'dead')

    def test_registry_from_another_machine_is_not_running(self):
        self.transcript([self.event('api-request')])
        self.native(pidDomain='linux:' + '0' * 32 + ':pid:[123]')
        self.process()
        self.assertFalse(self.result()['running'])
        self.assertEqual(self.result()['processState'], 'unknown')


if __name__ == '__main__':
    unittest.main(verbosity=2)
