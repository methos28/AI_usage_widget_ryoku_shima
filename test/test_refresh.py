"""Exercise visible collection and stopping after its dashboard is destroyed."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WIDGET = Path(os.environ.get('AI_USAGE_TEST_WIDGET', ROOT / 'ai-usage'))


@unittest.skipUnless(shutil.which('qs'), 'Quickshell required')
class RefreshTest(unittest.TestCase):
    def test_relative_time_ticker_stops_hidden_and_resumes_visible(self):
        source=(WIDGET/'UsageModel.qml').read_text()
        start=source.rfind('    Timer {',0,source.index('        interval: 30000'))
        end=source.index('\n    }',start)+len('\n    }')
        timer=source[start:end].replace('interval: 30000','interval: 60')
        with tempfile.TemporaryDirectory(prefix='usage-ticker-') as directory:
            work=Path(directory);runtime=work/'runtime';runtime.mkdir(mode=0o700)
            shell=work/'shell.qml'
            shell.write_text('''import QtQuick
import QtQuick.Window
import Quickshell
ShellRoot {
    property int held: 0
    Window { width:8; height:8; visible:true
      Item { id: root; property bool has: true; property int tick: 0
'''+timer+'''
      }
    }
    Timer { interval:200;running:true;onTriggered:{root.visible=false;held=root.tick} }
    Timer { interval:500;running:true;onTriggered:{
        if(root.tick!==held){console.log('TICKER-FAIL hidden');Qt.quit();return}
        root.visible=true;
    } }
    Timer { interval:750;running:true;onTriggered:{
        console.log(root.tick>held?'TICKER-PASS':'TICKER-FAIL resume');Qt.quit();
    } }
}
''')
            result=subprocess.run(['qs','-p',str(shell)],capture_output=True,text=True,timeout=8,
                env=dict(os.environ,HOME=str(work),XDG_RUNTIME_DIR=str(runtime),QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QS_DISABLE_CRASH_HANDLER='1'))
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('TICKER-PASS',result.stdout+result.stderr)
            self.assertNotIn('TICKER-FAIL',result.stdout+result.stderr)

    def test_pulse_pauses_without_losing_phase_on_cache_or_visibility_changes(self):
        source=(WIDGET/'components/AiUsageNowCard.qml').read_text()
        start=source.index('SequentialAnimation {')
        depth=0
        for end in range(source.index('{',start),len(source)):
            depth+=(source[end]=='{')-(source[end]=='}')
            if depth==0:
                break
        animation=source[start:end+1].replace('SequentialAnimation {','SequentialAnimation { id: pulseAnimation;',1)
        with tempfile.TemporaryDirectory(prefix='usage-pulse-') as directory:
            work=Path(directory);runtime=work/'runtime';runtime.mkdir(mode=0o700)
            shell=work/'shell.qml'
            shell.write_text('''import QtQuick
import Quickshell
ShellRoot {
    property real held: 0
    Item { id: container
        Item { id: liveDot; property bool live: true; property real pulse: 1
''' + animation + '''
        }
    }
    Timer { interval:200;running:true;onTriggered:{ held=liveDot.pulse;liveDot.live=false } }
    Timer { interval:500;running:true;onTriggered:{
        if(!pulseAnimation.running || !pulseAnimation.paused || Math.abs(liveDot.pulse-held)>0.001) {console.log('PULSE-FAIL idle');Qt.quit();return}
        liveDot.live=true;
        if(Math.abs(liveDot.pulse-held)>0.001) {console.log('PULSE-FAIL resume');Qt.quit();return}
    } }
    Timer { interval:800;running:true;onTriggered:{
        if(Math.abs(liveDot.pulse-held)<0.01) {console.log('PULSE-FAIL progress');Qt.quit();return}
        held=liveDot.pulse;liveDot.live=false;liveDot.live=true;
        if(Math.abs(liveDot.pulse-held)>0.001) {console.log('PULSE-FAIL cache');Qt.quit();return}
        container.visible=false;held=liveDot.pulse;
    } }
    Timer { interval:1100;running:true;onTriggered:{
        console.log(pulseAnimation.paused && Math.abs(liveDot.pulse-held)<0.001 ? 'PULSE-PASS' : 'PULSE-FAIL hidden');Qt.quit();
    } }
}
''')
            env=dict(os.environ,HOME=str(work),XDG_RUNTIME_DIR=str(runtime),QT_QPA_PLATFORM='offscreen',QT_QUICK_BACKEND='software',QS_DISABLE_CRASH_HANDLER='1')
            result=subprocess.run(['qs','-p',str(shell)],env=env,capture_output=True,text=True,timeout=8)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('PULSE-PASS',result.stdout+result.stderr)
            self.assertNotIn('PULSE-FAIL',result.stdout+result.stderr)

    def run_worker(self, actions, duration, retry=False):
        with tempfile.TemporaryDirectory(prefix='usage-background-') as directory:
            work = Path(directory)
            home = work / 'home'
            runtime = work / 'runtime'
            home.mkdir()
            runtime.mkdir(mode=0o700)
            bundle = work / 'widget space'
            shutil.copytree(WIDGET, bundle, ignore=shutil.ignore_patterns('__pycache__'))
            log = work / 'calls.jsonl'
            launcher = bundle / 'bin/collect-usage'
            launcher.write_text('''#!/usr/bin/env python3
import json, sys, time
from pathlib import Path
p=Path(''' + repr(str(log)) + ''')
count=len(p.read_text().splitlines()) if p.exists() else 0
with p.open('a') as f:
    f.write(json.dumps({'time':time.monotonic(),'args':sys.argv[1:]})+'\\n')
''' + ('''if count==0: sys.exit(75)
time.sleep(3)
''' if retry else ''))
            launcher.chmod(0o755)
            shell = work / 'shell.qml'
            shell.write_text('''import QtQuick
import Quickshell
ShellRoot {
    Loader { id: view; source: ''' + json.dumps((bundle / 'UsageModel.qml').as_uri()) + '''
        onLoaded: { item.tool="claude" }
    }
''' + actions + '''
    Timer { interval: ''' + str(duration) + '''; running: true
        onTriggered: Qt.quit() }
}
''')
            env = dict(os.environ, HOME=str(home), XDG_RUNTIME_DIR=str(runtime),
                       QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software',
                       PYTHONDONTWRITEBYTECODE='1')
            for key in ('RYOKU_AI_USAGE_COLLECTOR', '__QUICKSHELL_CRASH_INFO_FD',
                        '__QUICKSHELL_CRASH_DUMP_FD'):
                env.pop(key, None)
            result = subprocess.run(['qs', '-p', str(shell)], env=env,
                                    capture_output=True, text=True,
                                    timeout=duration / 1000 + 10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(log.exists(), result.stdout + result.stderr)
            rows = [json.loads(row) for row in log.read_text().splitlines()]
            self.assertTrue(all(row['args'] == [] for row in rows), rows)
            return rows

    def test_refresh_stops_after_page_unload_and_open_refreshes_immediately(self):
        rows = self.run_worker('''
    Timer { interval: 16500; running: true; onTriggered: view.active=false }
    Timer { interval: 18500; running: true; onTriggered: view.active=true }
    Timer { interval: 20000; running: true; onTriggered: view.active=false }
''', 36000)
        self.assertEqual(len(rows), 3, rows)
        gaps = [b['time'] - a['time'] for a, b in zip(rows, rows[1:])]
        self.assertGreater(gaps[0], 14)
        self.assertLess(gaps[0], 16.2)
        self.assertGreater(gaps[1], 3)
        self.assertLess(gaps[1], 4.5)

    def test_hidden_retry_stops_and_overlapping_view_requests_share_one_worker(self):
        rows = self.run_worker('''
    Timer { interval: 500; running: true; onTriggered: view.active=false }
    Timer { interval: 3000; running: true; onTriggered: view.active=true }
''', 6500, retry=True)
        self.assertEqual(len(rows), 2, rows)
        self.assertGreater(rows[1]['time'] - rows[0]['time'], 2.8)
        self.assertLess(rows[1]['time'] - rows[0]['time'], 4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
