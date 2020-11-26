from .scanner import Scanner


class Rule(object):

    def __init__(self, grammar, registry, **kwargs):
        self.grammar = grammar
        self.registry = registry
        self.scopeName = kwargs.get('scopeName')
        self.contentScopeName = kwargs.get('contentScopeName')
        self.endPattern = kwargs.get('endPattern')
        self.applyEndPatternLast = kwargs.get('applyEndPatternLast')

        self.patterns = []
        for pattern in kwargs.get('patterns', []):
            if not pattern.get('disabled'):
                self.patterns.append(self.grammar.createPattern(**pattern))

        if self.endPattern and not self.endPattern.hasBackReferences:
            if self.applyEndPatternLast:
                self.patterns.append(self.endPattern)
            else:
                self.patterns.insert(0, self.endPattern)

        self.scannersByBaseGrammarName = {}
        self.createEndPattern = None
        self.anchorPosition = -1

    # def __repr__(self):
    #     space = ' '
    #     s = [self.__class__.__name__  + ' {']
    #     for item in sorted(vars(self)):
    #         obj = getattr(self, item)
    #         if item == 'registry':
    #             s.append(space*2 + item + ': ' + obj.__class__.__name__)
    #         elif  item == 'grammar':
    #             s.append(space*2 + item + ': ' + obj.__class__.__name__ + '[' + obj.name + ']')
    #         elif item == 'patterns':
    #             s.append(space * 2 + item + ': [')
    #             for pattern in obj:
    #                 for p in str(pattern).splitlines():
    #                     s.append(space * 4 + p)
    #             s.append(space * 2 + ']')
    #         else:
    #             s.append(space*2 + item + ': ' + str(obj))
    #     s.append('}')
    #     return '\n'.join(s)

    def getIncludedPatterns(self, baseGrammar, included=None):
        if included is None:
            included = []

        if self in included:
            return []

        included = included + [self]
        allPatterns = []
        for pattern in self.patterns:
            allPatterns.extend(pattern.getIncludedPatterns(baseGrammar, included))
        return allPatterns

    def clearAnchorPosition(self):
        self.anchorPosition = -1
        return self.anchorPosition

    def getScanner(self, baseGrammar):
        scanner = self.scannersByBaseGrammarName.get(baseGrammar.name)
        if scanner:
            return scanner

        patterns = self.getIncludedPatterns(baseGrammar)
        scanner = Scanner(patterns)
        self.scannersByBaseGrammarName[baseGrammar.name] = scanner
        return scanner

    def scanInjections(self, ruleStack, line, position, firstLine):
        baseGrammar = ruleStack[0]['rule'].grammar
        if baseGrammar.injections:
            for scanner in baseGrammar.injections.getScanners(ruleStack):
                result = scanner.findNextMatch(line, firstLine, position, self.anchorPosition)
                if result:
                    return result

    def normalizeCaptureIndices(self, line, captureIndices):
        lineLength = len(line)
        for capture in captureIndices:
            capture['end'] = min(capture['end'], lineLength)
            capture['start'] = min(capture['start'], lineLength)

    def findNextMatch(self, ruleStack, lineWithNewline, position, firstLine):
        baseGrammar = ruleStack[0]['rule'].grammar
        results = []

        scanner = self.getScanner(baseGrammar)

        result = scanner.findNextMatch(lineWithNewline, firstLine, position, self.anchorPosition)
        if result:
            results.append(result)

        result = self.scanInjections(ruleStack, lineWithNewline, position, firstLine)
        if result:
            for injection in baseGrammar.injections.injections:
                if injection.scanner is result['scanner']:
                    if injection.selector.getPrefix(self.grammar.scopesFromStack(ruleStack)) == 'L':
                        for r in result[::-1]:
                            results.insert(0, r)
                    else:
                        # TODO: Prefixes can either be L, B, or R.
                        # R is assumed to mean "right", which is the default (add to end of stack).
                        # There's no documentation on B, however.
                        results.append(result)

        scopes = None
        for injectionGrammar in self.registry.injectionGrammars:
            if injectionGrammar is self.grammar:
                continue
            if injectionGrammar is baseGrammar:
                continue
            if scopes is None:
                scope = self.grammar.scopesFromStack(ruleStack)
            if injectionGrammar.injectionSelector.matches(scopes):
                scanner = injectionGrammar.getInitialRule().getScanner(injectionGrammar, position, firstLine)
                result = scanner.findNextMatch(lineWithNewline, firstLine, position, self.anchorPosition)
                if result:
                    if injectionGrammar.injectionSelector.getPrefix(scopes) == 'L':
                        for r in result[::-1]:
                            results.insert(0, r)
                    else:
                        # TODO: Prefixes can either be L, B, or R.
                        # R is assumed to mean "right", which is the default (add to end of stack).
                        # There's no documentation on B, however.
                        results.append(result)

        if len(results) > 1:
            min_index = len(results) + 1
            for r in results:
                self.normalizeCaptureIndices(lineWithNewline, r['captureIndices'])
                min_index = min(min_index, result['captureIndices'][0]['start'])
            return results[min_index]
        elif len(results) == 1:
            result = results[0]
            self.normalizeCaptureIndices(lineWithNewline, result['captureIndices'])
            return result

    def getNextTags(self, ruleStack, line, lineWithNewline, position, firstLine):
        result = self.findNextMatch(ruleStack, lineWithNewline, position, firstLine)
        if not result:
            return None

        index = result['index']
        captureIndices = result['captureIndices']
        scanner = result['scanner']
        firstCapture = captureIndices[0]
        endPatternMatch = self.endPattern == scanner.patterns[index]
        nextTags = scanner.handleMatch(result, ruleStack, line, self, endPatternMatch)
        if nextTags is not None:
            return {
                'nextTags': nextTags,
                'tagsStart': firstCapture['start'],
                'tagsEnd': firstCapture['end']
            }

    def getRuleToPush(self, line, beginPatternCaptureIndices):
        if self.endPattern.hasBackReferences:
            rule = self.grammar.createRule(**{'scopeName': self.scopeName, 'contentScopeName': self.contentScopeName})
            rule.endPattern = self.endPattern.resolveBackReferences(line, beginPatternCaptureIndices)
            rule.patterns = [rule.endPattern] + self.patterns
            return rule
        else:
            return self
