import os

from msl.qt.editor.color_schemes import load
from msl.qt.editor.python import PYTHON_GRAMMAR_PATH
from msl.qt.editor.modes.syntax_highlighter.grammar_registry import GrammarRegistry
from msl.examples.qt import EXAMPLES_DIR

data = load('Chromodynamics')

styles = dict()
styles['globals'] = dict()
styles['scopes'] = dict()
for setting in data['settings']:
    if 'name' not in setting:
        styles['globals'] = setting['settings']
    else:
        if ',' in setting['scope']:
            for scope in setting['scope'].split(','):
                styles['scopes'][scope.strip()] = setting['settings']
        elif ' ' in setting['scope']:
            for scope in setting['scope'].split(' '):
                styles['scopes'][scope.strip()] = setting['settings']
        else:
            styles['scopes'][setting['scope']] = setting['settings']

for name, color in styles['globals'].items():
    print(name, color)
for scope, style in styles['scopes'].items():
    print(scope, style)


def get_style_from_scopes(scopes):
    for scope in scopes[::-1]:
        while True:
            style = styles['scopes'].get(scope)
            if style:
                return scope, style
            scope, ext = os.path.splitext(scope)
            if not ext:
                break
    return styles['scopes'].get('source', '#000000')


print(get_style_from_scopes(['source', 'variable.f', 'd.try.nope.namespace.joe.b']))


registry = GrammarRegistry()
grammar = registry.loadGrammarSync(PYTHON_GRAMMAR_PATH)

scopes = set()


def get_all_scopes(obj):
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, (list, dict)):
                get_all_scopes(item)
        return

    if not isinstance(obj, dict):
        assert False

    if 'name' in obj:
        for scope in obj['name'].split():
            scopes.add(scope)

    for key, value in obj.items():
        if key == 'name':
            for scope in value.split():
                scopes.add(scope)
        if isinstance(value, (list, dict)):
            get_all_scopes(value)


get_all_scopes(grammar.rawRepository)

with open(os.path.join(EXAMPLES_DIR, 'editor_sample.py')) as fp:
    source = fp.read()

tokens = grammar.tokenizeLines(source)
for token in tokens:
    for item in token:
        print('{:25s} : {} : {} '.format(item['value'].strip(), ', '.join(item['scopes']), get_style_from_scopes(item['scopes'])))
