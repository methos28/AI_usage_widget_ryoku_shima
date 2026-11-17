"""Exercise installer failures without changing the real desktop."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='widget-install-audit-')
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.repo = self.work / 'repo with spaces'
        self.repo.mkdir()
        shutil.copy2(ROOT / 'install.sh', self.repo / 'install.sh')
        shutil.copytree(ROOT / 'ai-usage', self.repo / 'ai-usage', ignore=shutil.ignore_patterns('__pycache__'))
        self.home = self.work / 'home'
        self.target = self.home / '.config/inir/widgets/ai-usage'
        self.target.mkdir(parents=True)
        (self.target / 'keep').write_text('previous widget')
        self.tools = self.work / 'tools'
        self.tools.mkdir()
        self.stub('ryoku-shell', 'exit 0')
        self.env = dict(os.environ, HOME=str(self.home), PATH=str(self.tools) + os.pathsep + os.environ['PATH'])

    def stub(self, name, body):
        path = self.tools / name
        path.write_text('#!/bin/sh\n' + body + '\n')
        path.chmod(0o755)

    def install(self):
        return subprocess.run(['bash', str(self.repo / 'install.sh')], env=self.env,
                              capture_output=True, text=True, timeout=10)

    def test_reloader_does_not_inherit_the_install_lock(self):
        self.stub('ryoku-shell', """python3 - <<'CHECK'
import os
import sys
for entry in os.listdir('/proc/self/fd'):
    try:
        target=os.readlink('/proc/self/fd/'+entry)
    except OSError:
        continue
    if target.endswith('.ai-usage-install.lock'):
        sys.exit(8)
CHECK""")
        result=self.install()
        self.assertEqual(result.returncode,0,result.stderr)

    def test_failed_copy_keeps_the_previous_widget(self):
        self.stub('cp', 'exit 9')
        result = self.install()
        self.assertEqual(result.returncode, 9, result.stderr)
        self.assertEqual((self.target / 'keep').read_text(), 'previous widget')
        self.assertFalse(list(self.target.parent.glob('.ai-usage-stage.*')))

    def test_reload_failure_rolls_back_the_previous_widget(self):
        self.stub('ryoku-shell', 'exit 7')
        result = self.install()
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual((self.target / 'keep').read_text(), 'previous widget')
        self.assertFalse(list(self.target.parent.glob('.ai-usage-before.*')))

    def test_success_delivers_all_helpers_and_keeps_other_widgets(self):
        other = self.target.parent / 'other-widget'
        other.mkdir()
        (other / 'keep').write_text('other widget')
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ('collect-usage', 'codex-usage', 'claude-usage', 'model-pricing.py', 'model-prices.json'):
            self.assertEqual((self.target / 'bin' / name).read_bytes(), (ROOT / 'ai-usage/bin' / name).read_bytes())
        self.assertEqual((other / 'keep').read_text(), 'other widget')
        self.assertFalse(list(self.target.parent.glob('.ai-usage-before.*')))


if __name__ == '__main__':
    unittest.main(verbosity=2)
