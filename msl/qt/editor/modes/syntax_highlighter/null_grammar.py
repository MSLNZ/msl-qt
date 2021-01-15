from .grammar import Grammar


class NullGrammar(Grammar):

    def __init__(self, registry):
        options = {
            'name': 'Null Grammar',
            'scopeName': 'text.plain.null-grammar'
        }
        super(NullGrammar, self).__init__(registry, **options)

    def getScore(self):
        return 0
