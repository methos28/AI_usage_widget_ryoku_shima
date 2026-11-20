"""Check optional editor tooling with portable user and checkout paths."""
from pathlib import Path
import runpy
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
command = runpy.run_path(str(ROOT/'tools/lsp.py'))['command']


class LanguageServerTest(unittest.TestCase):
    def test_servers_resolve_from_another_users_home(self):
        with tempfile.TemporaryDirectory(prefix='lsp-home-') as directory:
            home = Path(directory)/'another user'
            folder = home/'.local/bin'
            folder.mkdir(parents=True)
            for name in ('pyright-langserver', 'vscode-json-language-server', 'bash-language-server'):
                binary = folder/name
                binary.write_text('#!/bin/sh\nexit 0\n')
                binary.chmod(0o755)
            for language, name, arg in [('python','pyright-langserver','--stdio'),
                                        ('json','vscode-json-language-server','--stdio'),
                                        ('bash','bash-language-server','start')]:
                self.assertEqual(command(language, path='', home=home), [str(folder/name), arg])

    def test_qml_imports_follow_the_selected_checkout_without_shell_expansion(self):
        with tempfile.TemporaryDirectory(prefix='lsp-qml-') as directory:
            home = Path(directory)
            binary = home/'qmlls'
            binary.write_text('#!/bin/sh\nexit 0\n')
            binary.chmod(0o755)
            imports = str(home/'QML checkout with spaces')
            self.assertEqual(command('qml', path=str(home), home=home, qml_imports=imports),
                             [str(binary), '--no-cmake-calls', '-I', imports])


if __name__ == '__main__':
    unittest.main(verbosity=2)
