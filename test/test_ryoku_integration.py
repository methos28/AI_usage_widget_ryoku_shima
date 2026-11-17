"""Run the optional shared-host check against an explicitly selected checkout."""
import os
from pathlib import Path
import unittest

from test_widget import binding, node


@unittest.skipUnless(os.environ.get('RYOKU_TEST_SOURCE'), 'Set RYOKU_TEST_SOURCE for the shared-host check')
class RyokuIntegrationTest(unittest.TestCase):
    def test_non_island_user_copy_does_not_hide_bundled_module(self):
        source=(Path(os.environ['RYOKU_TEST_SOURCE'])/'ryoku/shell/quickshell/inir/services/CustomWidgets.qml').read_text()
        script='''const assert=require('node:assert/strict');
const root={widgets:[{id:'ai-usage',irisQmlPath:''}],
shippedWidgets:[{id:'ai-usage',irisBuiltin:true,irisQmlPath:'bundled/IrisCompact.qml'}]};
function modules(){'''+binding(source,'irisModules')+'''}
assert.equal(modules().length,1);
assert.equal(modules()[0].irisQmlPath,'bundled/IrisCompact.qml');
root.widgets[0].irisQmlPath='custom/IrisCompact.qml';
assert.equal(modules().length,1);
assert.equal(modules()[0].irisQmlPath,'custom/IrisCompact.qml');
root.shippedWidgets[0].irisBuiltin=false;root.widgets=[];
assert.deepEqual(modules(),[]);
'''
        node(script)


if __name__=='__main__':
    unittest.main(verbosity=2)
