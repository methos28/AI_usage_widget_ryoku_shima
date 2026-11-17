"""Claude token pricing tests use isolated private state and no network."""
from copy import deepcopy
from datetime import datetime
import json
import os
from unittest.mock import patch
from pathlib import Path
import runpy
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "ai-usage/bin/claude-spending.py"


class ClaudeSpendingTest(unittest.TestCase):
    def setUp(self):
        self.network = patch.dict(os.environ, {"AI_USAGE_DISABLE_PRICE_DOWNLOADS": "1"})
        self.network.start()
        self.addCleanup(self.network.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name) / "state"
        self.helper = runpy.run_path(str(HELPER))
        self.estimate = self.helper["estimate_spending"]
        self.globals = self.estimate.__globals__
        self.now = datetime(2026, 11, 9, 12).astimezone().timestamp()
        self.row = dict(event_id="request:response", time=int(self.now * 1000),
            model_id="claude-sonnet-5-5", provider_id="", service_tier="standard",
            inference_geo="global", speed="standard", input=100, output=250,
            reasoning=50, cache_read=1000, cache_write=200,
            cache_write_5m=50, cache_write_1h=150)

    def estimate_rows(self, rows=None, now=None):
        return self.estimate([self.row] if rows is None else rows, state_dir=self.state,
                             now=self.now if now is None else now)

    def ledger(self, month="2026-11"):
        return json.loads((self.state / f"claude-spending-{month}.json").read_text())

    def test_malformed_nested_ledger_date_is_preserved_and_unavailable(self):
        self.estimate_rows()
        path=self.state/'claude-spending-2026-11.json'
        raw=self.ledger()
        next(iter(raw['events'].values()))['date']=[]
        original=json.dumps(raw)
        path.write_text(original)
        summary,costs=self.estimate_rows()
        self.assertIsNone(summary['amount'])
        self.assertEqual(summary['state_error'],'unreadable-ledger')
        self.assertEqual(path.read_text(),original)

    def test_native_categories_split_ttl_and_thinking_once(self):
        summary, costs = self.estimate_rows()
        # 100*2 + (250+50)*10 + 1000*.1 + 50*2.5 + 150*4.
        expected = 4025 / 1_000_000
        self.assertAlmostEqual(costs[self.row["event_id"]], expected)
        self.assertEqual(summary["amount"], expected)
        self.assertEqual(summary["priced_tokens"], 1600)
        self.assertFalse(summary["partial"])
        self.assertFalse(summary["charges"])
        self.assertTrue(summary["token_only"])
        self.assertEqual(summary["kind"], "api-equivalent")
        model = self.ledger()["days"]["2026-11-09"]["models"]["claude-sonnet-5-5"]
        self.assertEqual(model["output"], 300)

    def test_duplicate_snapshot_with_missing_split_remains_unpriced(self):
        partial=dict(self.row)
        partial.pop('cache_write_1h')
        summary,costs=self.estimate_rows([self.row,partial])
        self.assertIsNone(summary['amount'])
        self.assertTrue(summary['partial'])
        self.assertIsNone(costs[self.row['event_id']])

    def test_real_observed_sonnet_totals_all_one_hour(self):
        self.row.update(input=22, output=4451, reasoning=1663, cache_read=562928,
                        cache_write=138395, cache_write_5m=0, cache_write_1h=138395)
        summary, costs = self.estimate_rows()
        self.assertEqual(summary["priced_tokens"], 707459)
        self.assertAlmostEqual(costs[self.row["event_id"]], .6710568)
        self.assertEqual(summary["amount"], .671057)

    def test_mixed_sonnet_haiku_and_fast_opus_are_all_priced(self):
        haiku = dict(self.row, event_id="haiku", model_id="claude-haiku-5-5")
        opus = dict(self.row, event_id="opus", model_id="claude-opus-5-5", speed="fast")
        summary, costs = self.estimate_rows([self.row, haiku, opus])
        self.assertAlmostEqual(costs["haiku"], .00020625)
        self.assertAlmostEqual(costs["opus"], .0161)
        self.assertEqual(summary["amount"], .020331)
        self.assertEqual(summary["unpriced_tokens"], 0)
        self.assertFalse(summary["partial"])
        self.assertEqual(len(self.ledger()["days"]["2026-11-09"]["models"]), 3)

    def test_haiku_tier_counts_cached_input_and_cache_writes(self):
        low = dict(self.row, event_id="low", model_id="claude-haiku-5-5", input=1,
                   cache_read=99999, cache_write=0, cache_write_5m=0, cache_write_1h=0,
                   output=100, reasoning=0)
        high = dict(low, event_id="high", cache_read=100000)
        writes = dict(low, event_id="writes", input=99999, cache_read=0,
                      cache_write=2, cache_write_5m=0, cache_write_1h=2)
        _, costs = self.estimate_rows([low, high, writes])
        self.assertAlmostEqual(costs["low"], .00105009)
        self.assertAlmostEqual(costs["high"], .0052505)
        self.assertAlmostEqual(costs["writes"], .0502515)

    def test_existing_sonnet_only_snapshot_gains_haiku_without_resetting_state(self):
        self.estimate_rows()
        ledger = self.ledger()
        sonnet = ledger["days"]["2026-11-09"]["prices"]["claude-sonnet-5-5"]
        ledger["days"]["2026-11-09"]["prices"] = {"claude-sonnet-5-5": sonnet}
        (self.state / 'claude-spending-2026-11.json').write_text(json.dumps(ledger))
        haiku = dict(self.row, event_id="haiku", model_id="claude-haiku-5-5")
        summary, _ = self.estimate_rows([self.row, haiku])
        self.assertEqual(summary["unpriced_tokens"], 0)
        self.assertEqual(self.ledger()["days"]["2026-11-09"]["prices"]["claude-sonnet-5-5"], sonnet)
        self.assertEqual(summary["amount"], .004231)

    def test_published_snapshot_and_unspecified_standard_tier(self):
        row = dict(self.row, model_id="anthropic/claude-haiku-4-5-20251001")
        row.pop("service_tier")
        summary, costs = self.estimate_rows([row])
        self.assertAlmostEqual(costs[row["event_id"]], .0020625)
        self.assertFalse(summary["partial"])

    def test_batch_discount_and_invalid_fast_batch_combination(self):
        row = dict(self.row, service_tier="batch")
        summary, costs = self.estimate_rows([row])
        self.assertAlmostEqual(costs[row["event_id"]], .0020125)
        self.assertFalse(summary["partial"])
        row["speed"] = "fast"
        summary, _ = self.estimate_rows([row])
        self.assertTrue(summary["partial"])

    def test_duplicates_repoll_and_removed_transcript_do_not_add_spend(self):
        earlier = dict(self.row, output=100)
        first, costs = self.estimate_rows([self.row, earlier, self.row])
        second, _ = self.estimate_rows()
        third, _ = self.estimate_rows([])
        self.assertEqual(first["amount"], second["amount"])
        self.assertEqual(first["amount"], third["amount"])
        self.assertEqual(len(self.ledger()["events"]), 1)
        self.assertEqual(list(costs), [self.row["event_id"]])
        self.assertNotIn(self.row["event_id"], self.ledger()["events"])

    def test_daily_rates_freeze_and_new_day_uses_updated_snapshot(self):
        first, _ = self.estimate_rows()
        old_prices = deepcopy(self.ledger()["days"]["2026-11-09"]["prices"])
        self.globals["VERIFIED_PRICES"]["claude-sonnet-5-5"]["input"] = 20
        repeat, _ = self.estimate_rows()
        self.assertEqual(first["amount"], repeat["amount"])
        tomorrow = self.now + 2 * 86400
        new_row = dict(self.row, event_id="new-response", time=int(tomorrow * 1000))
        total, costs = self.estimate_rows([self.row, new_row], now=tomorrow)
        self.assertGreater(costs["new-response"], first["amount"])
        self.assertEqual(self.ledger()["days"]["2026-11-09"]["prices"], old_prices)
        self.assertTrue(total["stale_prices"])

    def test_past_days_without_snapshots_never_receive_todays_rates(self):
        yesterday = dict(self.row, event_id="old-response", time=int((self.now - 86400) * 1000))
        summary, costs = self.estimate_rows([yesterday, self.row])
        self.assertIsNone(costs["old-response"])
        self.assertEqual(summary["unpriced_days"], ["2026-11-08"])
        self.assertTrue(summary["partial"])
        self.assertNotIn("prices", self.ledger()["days"]["2026-11-08"])
        self.estimate_rows([yesterday, self.row], now=self.now + 86400)
        self.assertNotIn("prices", self.ledger()["days"]["2026-11-08"])

    def test_late_events_use_saved_day_and_month_rollover_is_separate(self):
        first, _ = self.estimate_rows()
        december = datetime(2026, 12, 1, 12).astimezone().timestamp()
        late = dict(self.row, event_id="late-response")
        current = dict(self.row, event_id="december-response", time=int(december * 1000))
        summary, costs = self.estimate_rows([self.row, late, current], now=december)
        self.assertEqual(summary["month"], "2026-12")
        self.assertEqual(summary["amount"], first["amount"])
        self.assertEqual(self.ledger()["days"]["2026-11-09"]["cost"], first["amount"] * 2)
        self.assertEqual(costs["late-response"], first["amount"])
        self.assertTrue(summary["stale_prices"])

    def test_unknown_exact_model_tier_speed_provider_and_geo_are_unpriced(self):
        changes = [dict(model_id="claude-sonnet-5-5-future"), dict(service_tier="priority"),
                   dict(service_tier="unknown"), dict(speed="fast"), dict(provider_id="bedrock"),
                   dict(inference_geo="new-region")]
        rows = [dict(self.row, event_id=str(index), **change) for index, change in enumerate(changes)]
        summary, costs = self.estimate_rows(rows)
        self.assertIsNone(summary["amount"])
        self.assertTrue(summary["partial"])
        self.assertEqual(summary["unpriced_tokens"], 1600 * len(rows))
        self.assertTrue(all(value is None for value in costs.values()))

    def test_missing_or_mismatched_ttl_is_not_assumed_five_minutes(self):
        missing = dict(self.row, event_id="missing")
        missing.pop("cache_write_1h")
        mismatch = dict(self.row, event_id="mismatch", cache_write_1h=100)
        summary, costs = self.estimate_rows([missing, mismatch])
        self.assertIsNone(summary["amount"])
        self.assertEqual(costs, {"missing": None, "mismatch": None})

    def test_zero_cache_write_needs_no_ttl_metadata_and_us_multiplier(self):
        self.row.update(cache_write=0, inference_geo="us")
        self.row.pop("cache_write_5m")
        self.row.pop("cache_write_1h")
        summary, costs = self.estimate_rows()
        self.assertAlmostEqual(costs[self.row["event_id"]], .0033 * 1.1)
        self.assertFalse(summary["partial"])
        self.row.update(cache_write_5m=None, cache_write_1h=None)
        _, costs = self.estimate_rows()
        self.assertAlmostEqual(costs[self.row["event_id"]], .0033 * 1.1)

    def test_server_tools_keep_token_subtotal_but_mark_extra_fees(self):
        self.row["server_tool_use"] = {"web_search_requests": 1, "web_fetch_requests": 2}
        summary, costs = self.estimate_rows()
        self.assertIsNotNone(costs[self.row["event_id"]])
        self.assertTrue(summary["partial"])
        self.assertTrue(summary["additional_costs_unpriced"])
        self.row["server_tool_use"] = {"web_search_requests": 0, "web_fetch_requests": 2}
        summary, _ = self.estimate_rows()
        self.assertFalse(summary["additional_costs_unpriced"])

    def test_state_is_private_atomic_and_never_touches_codex_ledger(self):
        self.state.mkdir()
        codex = self.state / "spending-2026-11.json"
        codex.write_text("codex-canary")
        self.row.update(prompt="prompt-canary", directory="path-canary", api_key="key-canary")
        self.estimate_rows()
        self.assertEqual(codex.read_text(), "codex-canary")
        for name in ("claude-spending-2026-11.json", "claude-spending.lock"):
            path = self.state / name
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            for canary in ("prompt-canary", "path-canary", "key-canary"):
                self.assertNotIn(canary, path.read_text())
        self.assertEqual(sorted(path.name for path in self.state.iterdir()),
            ["claude-spending-2026-11.json", "claude-spending.lock", "spending-2026-11.json"])

    def test_unreadable_or_malformed_historical_ledger_is_not_overwritten(self):
        self.state.mkdir()
        path = self.state / "claude-spending-2026-11.json"
        for raw in ("{broken", '{"schemaVersion":99}',
                    '{"schemaVersion":1,"month":"2026-11","currency":"USD","days":{},"events":{"x":{}}}'):
            path.write_text(raw)
            summary, costs = self.estimate_rows()
            self.assertEqual(path.read_text(), raw)
            self.assertEqual(summary["state_error"], "unreadable-ledger")
            self.assertIsNone(summary["amount"])
            self.assertIsNone(costs[self.row["event_id"]])

    def test_malformed_or_future_events_are_not_silently_priced(self):
        bad = [dict(self.row, input=True), dict(self.row, input=-1),
               dict(self.row, time=float("nan")), dict(self.row, output=10**100),
               dict(self.row, time=int((self.now + 86400) * 1000))]
        summary, costs = self.estimate_rows(bad)
        self.assertEqual(summary["invalid_events"], len(bad))
        self.assertTrue(summary["partial"])
        self.assertIsNone(summary["amount"])
        self.assertEqual(costs, {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
