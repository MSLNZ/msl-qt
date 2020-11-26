from .grammar import Grammar


class NullGrammar(Grammar):

    def __init__(self, registry):
        options = {
            'name': 'Null Grammar',
            'scopeName': 'text.plain.null-grammar'
        }
        Grammar.__init__(self, registry, **options)

    def getScore(self):
        return 0
