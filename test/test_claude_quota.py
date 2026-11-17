import importlib.util
import json
import hashlib
import struct
import zlib
from datetime import datetime, timezone
from email.utils import formatdate
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error


SOURCE = Path(__file__).resolve().parents[1] / "ai-usage/bin/claude-quota.py"
SPEC = importlib.util.spec_from_file_location("claude_quota", SOURCE)
quota = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(quota)


class ClaudeQuotaTests(unittest.TestCase):
    def test_huge_numeric_values_are_not_accepted_as_measurements(self):
        self.assertFalse(quota._number(10**1000))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / "profile"
        self.desktop = self.root / "Desktop"
        self.config.mkdir()
        self.desktop.mkdir()
        self.now = 1794219000
        self.write(self.config / ".claude.json", {"oauthAccount": {
            "accountUuid": "account-a", "organizationUuid": "org-a", "organizationType": "claude_pro"}})
        self.write(self.desktop / "config.json", {"lastKnownAccountUuid": "account-a"})

    def write(self, path, data):
        path.write_text(json.dumps(data))

    def history(self, usage=None, age=300, org="org-a", extra=None):
        rows = [{"t": (self.now - age) * 1000, "org": org,
                 "u": {"fh": 18, "sd": 50} if usage is None else usage}]
        rows.extend(extra or [])
        self.write(self.desktop / "plan-usage-history.json", {"version": 2, "samples": rows})

    def collect(self, **kwargs):
        return quota.collect_quota(self.config, desktop=self.desktop, now=self.now,
                                   allow_network=False, **kwargs)

    def credentials(self, **kwargs):
        self.write(self.config / ".credentials.json", {"claudeAiOauth": {
            "accessToken": "test-secret", "expiresAt": (self.now + 3600) * 1000,
            "scopes": ["user:profile"], "subscriptionType": "pro", **kwargs}})

    def cache_response(self, *, age=300, encoding="identity", status="200 OK", org="org-a",
                       query="", usage=None, date=None):
        key=("1/0/https://claude.ai/api/organizations/"+org+"/usage"+query).encode()
        observed=self.now-age
        iso=lambda stamp:datetime.fromtimestamp(stamp,timezone.utc).isoformat()
        usage=usage if usage is not None else {
            "five_hour":{"utilization":18,"resets_at":iso(observed+7200)},
            "seven_day":{"utilization":50,"resets_at":iso(observed+86400)}}
        body=json.dumps(usage).encode()
        if encoding=="gzip":
            compressor=zlib.compressobj(wbits=31)
            body=compressor.compress(body)+compressor.flush()
        elif encoding=="deflate":
            body=zlib.compress(body)
        elif encoding=="zstd":
            from compression import zstd
            body=zstd.compress(body)
        headers=("HTTP/1.1 "+status+"\0date: "+(date or formatdate(observed,usegmt=True))
            +"\0content-encoding: "+encoding+"\0set-cookie: secret-canary\0\0").encode()
        footer=lambda flags,crc,size:struct.pack("<QIIII",0xf4fa6f45970d41d8,flags,crc,size,0)
        raw=struct.pack("<QIIII",0xfcfb6d1ba7725c30,5,len(key),0,0)+key+body
        raw+=footer(1,zlib.crc32(body),0)+headers+hashlib.sha256(key).digest()
        raw+=footer(3,zlib.crc32(headers),len(headers))
        path=self.desktop/'Cache/Cache_Data'/(hashlib.sha1(key).digest()[:8][::-1].hex()+'_0')
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(raw)
        return path,key

    def test_account_limits_are_nonzero_percentages_not_local_tokens(self):
        self.history()
        result = self.collect()
        self.assertEqual([r["utilization"] for r in result["_windows"]], [0.18, 0.5])
        self.assertEqual([r["reset"] for r in result["_windows"]], [0, 0])
        self.assertEqual(result["_plan"], "pro")
        self.assertEqual(result["5h-reset"], "")
        self.assertEqual(result["_quota"]["age_seconds"], 300)
        self.assertNotIn("org-a", json.dumps(result))
        self.assertNotIn("account-a", json.dumps(result))

    def test_stale_capture_does_not_supply_current_limits(self):
        self.history(age=quota.FRESH_SECONDS + 1)
        result = self.collect()
        self.assertTrue(result["_quota"]["stale"])
        self.assertEqual(result["_windows"], [])
        self.assertEqual(result["5h-utilization"], "")
        self.assertEqual(result["_quota"]["last_known_windows"][1]["utilization"], 0.5)

    def test_switching_desktop_account_rejects_previous_usage(self):
        self.history()
        self.write(self.desktop / "config.json", {"lastKnownAccountUuid": "account-b"})
        result = self.collect()
        self.assertFalse(result["_quota"]["available"])
        self.assertEqual(result["_windows"], [])

    def test_history_must_match_selected_organization(self):
        self.history(org="org-b")
        self.assertFalse(self.collect()["_quota"]["available"])
        self.history(extra=[{"t": (self.now - 1) * 1000, "org": "org-b", "u": {"fh": 99}}])
        self.assertEqual(self.collect()["5h-utilization"], "0.1800")

    def test_choose_latest_matching_sample_not_file_order(self):
        self.history(extra=[{"t": (self.now - 900) * 1000, "org": "org-a", "u": {"fh": 9}}])
        self.assertEqual(self.collect()["5h-utilization"], "0.1800")

    def test_unscoped_old_history_and_future_samples_are_rejected(self):
        self.history(age=-1)
        self.assertFalse(self.collect()["_quota"]["available"])
        self.write(self.desktop / "plan-usage-history.json", {
            "version": 1, "samples": [{"t": self.now * 1000, "fh": 18, "sd": 50}]})
        self.assertFalse(self.collect()["_quota"]["available"])

    def test_only_explicit_numeric_zero_becomes_zero(self):
        self.history(usage={"fh": 0, "sd": None})
        result = self.collect()
        self.assertEqual(result["5h-utilization"], "0.0000")
        self.assertEqual(result["7d-utilization"], "")
        self.history(usage={"fh": True, "sd": "50"})
        self.assertEqual(self.collect()["_windows"], [])
        self.history(usage={"fh": -1, "sd": 101})
        self.assertEqual(self.collect()["_windows"], [])

    def test_missing_and_corrupt_history_stay_unavailable(self):
        self.assertFalse(self.collect()["_quota"]["available"])
        (self.desktop / "plan-usage-history.json").write_text('{"version":2')
        self.assertFalse(self.collect()["_quota"]["available"])

    def test_fresh_desktop_sample_never_reads_oauth(self):
        self.history()
        with patch.object(quota, "oauth_quota", side_effect=AssertionError("unexpected OAuth")):
            result = quota.collect_quota(self.config, desktop=self.desktop, now=self.now)
        self.assertEqual(result["_quota"]["source"], "desktop-history")

    def test_oauth_fallback_reads_real_windows_and_bounded_reset(self):
        self.credentials()
        response = {"five_hour": {"utilization": 21, "resets_at": "2026-11-09T12:00:00Z"},
                    "seven_day": {"utilization": 51, "resets_at": "bad"}}
        with patch.object(quota, "_fetch_oauth", return_value=response) as fetch:
            result = quota.collect_quota(self.config, desktop=self.desktop, now=self.now)
        fetch.assert_called_once_with("test-secret")
        self.assertEqual(result["5h-utilization"], "0.2100")
        self.assertGreater(result["_windows"][0]["reset"], self.now)
        self.assertEqual(result["_windows"][1]["reset"], 0)
        self.assertNotIn("test-secret", json.dumps(result))

    def test_cli_subscription_login_without_desktop_supplies_both_resets(self):
        (self.desktop/'config.json').unlink()
        self.credentials()
        iso=lambda stamp:datetime.fromtimestamp(stamp,timezone.utc).isoformat()
        response={'five_hour':{'utilization':18,'resets_at':iso(self.now+7200)},
                  'seven_day':{'utilization':50,'resets_at':iso(self.now+86400)}}
        with patch.object(quota,'_fetch_oauth',return_value=response):
            result=quota.collect_quota(self.config,desktop=self.desktop,now=self.now)
        self.assertEqual(result['_quota']['source'],'oauth')
        self.assertEqual([w['reset']for w in result['_windows']],
                         [self.now+7200,self.now+86400])
        self.assertEqual([w['utilization']for w in result['_windows']],[.18,.5])

    def test_expired_or_inference_only_credentials_never_request(self):
        for fields in ({"expiresAt": self.now * 1000}, {"scopes": ["user:inference"]}):
            self.credentials(**fields)
            with patch.object(quota, "_fetch_oauth", side_effect=AssertionError("unexpected network")):
                result = quota.collect_quota(self.config, desktop=self.desktop, now=self.now)
            self.assertEqual(result["_windows"], [])

    def test_oauth_errors_are_redacted_and_keep_last_known_sample(self):
        self.history(age=2000)
        self.credentials()
        error = urllib.error.HTTPError(quota.OAUTH_URL, 403, "secret-response", {}, None)
        with patch.object(quota, "_fetch_oauth", side_effect=error):
            result = quota.collect_quota(self.config, desktop=self.desktop, now=self.now)
        self.assertTrue(result["_quota"]["stale"])
        self.assertNotIn("secret-response", json.dumps(result))

    def test_redirects_are_rejected(self):
        handler = quota._NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "redirect", {}, "https://other.test"))

    def test_oauth_success_and_failure_are_throttled_for_five_minutes(self):
        self.credentials()
        response = {"five_hour": {"utilization": 21}}
        with patch.object(quota, "_fetch_oauth", return_value=response) as fetch:
            first = quota.collect_quota(self.config, desktop=self.desktop, now=self.now)
            reused = quota.collect_quota(self.config, desktop=self.desktop, now=self.now + 5, previous=first)
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(reused["_quota"]["observed_at"], self.now)
        with patch.object(quota, "_fetch_oauth", side_effect=OSError("secret-error")) as fetch:
            failed = quota.collect_quota(self.config, desktop=self.desktop, now=self.now + 300, previous=reused)
            retried = quota.collect_quota(self.config, desktop=self.desktop, now=self.now + 305, previous=failed)
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(retried["_windows"], [])
        self.assertTrue(retried["_quota"]["stale"])
        self.assertEqual(retried["_quota"]["last_known_windows"][0]["utilization"], 0.21)
        self.assertNotIn("secret-error", json.dumps(failed))

    def test_credential_switch_does_not_reuse_previous_account_limits(self):
        self.credentials()
        with patch.object(quota, "_fetch_oauth", return_value={"five_hour": {"utilization": 21}}):
            first = quota.collect_quota(self.config, desktop=self.desktop, now=self.now)
        self.credentials(accessToken="other-account-secret")
        with patch.object(quota, "_fetch_oauth", side_effect=OSError("offline")) as fetch:
            switched = quota.collect_quota(self.config, desktop=self.desktop, now=self.now + 5, previous=first)
        fetch.assert_called_once_with("other-account-secret")
        self.assertFalse(switched["_quota"]["available"])
        self.assertNotIn("last_known_windows", switched["_quota"])

    def test_missing_credentials_preserve_cooldown_in_both_previous_shapes(self):
        for desktop_available in (False, True):
            with self.subTest(desktop_available=desktop_available):
                if desktop_available:
                    self.history(age=2000)
                else:
                    (self.desktop/'plan-usage-history.json').unlink(missing_ok=True)
                self.credentials()
                with patch.object(quota,'_fetch_oauth',side_effect=OSError('offline')) as fetch:
                    first=quota.collect_quota(self.config,desktop=self.desktop,now=self.now)
                    (self.config/'.credentials.json').unlink()
                    missing=quota.collect_quota(self.config,desktop=self.desktop,now=self.now+15,previous=first)
                    self.credentials()
                    restored=quota.collect_quota(self.config,desktop=self.desktop,now=self.now+30,previous=missing)
                    self.assertEqual(fetch.call_count,1)
                    self.assertEqual(quota._oauth_probe(restored)['_quota']['checked_at'],self.now)
                    self.credentials(accessToken='different-account-token')
                    switched=quota.collect_quota(self.config,desktop=self.desktop,now=self.now+45,previous=restored)
                    self.assertEqual(fetch.call_count,2)
                    self.assertNotEqual(quota._oauth_probe(switched)['_quota']['credential_fingerprint'],
                                        quota._oauth_probe(restored)['_quota']['credential_fingerprint'])

    def test_stale_desktop_selection_still_preserves_oauth_probe_cooldown(self):
        self.history(age=2000)
        self.credentials()
        with patch.object(quota, "_fetch_oauth", side_effect=OSError("offline")) as fetch:
            first = quota.collect_quota(self.config, desktop=self.desktop, now=self.now)
            second = quota.collect_quota(self.config, desktop=self.desktop, now=self.now + 5, previous=first)
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(second["_quota"]["source"], "desktop-history")
        self.assertTrue(second["_quota"]["stale"])

    def test_desktop_compressed_usage_supplies_real_reset_times(self):
        self.history()
        encodings=['identity','gzip','deflate']
        try:
            from compression import zstd
        except ImportError:
            pass  # Older Python safely falls back to history for zstd entries.
        else:
            encodings.append('zstd')
        for encoding in encodings:
            with self.subTest(encoding=encoding):
                self.cache_response(encoding=encoding)
                result=self.collect()
                self.assertEqual(result['_quota']['source'],'desktop-cache')
                self.assertEqual(result['_windows'][0]['reset'],self.now-300+7200)
                self.assertEqual(result['_windows'][1]['reset'],self.now-300+86400)
                self.assertEqual(result['5h-utilization'],'0.1800')
                self.assertEqual(result['_quota']['observed_at'],self.now-300)
                self.assertNotIn('secret-canary',json.dumps(result))

    def test_old_cache_never_replaces_newer_history_and_newest_query_wins(self):
        self.history(age=100)
        self.cache_response(age=500)
        self.assertEqual(self.collect()['_quota']['source'],'desktop-history')
        self.cache_response(age=10,query='?skip_spend=1')
        result=self.collect()
        self.assertEqual(result['_quota']['source'],'desktop-cache')
        self.assertEqual(result['_quota']['observed_at'],self.now-10)

    def test_torn_wrong_key_corrupt_and_non_200_cache_entries_are_rejected(self):
        for case in ('torn','wrong_key','bad_body_crc','bad_header_crc','bad_version','status'):
            with self.subTest(case=case):
                path,key=self.cache_response(status='403 Forbidden' if case=='status' else '200 OK')
                raw=bytearray(path.read_bytes())
                if case=='torn':raw=raw[:-8]
                elif case=='wrong_key':raw[24]^=1
                elif case=='bad_body_crc':raw[24+len(key)]^=1
                elif case=='bad_header_crc':raw[-24-32-3]^=1
                elif case=='bad_version':raw[8]=99
                path.write_bytes(raw)
                self.assertFalse(self.collect()['_quota']['available'])

    def test_expired_captured_deadline_is_retained_as_stale_not_rolled_forward(self):
        iso=lambda stamp:datetime.fromtimestamp(stamp,timezone.utc).isoformat()
        self.cache_response(age=60,usage={
            'five_hour':{'utilization':47,'resets_at':iso(self.now-30)},
            'seven_day':{'utilization':53,'resets_at':iso(self.now+86400)}})
        result=self.collect()
        self.assertTrue(result['_quota']['stale'])
        self.assertEqual(result['_windows'],[])
        self.assertEqual(result['_quota']['last_known_windows'][0]['reset'],self.now-30)
        self.assertEqual(result['5h-utilization'],'')
        self.assertEqual(result['_quota']['age_seconds'],60)

    def test_cached_response_remains_bound_to_current_account_and_org(self):
        self.cache_response(org='other-org')
        self.assertFalse(self.collect()['_quota']['available'])
        self.cache_response()
        self.write(self.desktop/'config.json',{'lastKnownAccountUuid':'other-account'})
        self.assertFalse(self.collect()['_quota']['available'])

    def test_cache_date_and_reset_validation_never_invent_deadlines(self):
        for date in ('bad date',formatdate(self.now+100,usegmt=True)):
            self.cache_response(date=date)
            self.assertFalse(self.collect()['_quota']['available'])
        self.cache_response(usage={
            'five_hour':{'utilization':0,'resets_at':'2030-01-01T00:00:00Z'},
            'seven_day':{'utilization':53,'resets_at':'2026-11-10T10:00:00'}})
        result=self.collect()
        self.assertEqual([w['reset']for w in result['_windows']],[0,0])
        self.assertEqual(result['5h-utilization'],'0.0000')

    def test_oauth_reset_boundary_refreshes_once_and_keeps_failed_deadline(self):
        self.credentials()
        reset=datetime.fromtimestamp(self.now+30,timezone.utc).isoformat()
        with patch.object(quota,'_fetch_oauth',return_value={
                'five_hour':{'utilization':47,'resets_at':reset}}):
            first=quota.collect_quota(self.config,desktop=self.desktop,now=self.now)
        with patch.object(quota,'_fetch_oauth',side_effect=OSError('offline'))as fetch:
            second=quota.collect_quota(self.config,desktop=self.desktop,now=self.now+31,previous=first)
            third=quota.collect_quota(self.config,desktop=self.desktop,now=self.now+36,previous=second)
        self.assertEqual(fetch.call_count,1)
        self.assertTrue(third['_quota']['stale'])
        self.assertEqual(third['_quota']['last_known_windows'][0]['reset'],self.now+30)


if __name__ == "__main__":
    unittest.main()
