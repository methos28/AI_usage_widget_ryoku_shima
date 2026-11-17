import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
import runpy
from unittest.mock import patch
from datetime import datetime, timezone

COLLECTOR = Path(__file__).resolve().parents[1]/'ai-usage/bin/claude-usage'


class ClaudePreviewTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.projects = self.home/'claude/projects/project'
        self.projects.mkdir(parents=True)
        self.cache = self.home/'usage.json'
        self.event = dict(type='assistant', sessionId='session', requestId='request', effort='medium',
            timestamp=datetime.now(timezone.utc).isoformat(), cwd='/fixture', message=dict(
                id='response', role='assistant', model='claude-sonnet-5-5', usage=dict(
                    input_tokens=100, output_tokens=300, cache_read_input_tokens=1000,
                    cache_creation_input_tokens=200, output_tokens_details=dict(thinking_tokens=50),
                    cache_creation=dict(ephemeral_5m_input_tokens=0, ephemeral_1h_input_tokens=200),
                    service_tier='standard', inference_geo='global', speed='standard')))

    def run_collector(self):
        env = dict(os.environ, AI_USAGE_DISABLE_PRICE_DOWNLOADS='1', HOME=str(self.home), CLAUDE_CONFIG_DIR=str(self.home/'claude'),
                   XDG_CONFIG_HOME=str(self.home/'config'), XDG_STATE_HOME=str(self.home/'state'),
                   CLAUDE_USAGE_STATE_DIR=str(self.home/'state/ai-usage'))
        subprocess.run(['python3', str(COLLECTOR), '--cache', str(self.cache)], env=env,
                       check=True, capture_output=True, text=True, timeout=10)
        return json.loads(self.cache.read_text())

    def test_pricing_state_failure_does_not_stop_token_collection(self):
        state=self.home/'state/ai-usage'
        state.parent.mkdir(parents=True)
        state.write_text('do not overwrite')
        (self.projects/'session.jsonl').write_text(json.dumps(self.event)+'\n')
        result=self.run_collector()
        self.assertEqual(result['_today_tokens'],1600)
        self.assertIsNone(result['_spending']['amount'])
        self.assertTrue(result['_spending']['partial'])
        self.assertEqual(state.read_text(),'do not overwrite')

    def test_late_model_metadata_replaces_an_initial_unknown_model(self):
        initial=json.loads(json.dumps(self.event))
        initial['message'].pop('model')
        initial['message']['usage'].update(input_tokens=0,output_tokens=0,cache_read_input_tokens=0,cache_creation_input_tokens=0)
        (self.projects/'session.jsonl').write_text(json.dumps(initial)+'\n'+json.dumps(self.event)+'\n')
        result=self.run_collector()
        self.assertEqual(result['_model'],'claude-sonnet-5-5')
        self.assertEqual(result['_today_tokens'],1600)
        self.assertFalse(result['_spending']['partial'])

    def test_empty_synthetic_error_usage_does_not_add_a_model(self):
        error=json.loads(json.dumps(self.event))
        error.update(requestId='error-request',isApiErrorMessage=True)
        error['message'].update(id='error-response',model='<synthetic>')
        error['message']['usage'].update(input_tokens=0,output_tokens=0,cache_read_input_tokens=0,cache_creation_input_tokens=0)
        (self.projects/'session.jsonl').write_text(json.dumps(self.event)+'\n'+json.dumps(error)+'\n')
        result=self.run_collector()
        self.assertEqual(result['_diagnostics']['models'],['claude-sonnet-5-5'])
        self.assertEqual(result['_model'],'claude-sonnet-5-5')
        self.assertEqual(result['_today_tokens'],1600)

    def test_repeated_blocks_and_copied_transcript_are_not_added(self):
        raw=json.dumps(self.event)+'\n'
        (self.projects/'session.jsonl').write_text(raw*3)
        (self.projects/'copy.jsonl').write_text(raw)
        result=self.run_collector()
        self.assertEqual(result['_diagnostics']['requests'],1)
        self.assertEqual(result['_periods']['all']['models'][0]['totalWithCacheRead'],1600)
        self.assertEqual(result['_periods']['all']['models'][0]['reasoningLabel'],'50')
        self.assertEqual(result['_periods']['all']['models'][0]['outputLabel'],'250')
        self.assertEqual(result['_diagnostics']['efforts'],['medium'])
        self.assertEqual(self.run_collector()['_today_tokens'],1600)
        self.assertEqual(self.cache.stat().st_mode & 0o777,0o600)

    def test_usage_and_lifecycle_share_one_transcript_read(self):
        transcript = self.projects / 'session.jsonl'
        first = dict(type='user', sessionId='session', timestamp=self.event['timestamp'],
                     cwd='/fixture', message={'content':'fixture'})
        last = dict(type='system', subtype='turn_end', sessionId='session',
                    timestamp=self.event['timestamp'])
        transcript.write_text('\n'.join(json.dumps(row) for row in (first,self.event,last))+'\n')
        opens = []
        original = Path.open
        def tracked(path, *args, **kwargs):
            if path == transcript:
                opens.append(path)
            return original(path, *args, **kwargs)
        env = dict(HOME=str(self.home), AI_USAGE_DISABLE_PRICE_DOWNLOADS='1',
                   XDG_CONFIG_HOME=str(self.home/'config'), XDG_STATE_HOME=str(self.home/'state'),
                   CLAUDE_USAGE_STATE_DIR=str(self.home/'state/ai-usage'))
        with patch.dict(os.environ,env), patch.object(Path,'open',tracked):
            runpy.run_path(str(COLLECTOR))['collect'](self.home/'claude',self.cache)
        result=json.loads(self.cache.read_text())
        self.assertEqual(len(opens),1)
        self.assertEqual(result['_today_tokens'],1600)
        self.assertEqual(result['_sessions'][0]['activityState'],'completed')

    def test_streaming_max_and_bad_tail(self):
        event=json.loads(json.dumps(self.event))
        event['message']['usage']['output_tokens']=400
        (self.projects/'session.jsonl').write_text(json.dumps(self.event)+'\n'+json.dumps(event)+'\n{')
        result=self.run_collector()
        self.assertEqual(result['_today_tokens'],1700)
        self.assertEqual(result['_diagnostics']['malformed_lines'],1)

    def test_empty_preview_has_no_fabricated_quota_or_activity(self):
        result=self.run_collector()
        self.assertEqual(result['_today_tokens'],0)
        self.assertEqual(result['_windows'],[])
        self.assertEqual(result['_sessions'],[])
        self.assertEqual(result['status'],'unknown')

    def test_account_limits_and_api_value_publish_together_without_changing_tokens(self):
        desktop = self.home/'config/Claude'
        desktop.mkdir(parents=True)
        (desktop/'config.json').write_text(json.dumps({'lastKnownAccountUuid':'account'}))
        (self.home/'claude/.claude.json').write_text(json.dumps({'oauthAccount':{
            'accountUuid':'account','organizationUuid':'org','organizationType':'claude_pro'}}))
        (desktop/'plan-usage-history.json').write_text(json.dumps({'version':2,'samples':[{
            't':int(time.time()*1000)-1000,'org':'org','u':{'fh':18,'sd':50}}]}))
        (self.projects/'session.jsonl').write_text(json.dumps(self.event)+'\n')
        result=self.run_collector()
        self.assertEqual(result['_today_tokens'],1600)
        self.assertEqual(result['5h-utilization'],'0.1800')
        self.assertEqual(result['7d-utilization'],'0.5000')
        self.assertEqual(result['_spending']['amount'],.0041)
        self.assertFalse(result['_spending']['partial'])
        self.assertAlmostEqual(result['_days'][0]['cost'],.0041)
        self.assertEqual(self.run_collector()['_spending']['amount'],.0041)

    def test_session_before_usage_then_native_idle_stops_running(self):
        registry=self.home/'claude/sessions'
        registry.mkdir()
        pid=os.getpid()
        start=Path('/proc')/str(pid)/'stat'
        metadata={'sessionId':'live','pid':pid,'procStart':start.read_text().rsplit(')',1)[1].split()[19],
            'status':'working','startedAt':int(time.time()*1000)-1000,'updatedAt':int(time.time()*1000)}
        path=registry/f'{pid}.json'
        path.write_text(json.dumps(metadata))
        result=self.run_collector()
        self.assertEqual(result['_sessions'][0]['id'],'live')
        self.assertTrue(result['_sessions'][0]['running'])
        self.assertEqual(result['_sessions'][0]['tokens'],0)
        metadata['status']='idle'
        path.write_text(json.dumps(metadata))
        self.assertFalse(self.run_collector()['_sessions'][0]['running'])

    def test_unknown_cache_ttl_is_unpriced_and_null_stop_placeholder_is_excluded(self):
        self.event['message']['usage'].pop('cache_creation')
        (self.projects/'session.jsonl').write_text(json.dumps(self.event)+'\n')
        result=self.run_collector()
        self.assertIsNone(result['_spending']['amount'])
        self.assertEqual(result['_spending']['unpriced_tokens'],1600)
        self.event['message']['stop_reason']=None
        self.event['message']['usage'].update(output_tokens=0,cache_read_input_tokens=0,
                                             cache_creation_input_tokens=0)
        (self.projects/'session.jsonl').write_text(json.dumps(self.event)+'\n')
        result=self.run_collector()
        self.assertEqual(result['_today_tokens'],0)
        self.assertEqual(result['_diagnostics']['incomplete_requests'],1)
        self.assertTrue(result['_spending']['partial'])

    def test_request_alias_and_fallback_sessions_keep_distinct_responses(self):
        self.event['request_id']=self.event.pop('requestId')
        copy=json.loads(json.dumps(self.event))
        copy.pop('request_id')
        second=json.loads(json.dumps(copy))
        second['sessionId']='another-session'
        (self.projects/'session.jsonl').write_text('\n'.join(map(json.dumps,[self.event,self.event,copy,second]))+'\n')
        self.assertEqual(self.run_collector()['_diagnostics']['requests'],3)

    def test_observed_model_switch_keeps_writes_thinking_and_snapshot_boundaries(self):
        # Sanitized usage counters from the reported run. No prompts, native
        # identities or account information are needed to reproduce the totals.
        # Each tuple is input, inclusive output, cache read, cache write, thinking.
        sonnet = [
            (2,556,0,57911,131), (2,302,57911,7209,101),
            (2,442,65120,2146,292), (2,2312,67266,5111,658),
            (2,591,0,57898,259), (2,290,57898,2092,0),
            (2,328,59990,2247,89), (2,277,62237,643,0),
            (2,307,62880,1056,0), (2,223,63936,1754,42),
            (2,486,65690,328,91), (4,411,66018,501,0),
            (2,519,66519,973,0), (2,272,67492,1153,42),
            (2,206,68645,495,0),
        ]
        haiku = [
            (2,579,0,69291,183), (2,368,69291,887,0),
            (2,443,70178,617,0), (2,471,70795,831,299),
            (2,270,71626,918,0), (2,672,72544,705,138),
            (2,786,73249,856,334), (2,1709,74105,919,1273),
            (2,1533,75024,1753,1130), (2,836,76777,1577,520),
        ]
        events=[]
        for index,counts in enumerate(sonnet+haiku):
            event=json.loads(json.dumps(self.event))
            inp,output,read,write,thinking=counts
            event.update(requestId=f'request-{index}',
                         sessionId='older-session' if index<4 else 'session',
                         effort='high' if index<4 or index>=15 else 'medium')
            event['message'].update(id=f'response-{index}',
                model='claude-sonnet-5-5' if index<15 else 'claude-haiku-5-5')
            event['message']['usage'].update(input_tokens=inp,output_tokens=output,
                cache_read_input_tokens=read,cache_creation_input_tokens=write,
                cache_creation={'ephemeral_5m_input_tokens':0,'ephemeral_1h_input_tokens':write},
                output_tokens_details={'thinking_tokens':thinking})
            events.append(event)
        for haiku_count,expected in ((5,356575),(6,430498),(10,739630)):
            # Native content blocks repeat the same counters. Count each
            # response once while preserving later model switches in this SID.
            rows=[json.dumps(event) for event in events[:15+haiku_count] for _ in range(2)]
            (self.projects/'session.jsonl').write_text('\n'.join(rows)+'\n')
            result=self.run_collector()
            models={r['name']:r for r in result['_periods']['all']['models']}
            self.assertEqual(models['claude-sonnet-5-5']['totalWithCacheRead'],980673)
            self.assertEqual(models['claude-sonnet-5-5']['outputLabel'],'5.8K')
            self.assertEqual(models['claude-sonnet-5-5']['reasoningLabel'],'1.7K')
            self.assertEqual(models['claude-sonnet-5-5']['sessions'],2)
            self.assertEqual(models['claude-haiku-5-5']['sessions'],1)
            self.assertEqual(models['claude-haiku-5-5']['totalWithCacheRead'],expected)
            self.assertEqual(models['claude-haiku-5-5']['total'],
                             sum(r[0]+r[1]+r[3] for r in haiku[:haiku_count]))
            self.assertEqual(result['_today_tokens'],980673+expected)
            self.assertEqual(result['_diagnostics']['requests'],15+haiku_count)
        self.assertEqual(430498-356575,sum(haiku[5][:4]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
