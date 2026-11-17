#!/usr/bin/env python3
"""Exercise the shipped QML expressions and compile real components in isolation."""
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
SHIPPED = ROOT / 'ryoku/shell/quickshell/inir/defaults/widgets/ai-usage'
WIDGET = Path(os.environ.get('AI_USAGE_TEST_WIDGET', SHIPPED if SHIPPED.exists() else ROOT / 'ai-usage'))
IMPORTS = (ROOT / 'ryoku/shell/quickshell' if SHIPPED.exists() else
           Path(os.environ.get('RYOKU_QML_IMPORTS', Path.home() / '.config/quickshell')))


def function(source, name):
    start = source.index('    function ' + name + '(')
    end = source.index('\n    }', start) + len('\n    }')
    body = source[start:end]
    body = re.sub(r': (?:string|var|int|double|bool)(?=[,)])', '', body)
    return re.sub(r'\): (?:string|var|int|double|bool|void) \{', ') {', body)


def binding(source, name):
    match = re.search(r'^    readonly property \w+ ' + re.escape(name) + r': \{\n',
                      source, re.M)
    if not match:
        raise AssertionError('Missing binding: ' + name)
    end = source.index('\n    }', match.end())
    return source[match.end():end]


def node(script, timezone='Asia/Kolkata'):
    script = '''globalThis.Translation={tr:key=>String(key)};
String.prototype.arg=function(value) {
    const slots=[...this.matchAll(/%([1-9][0-9]*)/g)].map(match=>Number(match[1]));
    return slots.length ? this.replace(new RegExp('%'+Math.min(...slots),'g'),String(value)) : String(this);
};
''' + script
    result = subprocess.run(['node', '-e', script], capture_output=True, text=True,
                            env=dict(os.environ, TZ=timezone), timeout=15)
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)


SETUP = '''
const assert = require('node:assert/strict');
const RealDate = Date;
let clock = new RealDate(2026, 10, 7, 12).getTime();
global.Date = class extends RealDate {
    constructor(...args) { super(...(args.length ? args : [clock])); }
    static now() { return clock; }
};
const Qt = {formatDate: (d,format) => {
    const value=[d.getFullYear(), String(d.getMonth()+1).padStart(2,'0'),
        String(d.getDate()).padStart(2,'0')].join('-');
    return format==='yyyy-MM' ? value.slice(0,7) : value;
}};
'''


class WidgetTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which('qs'),'Quickshell required')
    def test_native_tile_fallback_reads_qobject_availability(self):
        source=(WIDGET/'AiUsageTile.qml').read_text()
        with tempfile.TemporaryDirectory(prefix='tile-fallback-') as directory:
            work=Path(directory);runtime=work/'runtime';runtime.mkdir(mode=0o700)
            (work/'shell.qml').write_text('''import QtQuick
import Quickshell
ShellRoot {
 Item { id:root;property string tool:"opencode"
  QtObject {id:availability;property bool ready:true;property bool opencode:false;property bool codex:true;property bool claude:false}
  QtObject {id:usage;property bool collectionReady:false}
  readonly property string activeTool: {'''+binding(source,'activeTool')+'''}
  Component.onCompleted: {
   if(activeTool!=="opencode"){console.log("TILE-FAIL readiness");Qt.callLater(Qt.quit);return}
   usage.collectionReady=true;
   Qt.callLater(()=>{
    if(activeTool!=="codex"){console.log("TILE-FAIL codex");Qt.quit();return}
    availability.codex=false;availability.claude=true;
    Qt.callLater(()=>{
     console.log(activeTool==="claude"?"TILE-PASS":"TILE-FAIL claude");Qt.quit();
    });
   });
  }
 }
 Timer {interval:1500;running:true;onTriggered:Qt.quit()}
}
''')
            result=subprocess.run(['qs','-p',str(work/'shell.qml')],capture_output=True,text=True,timeout=5,
                env=dict(os.environ,HOME=str(work),XDG_RUNTIME_DIR=str(runtime),QT_QPA_PLATFORM='offscreen',QS_DISABLE_CRASH_HANDLER='1'))
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('TILE-PASS',result.stdout+result.stderr)
            self.assertNotIn('TypeError',result.stdout+result.stderr)

    def test_tile_falls_back_after_collection_and_preserves_available_selection(self):
        source=(WIDGET/'AiUsageTile.qml').read_text()
        script=SETUP+'\nfunction activeTool(){'+binding(source,'activeTool')+'\n}'
        script+='''
const root={tool:'opencode'};
const availability={ready:false,opencode:false,codex:true,claude:false};
const usage={collectionReady:false};
assert.equal(activeTool(),'opencode');
availability.ready=true;
assert.equal(activeTool(),'opencode');
usage.collectionReady=true;
assert.equal(activeTool(),'codex');
availability.codex=false;availability.claude=true;
assert.equal(activeTool(),'claude');
root.tool='claude';availability.opencode=true;
assert.equal(activeTool(),'claude');
availability.claude=false;
assert.equal(activeTool(),'opencode');
availability.opencode=false;
assert.equal(activeTool(),'opencode');
'''
        node(script)
        self.assertIn('tool: root.activeTool',source)

    def test_quota_percentage_uses_translated_word_order(self):
        source=(WIDGET/'components/AiUsageLimitsCard.qml').read_text()
        expression=re.search(r'^\s+share: (.+)$',source,re.M).group(1)
        node(SETUP+'''
Translation.tr=key=>key==='%1% used'?'utilise : %1 %':key;
const modelData={pct:42};
const share='''+expression+''';
assert.equal(share,'utilise : 42 %');
''')

    def test_claude_login_bootstraps_without_projects_and_ignores_other_profiles(self):
        fixture,bundle,env=self.bundle_fixture()
        for name in ('opencode-usage','codex-usage'):
            (bundle/'bin'/name).write_text('#!/bin/sh\nexit 0\n')
        marker=fixture.home/'claude-calls.jsonl'
        script=bundle/'bin/claude-usage'
        script.write_text('#!/usr/bin/env python3\nimport json,sys\nfrom pathlib import Path\n'
            +'with Path('+repr(str(marker))+').open("a") as f: f.write(json.dumps(sys.argv[1:])+"\\n")\n')
        script.chmod(0o755)
        config=fixture.home/'.claude'
        env=dict(env,CLAUDE_CONFIG_DIR=str(config))
        def refresh():
            subprocess.run([str(bundle/'bin/collect-usage')],env=env,check=True,
                           capture_output=True,text=True,timeout=10)
        refresh()
        self.assertFalse(marker.exists())
        config.mkdir(exist_ok=True)
        (config/'.credentials.json').write_text('{}')
        refresh()
        rows=[json.loads(line) for line in marker.read_text().splitlines()]
        self.assertEqual(rows,[['--cache',str(fixture.home/'.cache/ai-usage/claude-usage.json')]])
        self.assertFalse((config/'projects').exists())
        (config/'.credentials.json').unlink()
        (fixture.home/'.claude.json').write_text('{}')
        alternate=fixture.home/'alternate-profile';alternate.mkdir()
        env['CLAUDE_CONFIG_DIR']=str(alternate)
        refresh()
        self.assertEqual(len(marker.read_text().splitlines()),1)
        (alternate/'.claude.json').write_text('{}')
        refresh()
        self.assertEqual(len(marker.read_text().splitlines()),2)

    @unittest.skipUnless(shutil.which('qs'),'Quickshell required')
    def test_native_rolling_labels_accept_default_and_explicit_end(self):
        source=(WIDGET/'IrisCompact.qml').read_text()
        start=source.index('    function bucketLabel(')
        end=source.index('\n    }',start)+len('\n    }')
        with tempfile.TemporaryDirectory(prefix='rolling-label-') as directory:
            work=Path(directory);runtime=work/'runtime';runtime.mkdir(mode=0o700)
            (work/'shell.qml').write_text('''import QtQuick
import Quickshell
ShellRoot {
 Item { id:root; property var trend: ({unit:"hours"})
'''+source[start:end]+'''
 Component.onCompleted: {
  const stamp=Date.now();const row={start:stamp-86400000,end:stamp};
  const first=bucketLabel(row), last=bucketLabel(row,true);
  console.log(first.length>0 && last.length>0 && first!==last ? "LABEL-PASS" : "LABEL-FAIL");
  Qt.callLater(Qt.quit);
 }
 }
 Timer {interval:1500;running:true;onTriggered:Qt.quit()}
}
''')
            result=subprocess.run(['qs','-p',str(work/'shell.qml')],capture_output=True,text=True,timeout=5,
                env=dict(os.environ,HOME=str(work),XDG_RUNTIME_DIR=str(runtime),QT_QPA_PLATFORM='offscreen',QS_DISABLE_CRASH_HANDLER='1'))
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('LABEL-PASS',result.stdout+result.stderr)
            self.assertNotIn('TypeError',result.stdout+result.stderr)

    def test_rolling_chart_uses_exact_collector_bins_and_full_range(self):
        source=(WIDGET/'IrisCompact.qml').read_text()
        script=SETUP+function(source,'historyWeight')+'\n'+function(source,'bucketLabel')
        script+='\nfunction trend(){'+binding(source,'trend')+'\n}'
        script+='''
const start=clock-86400000;
const rolling=Array.from({length:24},(_,i)=>({start:start+i*3600000,end:start+(i+1)*3600000,tokens:i,cacheRead:1}));
const usageModel={hours:[{start:0,tokens:9999}],period:key=>({hours:rolling})};
const root={hourly:true,periodKey:'24h',historyWeight};
root.trend=trend();
assert.equal(root.trend.buckets.length,24);
assert.equal(root.trend.total,300);
assert.equal(root.trend.buckets[0].start,start);
assert.equal(root.trend.buckets.at(-1).end,clock);
Qt.formatDateTime=date=>String(date.getTime());
assert.equal(Number(bucketLabel(root.trend.buckets.at(-1),true))-Number(bucketLabel(root.trend.buckets[0])),86400000);
'''
        node(script)

    def test_translations_preserve_period_keys_and_format_relative_times(self):
        page=(WIDGET/'IrisCompact.qml').read_text()
        model=(WIDGET/'UsageModel.qml').read_text()
        options=re.search(r'readonly property var periodOptions: (\[[\s\S]*?\n    \])',page).group(1)
        labels=page.split('readonly property var timeLabels: ',1)[1].split('\n    function translateTime',1)[0]
        script=SETUP+'''
const words={'Today':'Aujourd hui','%1 min. ago':'il y a %1 min','resets %1':'retour %1'};
Translation.tr=key=>words[key]??key;
'''
        script+='const options='+options+';\nconst root={tick:0,timeLabels:'+labels+'};\n'
        script+=function(page,'translateTime')+'\n'+function(model,'relative')+'\n'+function(model,'resetAt')
        script+='''
assert.deepEqual(options.map(option=>option.value),['today','24h','7','30','all']);
assert.equal(options[0].label,'Aujourd hui');
assert.equal(options[1].label,'Last 24 hours');
assert.equal(relative(clock-10*60000,translateTime),'il y a 10 min');
Qt.formatDateTime=()=> 'local deadline';
assert.equal(resetAt(clock/1000+60,translateTime),'retour local deadline');
'''
        node(script)

    def fixture(self, name):
        names = {'codex': 'codex-usage-regression.py', 'contract': 'ai-usage-cache.py'}
        primary = {'codex': 'test_codex_usage.py', 'contract': 'cache_contract.py'}
        path = ROOT / 'tests' / names[name] if SHIPPED.exists() else ROOT / 'test' / primary[name]
        spec = importlib.util.spec_from_file_location('bundle_' + name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def bundle_fixture(self):
        fixture = self.fixture('codex').CodexUsageTest()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        bundle = fixture.home / 'widget space $(touch injected)'
        shutil.copytree(WIDGET, bundle)
        env = dict(fixture.env, OPENCODE_DATA_DIR=str(fixture.home / 'absent'),
                   XDG_CONFIG_HOME=str(fixture.home / 'config'),
                   XDG_STATE_HOME=str(fixture.home / 'state'),
                   XDG_CACHE_HOME=str(fixture.home / 'cache'))
        return fixture, bundle, env

    def test_cache_inclusive_today_and_invalid_cache_shape(self):
        source = (WIDGET / 'UsageModel.qml').read_text()
        names = ('empty', 'pct', 'normalizeWindows', 'shortName', 'normalizePeriods', 'kmg', 'updateFreshness', 'parse')
        script = SETUP + '\n'.join(function(source, name) for name in names)
        script += '\nconst root={' + ','.join(names) + '}; const switchTimer={stop(){}};'
        script += """
root.parse(JSON.stringify({_source:'fixture',_today_tokens:5000,_today_tokens_with_cache_read:45000}),clock/1000);
assert.equal(root.today,45000);
root.parse(JSON.stringify({_source:'fixture',_today_tokens:6000}),clock/1000);
assert.equal(root.today,6000);
root.parse(JSON.stringify({_source:'storage',_stale:true}),clock/1000);
assert.equal(root.fresh,false);
root.parse(JSON.stringify({_source:'stale'}),clock/1000);
assert.equal(root.fresh,false);
root.parse(JSON.stringify({_source:'storage'}),clock/1000);
assert.equal(root.fresh,true);
root.parse(JSON.stringify({_source:'fixture'}),clock/1000+3600);
assert.equal(root.fresh,false);
for(const invalid of ['[123]','"not a cache"','null','{}']) {
    root.parse(invalid,clock/1000);
    assert.equal(root.has,false);
    assert.equal(root.today,0);
}
"""
        node(script)

    @unittest.skipUnless(shutil.which('qs'), 'Quickshell required for large counter check')
    def test_real_model_preserves_more_than_two_billion_tokens(self):
        with tempfile.TemporaryDirectory(prefix='large-token-qml-') as directory:
            work = Path(directory)
            for name in ('home','runtime'):
                (work / name).mkdir(mode=0o700)
            (work / 'shell.qml').write_text("""import QtQuick
import Quickshell
ShellRoot {
 Loader { source: """ + json.dumps((WIDGET / 'UsageModel.qml').as_uri()) + """
 onLoaded: {
    item.visible=false;
    item.parse(JSON.stringify({_source:'fixture',_today_tokens:3000000000,'5h-reset':'2200000000','7d-reset':'2200100000'}),Math.floor(Date.now()/1000));
    console.log(item.today===3000000000 && item.reset5hTs===2200000000 && item.reset7dTs===2200100000 ? 'LARGE-COUNT-PASS' : 'LARGE-COUNT-FAIL',item.today);
    Qt.callLater(Qt.quit);
 } }
 Timer { interval:4000;running:true;onTriggered:Qt.quit() }
}""")
            env = dict(os.environ, HOME=str(work / 'home'), XDG_CONFIG_HOME=str(work / 'config'),
                       XDG_CACHE_HOME=str(work / 'cache'), XDG_STATE_HOME=str(work / 'state'),
                       XDG_RUNTIME_DIR=str(work / 'runtime'), QT_QPA_PLATFORM='offscreen',
                       QS_DISABLE_CRASH_HANDLER='1', CODEX_USAGE_DISABLE_RPC='1',
                       CODEX_USAGE_DISABLE_PRICES='1', AI_USAGE_DISABLE_PRICE_DOWNLOADS='1',
                       CODEX_HOME=str(work / 'codex'), CLAUDE_CONFIG_DIR=str(work / 'claude'),
                       OPENCODE_DATA_DIR=str(work / 'opencode'), CODEX_USAGE_STATE_DIR=str(work / 'state'))
            result = subprocess.run(['qs','-p',str(work / 'shell.qml')], env=env,
                                    capture_output=True,text=True,timeout=8)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('LARGE-COUNT-PASS',result.stdout+result.stderr)

    def test_today_chart_keeps_all_tokens_on_dst_transition_days(self):
        source = (WIDGET / 'IrisCompact.qml').read_text()
        script = SETUP + '\n' + function(source, 'historyWeight')
        script += '\nfunction trend(){' + binding(source, 'trend') + '}\n'
        script += """
const usageModel={hours:[]}; const root={hourly:true,periodKey:'today',historyWeight};
clock=new RealDate(2026,10,1,23,30).getTime();
usageModel.hours=[['2026-11-01T01:00:00-04:00',10],['2026-11-01T01:00:00-05:00',20],['2026-11-01T23:00:00-05:00',30]]
 .map(([stamp,tokens])=>({start:new RealDate(stamp).getTime(),tokens}));
let result=trend();
assert.equal(result.buckets.length,24);assert.equal(result.total,60);
assert.equal(result.buckets[1].tokens,30);assert.equal(result.buckets[23].tokens,30);
clock=new RealDate(2026,2,8,23,30).getTime();
usageModel.hours=[['2026-03-08T01:00:00-05:00',10],['2026-03-08T03:00:00-04:00',20],['2026-03-08T23:00:00-04:00',30]]
 .map(([stamp,tokens])=>({start:new RealDate(stamp).getTime(),tokens}));
result=trend();assert.equal(result.buckets.length,24);assert.equal(result.total,60);
assert.equal(result.buckets[2].tokens,0);assert.equal(result.buckets[3].tokens,20);
"""
        node(script, timezone='America/New_York')

    def test_collector_paths_resolve_inside_widget_and_preserve_override(self):
        source = (WIDGET / 'refresh/UsageRefresh.qml').read_text()
        expression = re.search(
            r'    readonly property string collectorPath: ([\s\S]+?)\n    readonly property var collectorCommand:',
            source).group(1).strip()
        script = '''const assert=require('node:assert/strict');
let override='';
const Quickshell={env:name=>name==='RYOKU_AI_USAGE_COLLECTOR'?override:'/fixture/home'};
const Qt={resolvedUrl:name=>'file:///fixture/widget%20space/'+name.replace('../','')};
const collectorPath=()=>''' + expression + ''';
const root={get collectorPath(){return collectorPath()}};
function command(){''' + binding(source, 'collectorCommand') + '''}
assert.equal(collectorPath(),'/fixture/widget space/bin/collect-usage');
assert.deepEqual(command(),[collectorPath()]);
override='/fixture/custom collector';
assert.deepEqual(command(),[collectorPath(),override]);
'''
        node(script)
        self.assertNotIn('ryoku-host', source)
        for file in (WIDGET / 'UsageModel.qml', WIDGET / 'components/AgentAvailability.qml'):
            self.assertIn('"/.cache/ai-usage"', file.read_text())

    def test_bundle_collects_both_tools_without_system_collectors(self):
        fixture, bundle, env = self.bundle_fixture()
        contract = self.fixture('contract')
        self.addCleanup(contract.WORK.cleanup)
        self.assertEqual(contract.main(), 0)
        env['OPENCODE_DATA_DIR'] = str(Path(contract.WORK.name) / 'opencode')
        tools = fixture.home / 'tools'
        tools.mkdir()
        marker = fixture.home / 'wrong-system-collector'
        for name in ('opencode-usage', 'codex-usage', 'ryoku-host'):
            stub = tools / name
            stub.write_text('#!/usr/bin/env python3\nfrom pathlib import Path\n'
                            + 'Path(' + repr(str(marker)) + ').write_text("wrong")\nraise SystemExit(99)\n')
            stub.chmod(0o755)
        env['PATH'] = str(tools) + os.pathsep + os.environ['PATH']
        legacy = fixture.home / '.cache/codex-usage.json'
        legacy.parent.mkdir(exist_ok=True)
        legacy.write_text('{"_source":"old-system","5h-utilization":"0.08"}')
        subprocess.run([str(bundle / 'bin/collect-usage')], env=env, check=True,
                       capture_output=True, text=True, timeout=15)
        private = fixture.home / '.cache/ai-usage'
        codex = json.loads((private / 'codex-usage.json').read_text())
        fixture.assert_totals(codex)
        self.assertEqual(codex['_windows'][0]['utilization'], 0.25)
        self.assertEqual(codex['_spending']['kind'], 'api-equivalent')
        opencode = json.loads((private / 'opencode-usage.json').read_text())
        self.assertGreater(opencode['_today_tokens'], 0)
        self.assertTrue(opencode['_sessions'])
        self.assertEqual(json.loads(legacy.read_text())['_source'], 'old-system')
        self.assertFalse((fixture.home / '.cache/codex-usage.json.lock').exists())
        self.assertFalse(marker.exists())
        self.assertFalse((fixture.home / 'injected').exists())

    def test_bundle_ignores_system_collector_lock(self):
        fixture, bundle, env = self.bundle_fixture()
        lock = fixture.home / '.cache/codex-usage.json.lock'
        lock.parent.mkdir(exist_ok=True)
        cache = fixture.home / '.cache/ai-usage/codex-usage.json'
        with lock.open('w') as handle:
            handle.write('system-owned lock')
            handle.flush()
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            subprocess.run([str(bundle / 'bin/collect-usage')], env=env, check=True,
                           capture_output=True, timeout=15)
            fixture.assert_totals(json.loads(cache.read_text()))
        self.assertEqual(lock.read_text(), 'system-owned lock')
        self.assertFalse((fixture.home / '.cache/codex-usage.json').exists())

    def test_direct_bundled_collectors_default_to_private_caches(self):
        fixture, bundle, env = self.bundle_fixture()
        contract = self.fixture('contract')
        self.addCleanup(contract.WORK.cleanup)
        self.assertEqual(contract.main(), 0)
        env['OPENCODE_DATA_DIR'] = str(Path(contract.WORK.name) / 'opencode')
        env.pop('CODEX_USAGE_CACHE_FILE', None)
        env.pop('CODEX_USAGE_ACTIVITY_FILE', None)
        for tool in ('opencode', 'codex'):
            subprocess.run([str(bundle / 'bin' / (tool + '-usage'))], env=env, check=True,
                           capture_output=True, timeout=15)
            self.assertTrue((fixture.home / '.cache/ai-usage' / (tool + '-usage.json')).is_file())
            self.assertFalse((fixture.home / '.cache' / (tool + '-usage.json')).exists())
        self.assertTrue((fixture.home / '.cache/ai-usage/codex-usage-activity.json').is_file())
        self.assertFalse((fixture.home / '.cache/codex-usage.json.lock').exists())

    @unittest.skipUnless(shutil.which('qs'), 'Quickshell required for bootstrap runtime check')
    def test_model_bootstraps_collection_without_existing_cache(self):
        fixture, bundle, env = self.bundle_fixture()
        contract = self.fixture('contract')
        self.addCleanup(contract.WORK.cleanup)
        self.assertEqual(contract.main(), 0)
        env['OPENCODE_DATA_DIR'] = str(Path(contract.WORK.name) / 'opencode')
        shutil.copy2(bundle / 'components/AgentAvailability.qml', fixture.home / 'AgentAvailability.qml')
        page = (WIDGET / 'IrisCompact.qml').read_text()
        reconcile = function(page, 'reconcileAgent').replace('{', '''{
        const CustomWidgets={setConfigValue:(id,key,value)=>{root.tool=value;}};''', 1)
        start = page.index('    Connections {\n        target: availability')
        connections = page[start:page.index('\n    }', start) + len('\n    }')]
        runtime = fixture.home / 'runtime'
        runtime.mkdir(mode=0o700)
        qml = fixture.home / 'shell.qml'
        qml.write_text('''import QtQuick
import Quickshell
ShellRoot {
    id: root
    property string tool: "codex"
    property bool _fallbackWritten: false
    readonly property var usageModel: model.item
    readonly property var agentOptions: [
        {value:"opencode",available:availability.opencode},
        {value:"codex",available:availability.codex}].filter(option=>option.available)
    readonly property bool hasAnyAgent: agentOptions.length > 0
    readonly property bool toolAvailable: agentOptions.some(option=>option.value===tool)
    readonly property bool agentSwitchable: availability.ready && agentOptions.length > 1
    QtObject { id: agentMenu; property bool open: false }
    readonly property string activeTool: {''' + binding(page, 'activeTool') + '''
    }
    AgentAvailability { id: availability }
''' + reconcile + '\n' + connections + '''
    Loader { id: model; source: ''' + json.dumps((bundle / 'UsageModel.qml').as_uri()) + '''
        onLoaded: {
            item.tool = Qt.binding(()=>root.activeTool)
            item.collected.connect(()=>availability.reloadAll())
        }
    }
    Timer { interval: 100; running: true; repeat: true; onTriggered: {
        if (availability.opencode && availability.codex && root.tool !== "codex") {
            console.log("BUNDLED-BOOTSTRAP-FAIL saved agent changed"); Qt.quit();
        }
        if (availability.opencode && availability.codex && model.item?.has && model.item?.tool === "codex" && model.item?.plan === "plus") {
            console.log("BUNDLED-BOOTSTRAP-PASS", model.item.today); Qt.quit();
        }
    } }
    Timer { interval: 8000; running: true; onTriggered: { console.log("BUNDLED-BOOTSTRAP-FAIL"); Qt.quit() } }
}''')
        lock_path = fixture.home / '.cache/ai-usage/codex-usage.json.lock'
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            release = threading.Timer(0.9, lambda: fcntl.flock(lock, fcntl.LOCK_UN))
            release.start()
            try:
                result = subprocess.run(['qs', '-p', str(qml)], capture_output=True, text=True, timeout=12,
                                        env=dict(env, XDG_RUNTIME_DIR=str(runtime),
                                                 QT_QPA_PLATFORM='offscreen', QS_DISABLE_CRASH_HANDLER='1'))
            finally:
                release.cancel()
                release.join()
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn('BUNDLED-BOOTSTRAP-PASS 3000', output)
        self.assertNotIn('BUNDLED-BOOTSTRAP-FAIL', output)
        self.assertNotIn('ReferenceError', output)
        self.assertNotIn('TypeError', output)

    def test_trends_and_heatmap_fixed_calendar_windows(self):
        page = (WIDGET / 'IrisCompact.qml').read_text()
        activity = (WIDGET / 'components/AiUsageActivityCard.qml').read_text()
        script = SETUP + function(page, 'historyWeight') + '\n' + function(activity, 'dayWeight')
        script += '\nfunction trend() {\n' + binding(page, 'trend') + '\n}'
        script += '\nfunction heatmap() {\n' + binding(activity, 'map') + '\n}'
        script += '''
const usageModel = {days:[], hours:[]}, usage = usageModel;
const root = {hourly:false, periodDays:7, historyWeight};
const card = {dayWeight};
for (const date of [[2026,2,8],[2026,10,1],[2026,10,7]]) {
    clock = new RealDate(...date, 12).getTime();
    for (let weekday=0; weekday<7; weekday++) {
        clock += 86400000;
        const today = new Date();
        const yesterday = new Date(clock); yesterday.setDate(yesterday.getDate()-1);
        usage.days = [{date:Qt.formatDate(yesterday),tokens:2,cacheRead:3},
            {date:Qt.formatDate(today),tokens:7,cacheRead:11}];
        for (const count of [7,30,45]) {
            root.periodDays = count === 45 ? 0 : count;
            const result = trend();
            assert.equal(result.buckets.length,count);
            assert.equal(result.buckets.at(-1).date,Qt.formatDate(today));
            assert.equal(result.total,23);
            assert.equal(result.buckets.filter(x=>x.tokens===0).length,count-2);
        }
        const map = heatmap();
        assert.equal(map.weeks.length,9);
        assert(map.weeks.every(week=>week.length===7 && week.every(Boolean)));
        const cells=map.weeks.flat();
        assert.equal(new Set(cells.map(x=>x.date)).size,63);
        assert.equal(cells.at(-1).date,Qt.formatDate(today));
        const start=new Date(clock);start.setDate(start.getDate()-62);
        assert.equal(cells[0].date,Qt.formatDate(start));
        assert.equal(cells.filter(x=>x.value===0).length,61);
        assert.equal(map.active,2);
    }
}
usage.days=[];
assert.deepEqual(heatmap().weeks,[]);
'''
        for timezone in ('Asia/Kolkata', 'America/New_York'):
            node(script, timezone)

    def test_cache_hours_normalize_both_units(self):
        source = (WIDGET / 'UsageModel.qml').read_text()
        names = ('empty', 'pct', 'normalizeWindows', 'shortName', 'normalizePeriods', 'kmg', 'updateFreshness', 'parse')
        script = SETUP + '\n'.join(function(source, name) for name in names)
        script += '\nconst root = {' + ','.join(names) + '}; const switchTimer={stop(){}};'
        script += '''
for (const start of [1794054600,1794054600000]) {
    root.parse(JSON.stringify({_hours:[{start,tokens:10,cacheRead:20}]}),clock/1000);
    assert.equal(root.hours[0].start,1794054600000);
    assert.equal(root.hours[0].tokens+root.hours[0].cacheRead,30);
}
'''
        node(script)

    def test_agent_fallback_uses_only_supported_available_tools(self):
        source = (WIDGET / 'IrisCompact.qml').read_text()
        script = SETUP + '\nfunction activeTool() {\n' + binding(source, 'activeTool') + '\n}'
        script += '''
const availability={ready:true};
const root={tool:'claude',hasAnyAgent:false,toolAvailable:false,agentOptions:[]};
for (const open of [false,true]) for (const codex of [false,true]) {
    root.agentOptions=[...(open?[{value:'opencode'}]:[]),...(codex?[{value:'codex'}]:[])];
    root.hasAnyAgent=root.agentOptions.length>0;
    for (const tool of ['claude','opencode','codex']) {
        root.tool=tool;
        root.toolAvailable=root.agentOptions.some(x=>x.value===tool);
        const expected=root.toolAvailable?tool:root.agentOptions[0]?.value??'opencode';
        assert.equal(activeTool(),expected);
    }
}
'''
        node(script)

    def test_tile_reads_its_model_and_actual_quota_window(self):
        source = (WIDGET / 'AiUsageTile.qml').read_text()
        expression = re.search(r'        StyledText \{\n            text: (.*?)\n            font \{',
                               source, re.S).group(1)
        script = SETUP + '\nfunction metric() { return (' + expression + '); }'
        script += '''
const root={};
const usage={has:false,hasPlan:false,windows:[],today:123,kmg:n=>String(n)};
assert.equal(metric(),'-');
usage.has=true;
assert.equal(metric(),'123 tokens today');
usage.hasPlan=true;
usage.windows=[{pct:48,label:'30d'}];
assert.equal(metric(),'48% · 30d');
usage.windows=[];
assert.equal(metric(),'123 tokens today');
'''
        node(script)

    def test_estimated_spending_for_plan_agents_checks_month_and_coverage(self):
        source = (WIDGET / 'IrisCompact.qml').read_text()
        script = SETUP + '\nfunction monthly() {\n' + binding(source, 'monthly') + '\n}'
        script += '\nfunction spendHelp() {\n' + binding(source, 'spendHelp') + '\n}'
        script += '''
const root={activeTool:'codex',monthLabel:()=>'Nov'};
const usageModel={plan:'plus',days:[{date:'2026-11-07',cost:99}],spending:{
    kind:'api-equivalent',month:'2026-11',amount:1.23,partial:true,price_date:'2026-11-07'}};
root.monthly=monthly();
assert.equal(root.monthly.current,1.23);
assert.equal(root.monthly.available,true);
assert.equal(root.monthly.partial,true);
assert(spendHelp().includes('Not a bill'));
assert(spendHelp().includes('Plus'));
root.activeTool='claude';
assert.equal(monthly().current,1.23);
assert.equal(monthly().available,true);
assert(spendHelp().includes('Local Claude Code history only'));
assert(spendHelp().includes('pricing data'));
root.activeTool='codex';
usageModel.spending.amount=null;
assert.equal(monthly().available,false);
usageModel.spending.amount=NaN;
assert.equal(monthly().available,false);
usageModel.spending.amount=1.23;
usageModel.spending.month='2026-10';
assert.equal(monthly().available,false);
root.activeTool='opencode';
assert.equal(monthly().current,99);
assert.equal(monthly().available,undefined);
'''
        node(script)

    def test_claude_fast_refresh_keeps_other_collectors_idle(self):
        fixture, bundle, env = self.bundle_fixture()
        config=fixture.home/'claude'
        (config/'projects').mkdir(parents=True)
        env['CLAUDE_CONFIG_DIR']=str(config)
        env['CLAUDE_USAGE_STATE_DIR']=str(fixture.home/'state/ai-usage')
        # Codex remains importable as the shared schema library, but invoking
        # its main entry point fails this test before any RPC starts.
        codex=bundle/'bin/codex-usage'
        source=codex.read_text()
        source=source.replace('if __name__ == "__main__":',
            'if __name__ == "__main__":\n    raise RuntimeError("unexpected Codex collection")',1)
        codex.write_text(source)
        subprocess.run([str(bundle/'bin/collect-usage'),'--claude-only'], env=env,
                       check=True,capture_output=True,text=True,timeout=10)
        private=fixture.home/'.cache/ai-usage'
        self.assertTrue((private/'claude-usage.json').exists())
        self.assertFalse((private/'codex-usage.json').exists())
        self.assertFalse((private/'opencode-usage.json').exists())

    def test_claude_stale_limits_do_not_become_current_zero_windows(self):
        source=(WIDGET/'UsageModel.qml').read_text()
        names=('empty','pct','normalizeWindows','shortName','normalizePeriods','kmg','updateFreshness','parse')
        script=SETUP+'\n'.join(function(source,name) for name in names)
        script+='\nconst root={'+','.join(names)+'}; const switchTimer={stop(){}};'
        script+='''
root.parse(JSON.stringify({_plan:'pro',_windows:[],_quota:{stale:true,observed_at:1794218814,
    last_known_windows:[{minutes:300,utilization:.18,reset:0},{minutes:10080,utilization:.5,reset:0}]}}),clock/1000);
assert.deepEqual(root.windows,[]);
assert.equal(root.quota.stale,true);
assert.deepEqual(root.normalizeWindows({_windows:root.quota.last_known_windows}).map(x=>x.pct),[18,50]);
root.parse(JSON.stringify({_windows:[],_quota:{available:false}}),clock/1000);
assert.deepEqual(root.windows,[]);
assert.equal(root.quota.available,false);
'''
        node(script)

    @unittest.skipUnless(shutil.which('qs') and (IMPORTS / 'inir').exists(),
                         'Quickshell and Ryoku imports required for component compilation')
    def test_real_qml_components_compile_without_starting_services(self):
        with tempfile.TemporaryDirectory(prefix='ai-usage-qml-') as directory:
            work = Path(directory)
            for name in ('home', 'config', 'cache', 'runtime'):
                (work / name).mkdir(mode=0o700)
            for name in ('inir', 'shell', 'stage'):
                if (IMPORTS / name).exists():
                    (work / name).symlink_to(IMPORTS / name, target_is_directory=True)
            paths = [str(IMPORTS), str(Path.home() / '.local/lib/qt6/qml')]
            if SHIPPED.exists():
                (work / 'Ryoku').mkdir()
                (work / 'Ryoku/Ui').symlink_to(ROOT / 'ryoku/ui', target_is_directory=True)
            targets = list(WIDGET.rglob('*.qml'))
            platform = os.environ.get('AI_USAGE_QML_PLATFORM', 'offscreen')
            if SHIPPED.exists():
                targets.append(ROOT / 'ryoku/shell/quickshell/inir/services/CustomWidgets.qml')
                if platform == 'wayland':
                    targets.append(ROOT / 'ryoku/shell/quickshell/inir/modules/background/widgets/WidgetManagerPanel.qml')
            uris = json.dumps([path.as_uri() for path in targets])
            (work / 'shell.qml').write_text('''import QtQuick
import Quickshell
ShellRoot {
 Timer { interval: 50; running: true; onTriggered: {
    let failures=0;
    for (const path of ''' + uris + ''') {
        const component=Qt.createComponent(path, Component.PreferSynchronous);
        if (component.status!==Component.Ready) {
            console.log('FAIL:',path,component.errorString()); failures++;
        }
    }
    console.log(failures ? 'AI-USAGE-COMPILE-FAIL' : 'AI-USAGE-COMPILE-PASS');
    Qt.quit();
 } }
}''')
            env = dict(os.environ, HOME=str(work / 'home'), XDG_CONFIG_HOME=str(work / 'config'),
                       XDG_CACHE_HOME=str(work / 'cache'), XDG_STATE_HOME=str(work / 'state'),
                       XDG_RUNTIME_DIR=str(work / 'runtime'), QT_QPA_PLATFORM=platform,
                       QML_IMPORT_PATH=os.pathsep.join([str(work)] + paths),
                       QML2_IMPORT_PATH=os.pathsep.join([str(work)] + paths),
                       QS_DISABLE_CRASH_HANDLER='1')
            if platform == 'wayland':
                display = Path(os.environ.get('WAYLAND_DISPLAY', 'wayland-0'))
                if not display.is_absolute():
                    display = Path(os.environ['XDG_RUNTIME_DIR']) / display
                env['WAYLAND_DISPLAY'] = str(display)
            result = subprocess.run(['qs', '-p', str(work / 'shell.qml')], env=env,
                                    capture_output=True, text=True, timeout=20)
            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn('AI-USAGE-COMPILE-PASS', output)
            self.assertNotIn('FAIL:', output)


if __name__ == '__main__':
    unittest.main(verbosity=2)
