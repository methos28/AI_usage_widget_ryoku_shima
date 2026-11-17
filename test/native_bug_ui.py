"""Verify stale activity and parse recovery in an isolated Qt engine."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile

widget = Path(os.environ.get('AI_USAGE_TEST_WIDGET', Path(__file__).resolve().parents[1]/'ai-usage'))
with tempfile.TemporaryDirectory(prefix='usage-ui-audit-') as directory:
    work = Path(directory)
    bundle = work/'widget'
    shutil.copytree(widget, bundle, ignore=shutil.ignore_patterns('__pycache__'))
    launcher = bundle/'bin/collect-usage'
    launcher.write_text('#!/bin/sh\nexit 1\n')
    launcher.chmod(0o755)
    for name in ('home', 'runtime'):
        (work/name).mkdir(mode=0o700)
    shell = work/'shell.qml'
    shell.write_text('''import QtQuick
import Quickshell
ShellRoot {
 Loader { source: '''+json.dumps((bundle/'UsageModel.qml').as_uri())+'''
 onLoaded: {
    item.visible=false;
    item.parse(JSON.stringify({_source:'rpc',_sessions:[{id:'old',title:'Old',running:true}]}),Date.now()/1000-3600);
    console.log('STALE-SESSION', 'fresh='+item.fresh, 'running='+item.runningSessions.length);
    item.parse(JSON.stringify({_source:'rpc',_today_tokens:999,_periods:{today:{models:[null]}}}),Date.now()/1000);
    console.log('PARTIAL-PARSE','has='+item.has,'today='+item.today);
    item.parse(JSON.stringify({_source:'rpc',_sessions:[{id:'old',title:'Old',running:true}]}),Date.now()/1000);
    console.log('FRESH-SESSION','fresh='+item.fresh,'running='+item.runningSessions.length);
    item._modifiedAt=Date.now()/1000-3600;item.tick++;
    console.log('AGED-SESSION','fresh='+item.fresh,'running='+item.runningSessions.length);
    Qt.callLater(Qt.quit);
 } }
 Timer { interval:4000;running:true;onTriggered:Qt.quit() }
}
''')
    env = dict(os.environ, HOME=str(work/'home'), XDG_RUNTIME_DIR=str(work/'runtime'),
               XDG_CONFIG_HOME=str(work/'config'), XDG_STATE_HOME=str(work/'state'),
               QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software',
               QS_DISABLE_CRASH_HANDLER='1', AI_USAGE_DISABLE_PRICE_DOWNLOADS='1')
    env.pop('RYOKU_AI_USAGE_COLLECTOR', None)
    result = subprocess.run(['qs','-p',str(shell)],env=env,capture_output=True,text=True,timeout=8)
    print(result.stdout+result.stderr)
    assert result.returncode == 0
    assert 'fresh=false running=0' in result.stdout+result.stderr
    assert 'has=false today=0' in result.stdout+result.stderr

    assert 'FRESH-SESSION fresh=true running=1' in result.stdout+result.stderr
    assert 'AGED-SESSION fresh=false running=0' in result.stdout+result.stderr
