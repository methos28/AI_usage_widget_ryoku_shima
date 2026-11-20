"""Check real cache readers and presentation across every agent switch."""
from pathlib import Path
from datetime import datetime
import json
import os
import re
import runpy
import shutil
import unittest

ROOT = Path(__file__).resolve().parents[1]
WIDGET = Path(os.environ.get('AI_USAGE_TEST_WIDGET', ROOT/'ai-usage'))
transitions = runpy.run_path(str(ROOT/'test/test_transitions.py'))
widgets = runpy.run_path(str(ROOT/'test/test_widget.py'))


class AgentSwitchTest(unittest.TestCase):
    def ready_binding(self, path, model='usageModel'):
        source = (WIDGET/path).read_text()
        return re.search(r'readonly property bool dataReady: (.+)', source)[1]

    def data(self):
        month = datetime.now().strftime('%Y-%m')
        day = datetime.now().strftime('%Y-%m-%d')
        result = {}
        for index, agent in enumerate(('opencode', 'codex', 'claude'), 1):
            result[agent] = dict(_source='fixture', _plan='local messages' if agent=='opencode' else 'plus' if agent=='codex' else '',
                _today_tokens=1001*index, _days=[dict(date=day,tokens=1001*index,cost=111.11*index)],
                _hours=[dict(start=1,tokens=1001*index)],
                _sessions=[dict(id=agent,title=agent,started=1,updated=1,tokens=1001*index,running=False)],
                _periods={'all':dict(tokens=1001*index,models=[dict(name=agent,total=1001*index)])},
                _spending=dict(kind='api-equivalent',month=month,amount=111.11*index),
                _quota=dict(available=False,stale=False))
        result['opencode']['5h-utilization']='1.0'
        result['codex']['_windows']=[dict(minutes=300,utilization=0.25)]
        result['claude']['_windows']=[]
        return result

    @unittest.skipUnless(shutil.which('qs'), 'Quickshell required for native scene checks')
    def run_scene(self, qml, duration, data, delay):
        transitions['TransitionTest'].run_qml(self,qml,duration,cache_data=data,stat_delay=delay)

    def test_all_six_agent_directions_publish_only_matching_stats(self):
        monthly = widgets['binding']((WIDGET/'IrisCompact.qml').read_text(), 'monthly').replace('root.', 'probe.')
        ready = self.ready_binding('IrisCompact.qml').replace('root.', 'probe.')
        self.run_scene('''
 property var sequence:["opencode","codex","claude","opencode","claude","codex","opencode"]
 property int step:0
 property int steady:0
 property string activeTool:sequence[step]
 readonly property bool dataReady:'''+ready+'''
 property int radius:10;property int pad:10;property int stepSize:2
 property string toolLabel:activeTool;property bool planAgent:activeTool!=="opencode"
 property var translateTime:null;property string spendHelp:""
 property var monthly:{'''+monthly+'''}
 function monthLabel(key) { return key }
 function money(n) { return "$"+Number(n).toFixed(2) }
 property int expected:activeTool==="opencode"?1001:activeTool==="codex"?2002:3003
 function row(node) {
  if(node.proportion!==undefined && node.transition!==undefined) return node;
  for(const child of (node.children||[])) {const found=row(child);if(found)return found}
  return null;
 }
 QtObject {id:page
  property int radius:10;property int pad:10;property int step:2
  property string activeTool:probe.activeTool;property string toolLabel:probe.activeTool
  property bool planAgent:probe.planAgent;property var monthly:probe.monthly
  property string spendHelp:"";property var translateTime:null
  function money(n) {return "$"+Number(n).toFixed(2)}
 }
 Window {visible:true;width:500;height:400
  UsageModel {id:usageModel;tool:probe.activeTool}
  Item {id:content;opacity:probe.dataReady?1:0
   AiUsageLimitsCard {id:card;width:240;height:implicitHeight;usage:usageModel;page:page;visible:usageModel.has && (usageModel.hasPlan || probe.activeTool==="claude")}
   AiUsageSpendBody {id:spend;x:250;width:240;usage:usageModel;page:page}
  }
 }
 FrameAnimation {running:true;onTriggered:{
  if(!probe.dataReady) {probe.check(content.opacity===0,"old stats stayed visible");return}
  probe.check(usageModel.loadedTool===probe.activeTool,"wrong read owner");
  probe.check(usageModel.today===probe.expected,"wrong token snapshot");
  probe.check(usageModel.days[0]?.tokens===probe.expected,"wrong activity snapshot");
  probe.check(usageModel.period("all")?.tokens===probe.expected,"wrong period snapshot");
  probe.check(usageModel.sessions[0]?.id===probe.activeTool,"wrong session snapshot");
  if(probe.activeTool==="claude") probe.check(probe.row(card)===null,"unavailable Claude displayed old quota");
  const target=probe.activeTool==="opencode"?111.11:probe.activeTool==="codex"?222.22:333.33;
  if(spend.amount.hasValue && spend.amount.opacity>0) probe.check(Math.abs(spend.amount.value-target)<0.00001,"API value crossed agents");
  if(card.todayValue.hasValue && card.todayValue.opacity>0) probe.check(card.todayValue.value===probe.expected,"token animation crossed agents");
 } }
 Timer {interval:45;repeat:true;running:true;onTriggered:{
  if(probe.dataReady && usageModel.has) probe.steady++;else probe.steady=0;
  if(probe.steady>=3 && probe.step<probe.sequence.length-1){probe.steady=0;probe.step++}
 } }
 Timer {interval:2800;running:true;onTriggered:probe.check(probe.step===6 && probe.dataReady,"not all six directions completed")}
''', 3000, self.data(), 0.08)

    def test_rapid_round_trip_ignores_an_old_same_agent_stat_result(self):
        data = self.data()
        updated = dict(data['opencode'], _today_tokens=4040)
        ready = self.ready_binding('IrisCompact.qml').replace('root.', 'probe.')
        self.run_scene('''
 property string activeTool:"opencode"
 property bool rewritten:false
 readonly property bool dataReady:'''+ready+'''
 Window {visible:true;width:10;height:10
  UsageModel {id:usageModel;tool:probe.activeTool}
 }
 FrameAnimation {running:true;onTriggered:{
  if(probe.rewritten && probe.activeTool==="opencode" && probe.dataReady)
   probe.check(usageModel.today===4040,"old same-agent stat job overwrote a newer selection");
 } }
 Process {id:rewrite
  command:["python3","-c","import pathlib,sys;pathlib.Path(sys.argv[1]).write_text(sys.argv[2])",
   Quickshell.env("HOME")+"/.cache/ai-usage/opencode-usage.json",'''+json.dumps(json.dumps(updated))+''']
  onExited:{probe.rewritten=true;probe.activeTool="opencode"}
 }
 Timer {interval:80;running:true;onTriggered:probe.activeTool="codex"}
 Timer {interval:120;running:true;onTriggered:probe.activeTool="claude"}
 Timer {interval:160;running:true;onTriggered:rewrite.running=true}
 Timer {interval:2200;running:true;onTriggered:probe.check(usageModel.loadedTool==="opencode" && usageModel.today===4040,"latest round-trip snapshot did not land")}
''', 2400, data, 0.4)

    def test_missing_agent_caches_clear_old_state_and_recover(self):
        ready = self.ready_binding('IrisCompact.qml').replace('root.', 'probe.')
        self.run_scene('''
 property string activeTool:"opencode"
 readonly property bool dataReady:'''+ready+'''
 Window {visible:true;width:10;height:10
  UsageModel {id:usageModel;tool:probe.activeTool}
 }
 Timer {interval:250;running:true;onTriggered:probe.activeTool="codex"}
 Timer {interval:500;running:true;onTriggered:{probe.check(!usageModel.has && !probe.dataReady,"missing Codex retained old state");probe.activeTool="claude"}}
 Timer {interval:750;running:true;onTriggered:{probe.check(!usageModel.has && !probe.dataReady,"missing Claude retained old state");probe.activeTool="opencode"}}
 Timer {interval:1100;running:true;onTriggered:probe.check(probe.dataReady && usageModel.today===1001,"available agent did not recover")}
''', 1250, {'opencode':self.data()['opencode']}, 0.06)

    def test_newer_selected_cache_supersedes_an_inflight_old_snapshot(self):
        data = self.data()
        updated = dict(data['opencode'], _today_tokens=3030)
        ready = self.ready_binding('IrisCompact.qml').replace('root.', 'probe.')
        self.run_scene('''
 property string activeTool:"opencode"
 property bool rewritten:false
 readonly property bool dataReady:'''+ready+'''
 Window {visible:true;width:10;height:10
  UsageModel {id:usageModel;tool:probe.activeTool}
 }
 FrameAnimation {running:true;onTriggered:{
  if(probe.rewritten && probe.dataReady) probe.check(usageModel.today===3030,"an older pending snapshot was displayed first");
 } }
 Process {id:rewrite
  command:["python3","-c","import pathlib,sys;pathlib.Path(sys.argv[1]).write_text(sys.argv[2])",
   Quickshell.env("HOME")+"/.cache/ai-usage/opencode-usage.json",'''+json.dumps(json.dumps(updated))+''']
  onExited:probe.rewritten=true
 }
 Timer {interval:80;running:true;onTriggered:rewrite.running=true}
 Timer {interval:950;running:true;onTriggered:probe.check(probe.dataReady && usageModel.today===3030,"newest selected snapshot did not land")}
''', 1100, data, 0.35)

    def test_tile_and_all_cards_gate_the_selected_snapshot(self):
        source = (WIDGET/'IrisCompact.qml').read_text()
        self.assertEqual(source.count('opacity: root.dataReady ? 1 : 0'), 4)
        normal = self.ready_binding('IrisCompact.qml')
        tile = self.ready_binding('AiUsageTile.qml')
        widgets['node']('''const assert=require('node:assert/strict');
const root={activeTool:''};const usageModel={switching:false,loadedTool:''};const usage=usageModel;
function pageReady(){return '''+normal+'''}
function tileReady(){return '''+tile+'''}
for(const from of ['opencode','codex','claude']) for(const to of ['opencode','codex','claude']) {
 root.activeTool=to;usageModel.loadedTool=from;usageModel.switching=false;
 assert.equal(pageReady(),from===to);assert.equal(tileReady(),from===to);
 usageModel.switching=true;assert.equal(pageReady(),false);assert.equal(tileReady(),false);
 usageModel.loadedTool=to;usageModel.switching=false;assert.equal(pageReady(),true);assert.equal(tileReady(),true);
}
''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
