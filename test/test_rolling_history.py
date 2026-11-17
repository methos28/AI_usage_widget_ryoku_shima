"""Check exact rolling boundaries and agreement between period totals and bars."""
from datetime import datetime, timezone
from pathlib import Path
import os
import runpy
import time
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('AI_USAGE_TEST_WIDGET', Path(__file__).resolve().parents[1]/'ai-usage'))
ROLLING = runpy.run_path(str(ROOT/'bin/rolling-history.py'))['rolling_period']
CODEX = runpy.run_path(str(ROOT/'bin/codex-usage'))
OPENCODE = runpy.run_path(str(ROOT/'bin/opencode-usage'))


class RollingHistoryTest(unittest.TestCase):
    def test_exact_boundaries_match_models_costs_and_twenty_four_bins(self):
        for minute in (1,59):
            end=int(datetime(2026,11,10,10,minute,tzinfo=timezone.utc).timestamp()*1000)
            start=end-86400000
            for summarize in (CODEX['history_period'],OPENCODE['period_stats']):
                with self.subTest(minute=minute,summarize=summarize.__name__):
                    rows=[]
                    for stamp,count in [(start-1,9999),(start,1),(start+3599999,2),
                                        (start+3600000,3),(end,4),(end+1,9999)]:
                        rows.append(dict(time=stamp,session_id='session',model_id='fixture',provider_id='',
                                         input=count,output=0,reasoning=0,cache_write=0,cache_read=count*2,
                                         total=count,total_with_cache_read=count*3,cost=count/1000))
                    result=ROLLING(rows,end,summarize)
                    self.assertEqual(result['start'],start)
                    self.assertEqual(result['end'],end)
                    self.assertEqual(result['tokens'],10)
                    self.assertEqual(result['cost'],.01)
                    self.assertEqual(sum(row['totalWithCacheRead'] for row in result['models']),30)
                    self.assertEqual(len(result['hours']),24)
                    self.assertEqual(sum(row['tokens'] for row in result['hours']),10)
                    self.assertEqual(sum(row['cacheRead'] for row in result['hours']),20)
                    self.assertEqual(result['hours'][0]['tokens'],3)
                    self.assertEqual(result['hours'][1]['tokens'],3)
                    self.assertEqual(result['hours'][-1]['end'],end)

    def test_cutoff_is_a_duration_across_timezones_and_dst(self):
        for zone in ('UTC','Asia/Kolkata','America/New_York'):
            try:
                with patch.dict(os.environ,TZ=zone):
                    time.tzset()
                    for stamp in (1793509260,1793516340,1794308340):
                        self.assertEqual(CODEX['period_starts'](stamp)['24h'],stamp*1000-86400000)
            finally:
                time.tzset()

    def test_source_stream_is_consumed_once(self):
        class Once:
            def __init__(self):
                self.used=False
            def __iter__(self):
                if self.used:
                    raise AssertionError('second history traversal')
                self.used=True
                return iter(())
        result=ROLLING(Once(),100000000,lambda rows,start:{'tokens':sum(row['total'] for row in rows)})
        self.assertEqual(result['tokens'],0)
        self.assertEqual(len(result['hours']),24)


if __name__=='__main__':
    unittest.main(verbosity=2)
