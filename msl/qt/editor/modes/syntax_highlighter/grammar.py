import sys

from .injections import Injections
from .rule import Rule
from .pattern import Pattern
from .... import QtCore


class Grammar(object):

    Infinity = sys.maxsize

    def __init__(self, registry, **options):
        self.registry = registry

        self.name = options['name']
        self.scopeName = options['scopeName']

        self.repository = None
        self.initialRule = None
        self.includedGrammarScopes = []

        self.fileTypes = options.get('fileTypes', [])
        self.foldingStopMarker = options.get('foldingStopMarker')
        self.maxTokensPerLine = options.get('maxTokensPerLine', Grammar.Infinity)
        self.maxLineLength = options.get('maxLineLength', Grammar.Infinity)
        self.rawPatterns = options.get('patterns', [])
        self.rawRepository = options.get('repository', {})

        self.injectionSelector = None
        if options.get('injectionSelector'):
            raise NotImplementedError('injectionSelector is not currently supported')
            # from .scope_selector import ScopeSelector
            # self.injectionSelector = ScopeSelector(options['injectionSelector'])

        try:
            self.firstLineRegex = QtCore.QRegularExpression(options['firstLineMatch'])
        except KeyError:
            self.firstLineRegex = None

        self.injections = Injections(self, **options.get('injections', {}))

    # def __repr__(self):
    #     space = ' '
    #     s = [self.__class__.__name__  + ' {']
    #     for item in sorted(vars(self)):
    #         obj = getattr(self, item)
    #         if item == 'registry':
    #             s.append(space*2 + item + ': ' + obj.__class__.__name__)
    #         else:
    #             s.append(space*2 + item + ': ' + str(obj))
    #     s.append('}')
    #     return '\n'.join(s)

    def tokenizeLines(self, text, compatibilityMode=True):
        lines = text.splitlines()
        lastLine = len(lines) - 1
        ruleStack = []
        results = []
        for lineNumber, line in enumerate(lines):
            result = self.tokenizeLine(line, ruleStack, lineNumber == 0, compatibilityMode, lineNumber != lastLine)
            results.append(result)
            ruleStack = result.ruleStack
        return results

    def tokenizeLine(self, inputLine, ruleStack=None, firstLine=False, compatibilityMode=True, appendNewLine=True):
        tags = []

        truncatedLine = False
        if len(inputLine) > self.maxLineLength:
            line = inputLine[0:self.maxLineLength]
            truncatedLine = True
        else:
            line = inputLine

        openScopeTags = []
        string = line  # OnigString
        stringWithNewLine = line + '\n' if appendNewLine else line  # OnigString

        if ruleStack:
            ruleStack = ruleStack[:]
            if compatibilityMode:
                openScopeTags = []
                for rule in ruleStack:
                    scopeName = rule['scopeName']
                    contentScopeName = rule['contentScopeName']
                    if scopeName:
                        openScopeTags.append(self.registry.startIdForScope(scopeName))
                    if contentScopeName:
                        openScopeTags.append(self.registry.startIdForScope(contentScopeName))
        else:
            if compatibilityMode:
                openScopeTags = []
            initialRule = self.getInitialRule()
            ruleStack = [{
                'rule': initialRule,
                'scopeName': initialRule.scopeName,
                'contentScopeName': initialRule.contentScopeName
            }]
            if initialRule.scopeName:
                tags.append(self.startIdForScope(initialRule.scopeName))
            if initialRule.contentScopeName:
                tags.append(self.startIdForScope(initialRule.contentScopeName))

        initialRuleStackLength = len(ruleStack)
        position = 0
        tokenCount = 0
        popStack = None

        while True:
            previousRuleStackLength = len(ruleStack)
            previousPosition = position

            if position > len(line):
                break

            if tokenCount >= self.getMaxTokensPerLine() - 1:
                truncatedLine = True
                break

            match = ruleStack[-1]['rule'].getNextTags(ruleStack, string, stringWithNewLine, position, firstLine)
            if match:
                nextTags = match['nextTags']
                tagsStart = match['tagsStart']
                tagsEnd = match['tagsEnd']

                # Unmatched text before next tags
                if position < tagsStart:
                    tags.append(tagsStart - position)
                    tokenCount += 1

                tags.extend(nextTags)
                for tag in nextTags:
                    if tag:
                        tokenCount += 1

                position = tagsEnd

            else:
                # Push filler token for unmatched text at end of line
                if position < len(line) or len(line) == 0:
                    tags.append(len(line) - position)
                break

            if position == previousPosition:
                if len(ruleStack) is previousRuleStackLength:
                    print("Popping rule because it loops at column {} of line '{}' ruleStack:{}".format(position, line, ruleStack))
                    if len(ruleStack) > 1:
                        rule = ruleStack.pop()
                        scopeName = rule['scopeName']
                        contentScopeName = rule['contentScopeName']
                        if contentScopeName:
                            tags.append(self.endIdForScope(contentScopeName))
                        if scopeName:
                            tags.append(self.endIdForScope(scopeName))
                    else:
                        if position < len(line) or (len(line) == 0 and len(tags) == 0):
                            tags.append(line.length - position)
                        break
                elif len(ruleStack) > previousRuleStackLength:  # Stack size increased with zero length match
                    _ref3 = ruleStack[-2:]
                    _ref4 = _ref3[0]
                    penultimateRule = _ref4['rule']
                    _ref5 = _ref3[1]
                    lastRule = _ref5['rule']

                    # Same exact rule was pushed but position wasn't advanced
                    if lastRule and lastRule == penultimateRule:
                        popStack = True

                    # Rule with same scope name as previous rule was pushed but position wasn't advanced
                    if lastRule and lastRule.scopeName and penultimateRule.scopeName == lastRule.scopeName:
                        popStack = True

                    if popStack:
                        ruleStack.pop()
                        lastSymbol = tags[-1]
                        if lastSymbol < 0 and lastSymbol is self.startIdForScope(lastRule.scopeName):
                            tags.pop()  # also pop the duplicated start scope if it was pushed
                        tags.append(len(line) - position)
                        break

        if truncatedLine:
            tagCount = len(tags)
            if tags[tagCount - 1] > 0:
                tags[tagCount - 1] += len(inputLine) - position
            else:
                tags.append(len(inputLine) - position)
            while len(ruleStack) > initialRuleStackLength:
                rule = ruleStack.pop()
                scopeName = rule['scopeName']
                contentScopeName = rule['contentScopeName']
                if contentScopeName:
                    tags.append(self.endIdForScope(contentScopeName))
                if scopeName:
                    tags.append(self.endIdForScope(scopeName))

        for rule in ruleStack:
            rule['rule'].clearAnchorPosition()

        if compatibilityMode:
            return TokenizeLineResult(inputLine, openScopeTags, tags, ruleStack, self.registry)
        else:
            return {'line': inputLine, 'tags': tags, 'ruleStack': ruleStack}

    def activate(self):
        self.registration = self.registry.addGrammar(self)

    def deactivate(self):
        # @emitter = new Emitter
        # @registration?.dispose()
        self.registration = None

    def clearRules(self):
        self.initialRule = None
        self.repository = None

    def getInitialRule(self):
        if self.initialRule:
            return self.initialRule
        self.initialRule = self.createRule(**{
            'scopeName': self.scopeName,
            'patterns': self.rawPatterns
        })
        return self.initialRule

    def getRepository(self):
        if self.repository:
            return self.repository

        self.repository = {}
        for name, data in self.rawRepository.items():
            if data.get('begin') or data.get('match'):
                data = {
                    'patterns': [data],
                    'tempName': name
                }
            self.repository[name] = self.createRule(**data)
        return self.repository

    def addIncludedGrammarScope(self, scope):
        if scope not in self.includedGrammarScopes:
            return self.includedGrammarScopes.append(scope)

    def grammarUpdated(self, scopeName):
        if not scopeName in self.includedGrammarScopes:
            return False
        self.clearRules()
        self.registry.grammarUpdated(self.scopeName)
        #@emit 'grammar-updated' if Grim.includeDeprecatedAPIs
        #@emitter.emit 'did-update'
        return True

    def startIdForScope(self, scope):
        return self.registry.startIdForScope(scope)

    def endIdForScope(self, scope):
        return self.registry.endIdForScope(scope)

    def scopeForId(self, id_):
        return self.registry.scopeForId(id_)

    def createRule(self, **options):
        return Rule(self, self.registry, **options)

    def createPattern(self, **options):
        return Pattern(self, self.registry, **options)

    def getMaxTokensPerLine(self):
        return self.maxTokensPerLine

    def scopesFromStack(self, stack, rule, endPatternMatch):
        scopes = []
        for item in stack:
            scopeName = item['scopeName']
            contentScopeName = item['contentScopeName']
            if scopeName:
                scopes.append(scopeName)
            if contentScopeName:
                scopes.append(contentScopeName)

        # Pop the last content name scope if the end pattern at the top of the stack
        # was matched since only text between the begin/end patterns should have the
        # content name scope
        if endPatternMatch and rule and rule['contentScopeName'] and rule is stack[len(stack) - 1]:
          scopes.pop()

        return scopes


class TokenizeLineResult(object):

    def __init__(self, line, openScopeTags, tags, ruleStack, registry):
        self.line = line
        self.openScopeTags = openScopeTags
        self.tags = tags
        self.ruleStack = ruleStack
        self.registry = registry
        self.tokens = self.registry.decodeTokens(line, tags, openScopeTags)
