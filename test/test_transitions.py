"""Exercise actual transition components in Qt with isolated service stubs."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
WIDGET = Path(os.environ.get('AI_USAGE_TEST_WIDGET', ROOT/'ai-usage'))


@unittest.skipUnless(shutil.which('qs'), 'Quickshell required')
class TransitionTest(unittest.TestCase):
    def run_qml(self, content, duration=1500, cache_data=None, stat_delay=0):
        with tempfile.TemporaryDirectory(prefix='usage-transitions-') as directory:
            work = Path(directory)
            imports = work/'imports'
            def module(name, files):
                path = imports/Path(*name.split('.'))
                path.mkdir(parents=True, exist_ok=True)
                for file, text in files.items():
                    (path/file).write_text(text)
            module('inir.modules.iris.style', {
                'qmldir': 'module inir.modules.iris.style\nsingleton IrisStyle 1.0 IrisStyle.qml\n',
                'IrisStyle.qml': '''pragma Singleton
import QtQuick
QtObject {
 property bool motionEnabled:true
 property string morphName:"direct"
 property int feedbackEasing:Easing.OutCubic
 property var curves:({gentle:[0.4,0,0.2,1]})
 property real density:1
 property color accent:"#aaccff"
 property color muted:"#8899aa"
 property color text:"#eeeeee"
 property color warning:"#ddaa22"
 property color danger:"#dd5544"
 property string fontNumbers:"monospace"
 function duration(ms) { return ms }
 function weight(value) { return value }
}'''})
            module('inir', {'qmldir': 'module inir\nsingleton Translation 1.0 Translation.qml\n',
                'Translation.qml': 'pragma Singleton\nimport QtQuick\nQtObject { function tr(s) { return s } }'})
            for name in ('inir.services', 'inir.modules.common'):
                module(name, {'qmldir': 'module '+name+'\nStub 1.0 Stub.qml\n',
                              'Stub.qml': 'import QtQuick\nQtObject {}'})
            module('inir.modules.common.functions', {
                'qmldir': 'module inir.modules.common.functions\nsingleton ColorUtils 1.0 ColorUtils.qml\n',
                'ColorUtils.qml': 'pragma Singleton\nimport QtQuick\nQtObject { function applyAlpha(c,a) { return c } }'})
            module('inir.modules.common.widgets', {
                'qmldir': 'module inir.modules.common.widgets\nStyledToolTip 1.0 StyledToolTip.qml\n',
                'StyledToolTip.qml': 'import QtQuick\nItem { property bool extraVisibleCondition:false;property string text:"" }'})
            module('inir.modules.iris.components', {
                'qmldir': 'module inir.modules.iris.components\nIrisText 1.0 IrisText.qml\n',
                'IrisText.qml': 'import QtQuick\nText { enum Role { Body, Meta, Eyebrow, Title, Display, Metric }\n property int role:0 }'})
            bundle = work/'components'
            bundle.mkdir()
            for name in ('AiUsageAnimatedValue.qml', 'AiUsageLimitsCard.qml',
                         'AiUsageWindowRow.qml', 'AiUsageSpendBody.qml'):
                shutil.copy2(WIDGET/'components'/name, bundle/name)
            (bundle/'AiUsageGlassCard.qml').write_text(
                'import QtQuick\nItem { required property var page; property real radius:0 }')
            if cache_data is not None:
                shutil.copy2(WIDGET/'UsageModel.qml', bundle/'UsageModel.qml')
                shutil.copytree(WIDGET/'refresh', bundle/'refresh')
                (bundle/'bin').mkdir()
                launcher = bundle/'bin/collect-usage'
                launcher.write_text('#!/bin/sh\nexit 0\n')
                launcher.chmod(0o755)
                cache = work/'.cache/ai-usage'
                cache.mkdir(parents=True)
                for tool, data in cache_data.items():
                    (cache/(tool+'-usage.json')).write_text(json.dumps(data))
            tools = work/'tools'
            tools.mkdir()
            if stat_delay:
                wrapper = tools/'stat'
                wrapper.write_text('#!/usr/bin/env python3\nimport os,sys,time\ntime.sleep('+repr(stat_delay)+')\nos.execv("/usr/bin/stat",["stat",*sys.argv[1:]])\n')
                wrapper.chmod(0o755)
            (work/'runtime').mkdir(mode=0o700)
            shell = work/'shell.qml'
            shell.write_text('''import QtQuick
import QtQuick.Window
import Quickshell
import Quickshell.Io
import "components"
ShellRoot {
 id: probe
 property string failure:""
 function check(ok, reason) { if(!ok && !failure.length) failure=reason }
'''+content+'''
 Timer { interval:'''+str(duration)+''';running:true;onTriggered:{
  console.log(probe.failure.length ? "TRANSITION-FAIL "+probe.failure : "TRANSITION-PASS");Qt.quit();
 } }
}
''')
            env = dict(os.environ, HOME=str(work), XDG_RUNTIME_DIR=str(work/'runtime'),
                       XDG_CONFIG_HOME=str(work/'config'), XDG_STATE_HOME=str(work/'state'),
                       QML_IMPORT_PATH=str(imports), QT_QPA_PLATFORM='offscreen',
                       PATH=str(tools)+os.pathsep+os.environ.get('PATH',''),
                       QT_QUICK_BACKEND='software', QS_DISABLE_CRASH_HANDLER='1')
            result = subprocess.run(['qs', '-p', str(shell)], env=env,
                                    capture_output=True, text=True, timeout=duration/1000+8)
            output = result.stdout+result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn('TRANSITION-PASS', output)
            self.assertNotIn('TRANSITION-FAIL', output)
            self.assertNotIn('ReferenceError', output)
            self.assertNotIn('TypeError', output)

    def test_switch_to_unavailable_agent_never_reveals_a_hidden_budget(self):
        self.run_qml('''
 function row(node) {
  if(node.proportion!==undefined && node.transition!==undefined) return node;
  for(const child of (node.children||[])) { const found=row(child);if(found)return found }
  return null;
 }
 QtObject {id:fakeUsage
  property bool has:true
  property bool switching:false
  property string plan:"local messages"
  property real today:1000
  property var quota:({})
  property var windows:[{label:"5h",pct:100,caption:"local budget",resetTs:0}]
  function kmg(n) { return String(n) }
  function resetAt(n,t) { return "reset" }
  function relative(n,t) { return "" }
  function normalizeWindows(d) { return d._windows }
 }
 QtObject {id:fakePage
  property int radius:10;property int pad:10;property int step:2
  property string activeTool:"opencode";property string toolLabel:"OpenCode"
  property var translateTime:null
 }
 Window {visible:true;width:300;height:300
  AiUsageLimitsCard {id:card;width:240;height:implicitHeight;visible:fakePage.activeTool!=="opencode";usage:fakeUsage;page:fakePage}
 }
 Timer {interval:140;running:true;onTriggered:{fakeUsage.switching=true;fakePage.activeTool="claude";fakePage.toolLabel="Claude"} }
 Timer {interval:190;running:true;onTriggered:{
  probe.check(probe.row(card)===null,"previous agent's exhausted budget was visible during selection");
  fakeUsage.windows=[];fakeUsage.plan="";fakeUsage.switching=false;
 } }
 Timer {interval:260;running:true;onTriggered:probe.check(probe.row(card)===null,"unavailable Claude inherited quota rows") }
''', 400)

    def test_values_interpolate_and_retarget_from_current_value(self):
        self.run_qml('''
 property real held:0
 AiUsageAnimatedValue { id:value;targetValue:100;contextKey:"codex" }
 Timer { interval:70;running:true;onTriggered:{
  probe.check(value.value===100 && !value.tween.running,"first value counted from zero");value.targetValue=200;
 } }
 Timer { interval:150;running:true;onTriggered:{
  probe.check(value.value>100 && value.value<200,"no intermediate value");
  probe.held=value.value;value.targetValue=300;
  probe.check(value.value===probe.held,"retarget jumped");
 } }
 Timer { interval:250;running:true;onTriggered:probe.check(value.value>probe.held && value.value<300,"retarget did not continue") }
 Timer { interval:600;running:true;onTriggered:probe.check(value.value===300 && !value.tween.running,"wrong final value") }
''', 750)

    def test_parse_coalescing_context_unavailable_hidden_and_reduced_motion(self):
        self.run_qml('''
 AiUsageAnimatedValue { id:value;targetValue:100;contextKey:"codex" }
 Timer { interval:70;running:true;onTriggered:{
  value.available=false;value.targetValue=0;value.available=true;value.targetValue=200;
 } }
 Timer { interval:100;running:true;onTriggered:{
  probe.check(value.hasValue && value.value>=100 && value.value<200,"parse flashed zero or unavailable");
  value.contextKey="claude";value.targetValue=10;
 } }
 Timer { interval:140;running:true;onTriggered:{
  probe.check(value.value===10 && !value.tween.running,"animated across agents");
  probe.check(value.opacity>0 && value.opacity<1,"missing state fade");
  value.hold=true;value.targetValue=999;value.contextKey="other";
 } }
 Timer { interval:210;running:true;onTriggered:{probe.check(value.value===10,"switching replaced held data");value.hold=false} }
 Timer { interval:250;running:true;onTriggered:{probe.check(value.value===999,"switch never landed");value.available=false} }
 Timer { interval:290;running:true;onTriggered:{probe.check(!value.hasValue,"unavailable showed a value");value.available=true;value.targetValue=50} }
 Timer { interval:330;running:true;onTriggered:{probe.check(value.value===50,"counted from missing data");value.active=false;value.targetValue=90} }
 Timer { interval:370;running:true;onTriggered:{
  probe.check(value.value===90 && !value.tween.running && value.opacity===1,"hidden animation running");
  value.active=true;value.targetValue=120;
 } }
 Timer { interval:420;running:true;onTriggered:value.motionEnabled=false }
 Timer { interval:460;running:true;onTriggered:probe.check(value.value===120 && !value.tween.running && value.opacity===1,"reduced motion animates") }
''', 650)

    def test_real_cards_keep_rows_and_animate_collected_values(self):
        self.run_qml('''
 property var retained:null
 property real priorHeight:0
 function row(node) {
  if(node.proportion!==undefined && node.transition!==undefined) return node;
  for(const child of (node.children||[])) { const found=row(child);if(found)return found }
  return null;
 }
 function texts(node) {
  let values=node.text===undefined ? [] : [String(node.text)];
  for(const child of (node.children||[])) values=values.concat(texts(child));
  return values;
 }
 QtObject { id:fakeUsage
  property bool has:true
  property bool switching:false
  property string plan:"plus"
  property real today:100
  property var quota:({})
  property var windows:[{label:"5h",pct:25,caption:"",resetTs:0}]
  function kmg(n) { return String(n) }
  function resetAt(n,t) { return "reset" }
  function relative(n,t) { return "" }
  function normalizeWindows(d) { return d._windows }
 }
 QtObject { id:fakePage
  property int radius:10
  property int pad:10
  property int step:2
  property string activeTool:"codex"
  property string toolLabel:"Codex"
  property bool planAgent:true
  property string spendHelp:"API equivalent"
  property var translateTime:null
  property var monthly:({current:100,label:"Nov",available:true,partial:false,stale:false})
  function money(n) { return "$"+Number(n).toFixed(2) }
 }
 Window {visible:true;width:500;height:400
  AiUsageLimitsCard { id:card;width:240;height:implicitHeight;visible:fakeUsage.has;usage:fakeUsage;page:fakePage }
  AiUsageSpendBody { id:spend;x:250;width:240;visible:fakeUsage.has;usage:fakeUsage;page:fakePage }
 }
 Timer { interval:150;running:true;onTriggered:{
  probe.retained=probe.row(card);probe.priorHeight=card.implicitHeight;
  probe.check(probe.retained!==null,"quota row missing");
  fakeUsage.windows=[];fakeUsage.today=0;fakeUsage.has=false;
  fakeUsage.windows=[{label:"5h",pct:75,caption:"",resetTs:0}];fakeUsage.today=200;fakeUsage.has=true;
  fakePage.monthly={current:200,label:"Nov",available:true,partial:false,stale:false};
 } }
 Timer { interval:230;running:true;onTriggered:{
  const current=probe.row(card);
  probe.check(current===probe.retained,"collector rebuilt the quota row");
  probe.check(current.transition.value>0.25 && current.transition.value<0.75,"bar did not interpolate");
  probe.check(card.todayValue.value>100 && card.todayValue.value<200,"tokens did not interpolate");
  probe.check(probe.texts(card).some(text=>/^\\d+$/.test(text)),"fractional token count displayed");
  probe.check(spend.amount.value>100 && spend.amount.value<200,"API value did not interpolate");
  probe.check(card.implicitHeight===probe.priorHeight,"update changed card height");
 } }
 Timer { interval:600;running:true;onTriggered:{
  probe.check(probe.row(card).transition.value===0.75,"bar final value");
  probe.check(card.todayValue.value===200 && spend.amount.value===200,"metric final values");
 } }
''', 750)


if __name__ == '__main__':
    unittest.main(verbosity=2)
