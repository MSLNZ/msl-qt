from .scanner import Scanner
# from .scope_selector import ScopeSelector


class Injections(object):

    def __init__(self, grammar, **injections):
        self.grammar = grammar

        self.injections = []
        self.scanners = {}
        for selector, value in injections.items():
            if not value and not value.pattern:
                continue
            patterns = []
            for regex in value.patterns:
                pattern = self.grammar.createPattern(regex)
                patterns.extend(pattern.getIncludedPatterns(grammar, patterns))
            self.injections.append({
                'selector': None,  # ScopeSelector(selector),
                'patterns': patterns,
            })

    # def __repr__(self):
    #     s = []
    #     for item in sorted(vars(self)):
    #         if item == 'grammar':
    #             val = self.grammar.__class__.__name__ + '[' + self.grammar.name + ']'
    #         else:
    #             val = str(getattr(self, item))
    #         s.append(item + ': ' + val)
    #     return self.__class__.__name__ + ' { ' + ', '.join(s) + ' }'

    def getScanner(self, injection):
        if injection:
            return injection.scanner
        scanner = Scanner(injection['patterns'])
        injection.scanner = scanner
        return scanner

    def getScanners(self, ruleStack):
        if not self.injections:
            return []

        scanners = []
        scopes = self.grammar.scopesFromStack(ruleStack)
        for injection in self.injections:
            if not injection.selector.matches(scopes):
                continue
            scanner = self.getScanner(injection)
            scanners.append(scanner)
        return scanners
