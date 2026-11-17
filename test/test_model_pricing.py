"""Verify public catalog refresh, offline coverage and native pricing tiers."""
from copy import deepcopy
import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
WIDGET = ROOT / 'ai-usage'
if not WIDGET.exists():
    WIDGET = ROOT / 'ryoku/shell/quickshell/inir/defaults/widgets/ai-usage'


class ModelPricingTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name)
        self.module = runpy.run_path(str(WIDGET / 'bin/model-pricing.py'))
        self.load = self.module['load_prices']
        self.globals = self.load.__globals__
        self.resolve = self.module['resolve_rate']
        self.now = self.module['read_bundle']('openai')['fetched_at'] + 60
        self.env = patch.dict(os.environ, {'AI_USAGE_DISABLE_PRICE_DOWNLOADS': '0'})
        self.env.start()
        self.addCleanup(self.env.stop)

    def bundle(self, provider):
        return self.module['read_bundle'](provider)['models']

    def test_malformed_frozen_rates_fail_closed_without_type_errors(self):
        prices={'gpt-unit':{'input':2,'output':10,'cache_read':'bad'}}
        rate=self.resolve(prices,'gpt-unit')
        self.assertNotIn('cache_read',rate)
        for bad in ('bad', [1], [None], [{'above':'bad','input':4,'output':20}]):
            prices['gpt-unit']['tiers']=bad
            self.assertIsNone(self.resolve(prices,'gpt-unit'))

    def test_context_token_thresholds_are_not_limited_by_currency_bounds(self):
        price={'input':2,'output':10,'tiers':[{'above':2000000,'input':4,'output':20}]}
        self.assertEqual(self.resolve({'gpt-unit':price},'gpt-unit',2000001)['input'],4)

    def test_highest_applicable_tier_can_follow_an_unsupported_tier(self):
        rate={'input':1,'output':2,'tiers':[{'above':100,'unsupported':True},
            {'above':200,'input':3,'output':6},{'above':300,'unsupported':True}]}
        prices={'gpt-unit':dict(rate,service_tiers={'fast':deepcopy(rate)})}
        original=deepcopy(prices)
        for service in ('standard','fast'):
            for context,expected in ((99,1),(101,None),(200,None),(201,3),(301,None)):
                with self.subTest(service=service,context=context):
                    result=self.resolve(prices,'gpt-unit',context,service)
                    self.assertEqual(result['input'] if result else None,expected)
        self.assertEqual(prices,original)

    def test_valid_json_with_invalid_bundle_shape_is_unavailable(self):
        path=self.state/'bad-bundle.json'
        self.module['read_bundle'].__globals__['BUNDLE']=path
        for raw in ('null','[]','{"models":[],"verified_at":"bad"}', '{"models":{},"verified_at":null}'):
            path.write_text(raw)
            self.assertEqual(self.module['read_bundle']('openai')['models'],{})

    def test_native_codex_current_and_legacy_models(self):
        expected = {
            'gpt-6-astra': (10, 50, 1), 'gpt-6-astra-law': (10, 50, 1), 'gpt-6.1-sol': (2, 10, .1),
            'gpt-6.1-terra': (1, 5, .05), 'gpt-6-luna': (.1, .5, .01),
            'gpt-6-sol': (2, 10, .2), 'gpt-5.6-sol': (4, 20, .4),
            'gpt-5.5': (5, 30, .5), 'gpt-5.4': (2.5, 15, .25),
            'gpt-5.3-codex': (1.75, 14, .175), 'gpt-5.3-codex-spark': (1.75, 14, .175),
            'gpt-5.2-codex': (1.75, 14, .175), 'gpt-5.1-codex': (1.25, 10, .125),
            'gpt-5.1-codex-max': (1.25, 10, .125), 'gpt-5.1-codex-mini': (.25, 2, .025),
            'gpt-5-codex': (1.25, 10, .125), 'codex-mini-latest': (1.5, 6, .375),
        }
        for name, values in expected.items():
            with self.subTest(model=name):
                rate = self.resolve(self.bundle('openai'), name)
                self.assertEqual(tuple(rate[key] for key in ('input', 'output', 'cache_read')), values)

    def test_claude_lineup_and_published_snapshot_ids(self):
        expected = {
            'claude-fable-5-1': (10, 50, .25), 'claude-mythos-5-1': (10, 50, .25),
            'claude-opus-5-5': (4, 20, .2), 'claude-sonnet-5-5': (2, 10, .1),
            'claude-haiku-5-5': (.1, .5, .01), 'claude-opus-5': (5, 25, .5),
            'claude-opus-4-8': (5, 25, .5), 'claude-opus-4-7': (5, 25, .5),
            'claude-opus-4-6': (5, 25, .5), 'claude-opus-4-5-20251101': (5, 25, .5),
            'claude-sonnet-4-6': (3, 15, .3), 'claude-sonnet-4-5-20250929': (3, 15, .3),
            'claude-haiku-4-5-20251001': (1, 5, .1), 'claude-opus-4-1-20250805': (15, 75, 1.5),
            'claude-3-7-sonnet-20250219': (3, 15, .3),
        }
        for name, values in expected.items():
            with self.subTest(model=name):
                rate = self.resolve(self.bundle('anthropic'), name)
                self.assertEqual(tuple(rate[key] for key in ('input', 'output', 'cache_read')), values)

    def test_openai_service_tiers_and_context_boundary(self):
        prices = self.bundle('openai')
        for tier, expected in [('standard', 2), ('default', 2), ('auto', 2),
                               ('fast', 4), ('priority', 4), ('flex', 1), ('batch', 1), ('ultrafast', 12)]:
            with self.subTest(tier=tier):
                self.assertEqual(self.resolve(prices, 'gpt-6.1-sol', 272000, tier)['input'], expected)
                self.assertEqual(self.resolve(prices, 'gpt-6.1-sol', 272001, tier)['input'], expected * 2)
        self.assertEqual(self.resolve(prices, 'gpt-6.1-sol', 272001, 'fast')['output'], 30)
        self.assertEqual(self.resolve(prices, 'gpt-5.3-codex', 100, 'priority')['input'], 3.5)
        self.assertIsNone(self.resolve(prices, 'gpt-5.5', 272001, 'fast'))

    def test_claude_haiku_threshold_and_opus_fast(self):
        prices = self.bundle('anthropic')
        self.assertEqual(self.resolve(prices, 'claude-haiku-5-5', 100000)['input'], .1)
        self.assertEqual(self.resolve(prices, 'claude-haiku-5-5', 100001)['input'], .5)
        self.assertEqual(self.resolve(prices, 'claude-haiku-5-5', 100001)['cache_write_1h'], 1)
        self.assertEqual(self.resolve(prices, 'claude-opus-5-5', 500000, 'fast')['input'], 8)
        self.assertEqual(self.resolve(prices, 'claude-sonnet-5-5', 500000)['input'], 2)
        self.assertIsNone(self.resolve(prices, 'claude-haiku-5-5', 100, 'fast'))

    def test_prefixes_are_supported_but_unknown_suffixes_are_not_guessed(self):
        prices = self.bundle('openai')
        self.assertEqual(self.resolve(prices, 'openai/GPT-6.1-SOL')['input'], 2)
        self.assertIsNone(self.resolve(prices, 'gpt-6.1-sol-future'))
        self.assertIsNone(self.resolve(prices, 'gpt-6.1-sol-2099-01-01'))
        self.assertIsNone(self.resolve(prices, 'bedrock/gpt-6.1-sol'))

    def test_first_run_offline_has_both_provider_catalogs(self):
        for provider, name in [('openai', 'gpt-6.1-sol'), ('anthropic', 'claude-haiku-5-5')]:
            self.globals['download'] = MagicMock(side_effect=OSError('offline'))
            result = self.load(provider, state_dir=self.state, now=self.now)
            self.assertIn(name, result['models'])
            self.assertFalse(result['stale'])
            self.assertEqual((self.state / ('prices-' + provider + '.json')).stat().st_mode & 0o777, 0o600)

    def test_public_refresh_adds_new_models_without_a_code_update(self):
        catalog = {'anthropic': {'models': {'claude-new-9': {'cost': {'input': 7, 'output': 35, 'cache_read': .7, 'cache_write': 8.75}}}}}
        self.globals['download'] = MagicMock(side_effect=lambda url:
            json.dumps(catalog) if url == self.module['CATALOG_URL'] else '# No price table')
        result = self.load('anthropic', state_dir=self.state, now=self.now)
        self.assertEqual(result['models']['claude-new-9']['cache_write_1h'], 14)
        self.assertIn('claude-haiku-5-5', result['models'])
        self.globals['download'].reset_mock()
        again = self.load('anthropic', state_dir=self.state, now=self.now + 10)
        self.assertIn('claude-new-9', again['models'])
        self.globals['download'].assert_not_called()

    def test_new_model_refreshes_a_fresh_cache_after_retry_interval(self):
        self.globals['download'] = MagicMock(side_effect=OSError('offline'))
        self.load('openai', state_dir=self.state, now=self.now)
        catalog = {'openai': {'models': {'gpt-new-release': {'cost': {'input': 2, 'output': 10}}}}}
        self.globals['download'] = MagicMock(side_effect=lambda url:
            json.dumps(catalog) if url == self.module['CATALOG_URL'] else '')
        early = self.load('openai', state_dir=self.state, now=self.now + 60,
                          required=[('gpt-new-release', 100, 'standard')])
        self.assertNotIn('gpt-new-release', early['models'])
        self.globals['download'].assert_not_called()
        refreshed = self.load('openai', state_dir=self.state, now=self.now + 901,
                              required=[('gpt-new-release', 100, 'standard')])
        self.assertEqual(refreshed['models']['gpt-new-release']['input'], 2)

    def test_official_tables_override_catalog_numbers(self):
        catalog = {'openai': {'models': {'gpt-unit': {'cost': {'input': 99, 'output': 99}}}}}
        official = 'Standard\n| Model | Input | Output | Cached input |\n| --- | --- | --- | --- |\n| gpt-unit | $2 | $10 | $0.10 |'
        self.globals['download'] = lambda url: json.dumps(catalog) if url == self.module['CATALOG_URL'] else official
        result = self.load('openai', state_dir=self.state, now=self.now)
        self.assertEqual(result['models']['gpt-unit']['input'], 2)
        self.assertIn('developers.openai.com', result['source'])

    def test_offline_refresh_retains_last_good_prices_and_throttles_failure(self):
        cache = self.state / 'prices-openai.json'
        cache.write_text(json.dumps({'models': {'gpt-retained': {'input': 3, 'output': 9}},
                                    'fetched_at': self.now - 90000, 'last_attempt': self.now - 90000}))
        self.globals['download'] = MagicMock(side_effect=OSError('offline'))
        result = self.load('openai', state_dir=self.state, now=self.now)
        self.assertEqual(result['models']['gpt-retained']['input'], 3)
        self.assertTrue(result['stale'])
        self.globals['download'].reset_mock()
        self.load('openai', state_dir=self.state, now=self.now + 10)
        self.globals['download'].assert_not_called()

    def test_invalid_rates_and_broken_cache_do_not_zero_the_catalog(self):
        self.globals['download'] = lambda url: '{broken'
        for bad in ('{broken', '[]', '{"models":{}}', '{"models":{"gpt-bad":{"input":2,"output":10}},"fetched_at":"bad"}'):
            (self.state / 'prices-openai.json').write_text(bad)
            result = self.load('openai', state_dir=self.state, now=self.now)
            self.assertIn('gpt-6.1-sol', result['models'])
        clean = self.module['clean_models']({
            'negative': {'input': -1, 'output': 10}, 'boolean': {'input': True, 'output': 10},
            'nan': {'input': float('nan'), 'output': 10}, 'huge': {'input': 10**1000, 'output': 10},
            'nested': {'input': 2, 'output': 10, 'service_tiers': []},
        })
        self.assertEqual(clean, {})

    def test_public_download_has_no_credentials_or_local_usage(self):
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value.read.return_value = b'{}'
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'secret-canary', 'ANTHROPIC_API_KEY': 'secret-canary'}), \
                patch.object(self.module['urllib'].request, 'build_opener', return_value=opener) as build:
            self.module['download'](self.module['CATALOG_URL'])
        request = opener.open.call_args.args[0]
        self.assertIsNone(request.data)
        self.assertNotIn('secret-canary', str(request.headers))
        self.assertNotIn('authorization', {key.lower() for key in request.headers})
        self.assertIsNone(build.call_args.args[1].redirect_request(None, None, 302, '', {}, 'https://elsewhere.invalid'))

    def test_frozen_rates_gain_missing_models_and_tiers_without_repricing(self):
        old = {'gpt-unit': {'input': 2, 'output': 10}}
        new = {'gpt-unit': {'input': 9, 'output': 45, 'service_tiers': {'fast': {'input': 4, 'output': 20}}},
               'gpt-second': {'input': 1, 'output': 5}}
        frozen = deepcopy(old)
        combined = self.module['merge_models'](old, new, preserve=True)
        self.assertEqual(old, frozen)
        self.assertEqual(combined['gpt-unit']['input'], 2)
        self.assertEqual(combined['gpt-unit']['service_tiers']['fast']['input'], 4)
        self.assertIn('gpt-second', combined)


if __name__ == '__main__':
    unittest.main(verbosity=2)
