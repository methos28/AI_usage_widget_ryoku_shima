#!/usr/bin/env python3
"""Resolve optional editor language servers without user-specific paths."""
import os
from pathlib import Path
import shutil
import sys

SERVERS = {
    'qml': ('qmlls', ['--no-cmake-calls']),
    'python': ('pyright-langserver', ['--stdio']),
    'json': ('vscode-json-language-server', ['--stdio']),
    'bash': ('bash-language-server', ['start']),
}


def command(language, *, path=None, home=None, qml_imports=None):
    name, arguments = SERVERS[language]
    home = Path(home or Path.home())
    search = os.pathsep.join([path if path is not None else os.environ.get('PATH', ''),
                              str(home/'.local/bin'), str(home/'.npm-global/bin')])
    binary = shutil.which(name, path=search)
    if binary is None and language == 'qml':
        for candidate in ('/usr/lib/qt6/bin/qmlls', '/usr/lib64/qt6/bin/qmlls'):
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                binary = candidate
                break
    if binary is None:
        raise FileNotFoundError(f'{name} is not installed; see docs/continuing-development.md')
    result = [binary, *arguments]
    if language == 'qml':
        imports = qml_imports or os.environ.get('RYOKU_QML_IMPORTS') or str(home/'.config/quickshell')
        result.extend(['-I', imports])
    return result


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in SERVERS:
        raise SystemExit('usage: python3 tools/lsp.py qml|python|json|bash')
    try:
        argv = command(sys.argv[1])
    except FileNotFoundError as error:
        raise SystemExit(str(error))
    os.execv(argv[0], argv)
