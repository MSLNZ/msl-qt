from .... import QtCore

AllCustomCaptureIndicesRegex = QtCore.QRegularExpression(r'\$(\d+)|\${(\d+):\/(downcase|upcase)}')  # use matchGlobal
AllDigitsRegex = QtCore.QRegularExpression(r'\\\d+')  # use matchGlobal
DigitRegex = QtCore.QRegularExpression(r'\\\d+')


class Pattern(object):

    def __init__(self, grammar, registry, **options):
        self.grammar = grammar
        self.registry = registry

        self.pushRule = None
        self.backReferences = None
        self.captures = None
        self.regexSource = None

        match = options.get('match')
        begin = options.get('begin')
        end = options.get('end')
        patterns = options.get('patterns')
        captures = options.get('captures')
        beginCaptures = options.get('beginCaptures')
        endCaptures = options.get('endCaptures')
        applyEndPatternLast = options.get('applyEndPatternLast')

        self.scopeName = options.get('name')
        self.include = options.get('include')
        self.popRule = options.get('popRule')
        self.hasBackReferences = options.get('hasBackReferences')
        self.contentScopeName = options.get('contentName')

        if match:
            if not self.hasBackReferences:
                self.hasBackReferences = DigitRegex.match(match).hasMatch()
            if (end or self.popRule) and self.hasBackReferences:
                self.match = match
            else:
                self.regexSource = match
            self.captures = captures
        elif begin:
            self.regexSource = begin
            self.captures = beginCaptures if beginCaptures else captures
            endPattern = self.grammar.createPattern(**{
                'match': end,
                'captures': endCaptures if endCaptures else captures,
                'popRule': True
            })
            self.pushRule = self.grammar.createRule(**{
                'scopeName': self.scopeName,
                'contentScopeName': self.contentScopeName,
                'patterns': patterns,
                'endPattern': endPattern,
                'applyEndPatternLast': applyEndPatternLast
            })

        if self.captures:
            for group, capture in self.captures.items():
                if capture and capture.get('pattern') and not capture.get('rule'):
                    capture.scopeName = self.scopeName
                    capture.rule = self.grammar.createRule(capture)

        self.anchored = self.hasAnchor()

    # def __repr__(self):
    #     space = ' '
    #     s = [self.__class__.__name__  + ' {']
    #     for item in sorted(vars(self)):
    #         obj = getattr(self, item)
    #         if item == 'registry':
    #             s.append(space*2 + item + ': ' + obj.__class__.__name__)
    #         elif item == 'grammar':
    #             s.append(space*2 + item + ': ' + obj.__class__.__name__ + '[' + obj.name + ']')
    #         else:
    #             s.append(space*2 + item + ': ' + str(obj))
    #     s.append('}')
    #     return '\n'.join(s)

    def getRegex(self, firstLine, position, anchorPosition):
        if self.anchored:
            return self.replaceAnchor(firstLine, position, anchorPosition)
        else:
            return self.regexSource

    def hasAnchor(self):
        if not self.regexSource:
            return False
        escape = False
        for character in self.regexSource:
            if escape and (character == 'A' or character == 'G' or character == 'z'):
                return True
            escape = not escape and character == '\\'
        return False

    def replaceAnchor(self, firstLine, offset, anchor):
        escaped = []
        placeholder = '\uFFFF'
        escape = False
        for character in self.regexSource:
            if escape:
                if character == 'A':
                    if firstLine:
                        escaped.append('\\' + character)
                    else:
                        escaped.append(placeholder)
                elif character == 'G':
                    if offset == anchor:
                        escaped.append('\\' + character)
                    else:
                        escaped.append(placeholder)
                elif character == 'z':
                    escaped.append('$(?!\n)(?<!\n)')
                else:
                    escaped.append('\\' + character)
                escape = False
            elif character == '\\':
                escape = True
            else:
                escaped.append(character)
        return ''.join(escaped)

    def resolveBackReferences(self, line, beginCaptureIndices):
        beginCaptures = []

        for index in beginCaptureIndices:
            beginCaptures.append(line[index['start']:index['end']])

        resolvedMatch = self.match
        match_iter = AllDigitsRegex.globalMatch(self.match)
        while match_iter.hasNext():
            result = match_iter.next().captured()
            index = int(result[1:])
            if beginCaptures[index]:
                val = QtCore.QRegularExpression.escape(beginCaptures[index])
            else:
                val = "\\" + str(index)
            resolvedMatch = resolvedMatch.replace(result, val)

        return self.grammar.createPattern(**{
            'hasBackReferences': False,
            'match': resolvedMatch,
            'captures': self.captures,
            'popRule': self.popRule
        })

    def ruleForInclude(self, baseGrammar, name):
        hashIndex = name.find('#')
        if hashIndex == 0:
            return self.grammar.getRepository()[name[1:]]
        elif hashIndex >= 1:
            grammarName = name[0:hashIndex-1]
            ruleName = name[hashIndex+1:]
            self.grammar.addIncludedGrammarScope(grammarName)
            _ref = self.registry.grammarForScopeName(grammarName)
            if _ref:
                return _ref.getRepository()[ruleName]
            else:
                return None
        elif name == '$self':
            return self.grammar.getInitialRule()
        elif name == '$base':
            return baseGrammar.getInitialRule()
        else:
            self.grammar.addIncludedGrammarScope(name)
            _ref1 = self.registry.grammarForScopeName(name)
            if _ref1:
                return _ref1.getInitialRule()
            else:
                return None

    def getIncludedPatterns(self, baseGrammar, included):
        if self.include:
            rule = self.ruleForInclude(baseGrammar, self.include)
            if rule:
                return rule.getIncludedPatterns(baseGrammar, included)
            else:
                return []
        else:
            return [self]

    def resolveScopeName(self, scopeName, line, captureIndices):
        resolvedScopeName = scopeName
        match_iter = AllCustomCaptureIndicesRegex.globalMatch(scopeName)
        while match_iter.hasNext():
            raise NotImplementedError
        # return resolvedScopeName = scopeName.replace(AllCustomCaptureIndicesRegex, function(match, index, commandIndex, command) {
        #     var capture, replacement;
        #     capture = captureIndices[parseInt(index != null ? index : commandIndex)];
        #     if (capture != null) {
        #       replacement = line.substring(capture.start, capture.end);
        #       while (replacement[0] === '.') {
        #         replacement = replacement.substring(1);
        #       }
        #       switch (command) {
        #         case 'downcase':
        #           return replacement.toLowerCase();
        #         case 'upcase':
        #           return replacement.toUpperCase();
        #         default:
        #           return replacement;
        #       }
        #     } else {
        #       return match;
        #     }
        #   });
        # };
        return resolvedScopeName

    def handleMatch(self, stack, line, captureIndices, rule, endPatternMatch):
        tags = []
        scopeName = None

        zeroWidthMatch = captureIndices[0]['start'] == captureIndices[0]['end']

        if self.popRule:
            # Pushing and popping a rule based on zero width matches at the same index
            # leads to an infinite loop. We bail on parsing if we detect that case here.
            if zeroWidthMatch and stack[-1].get('zeroWidthMatch') and \
                    stack[-1]['rule'].anchorPosition == captureIndices[0]['end']:
                return False

            contentScopeName = stack[-1]['contentScopeName']
            if contentScopeName:
                tags.append(self.grammar.endIdForScope(contentScopeName))
        elif self.scopeName:
            scopeName = self.resolveScopeName(self.scopeName, line, captureIndices)
            tags.append(self.grammar.startIdForScope(scopeName))

        if self.captures:
            tags.extend(self.tagsForCaptureIndices(line, captureIndices[:], captureIndices, stack))
        else:
            start = captureIndices[0]['start']
            end = captureIndices[0]['end']
            if end != start:
                tags.append(end - start)

        if self.pushRule:
            ruleToPush = self.pushRule.getRuleToPush(line, captureIndices)
            ruleToPush.anchorPosition = captureIndices[0]['end']
            contentScopeName = ruleToPush.contentScopeName
            if contentScopeName:
                contentScopeName = self.resolveScopeName(contentScopeName, line, captureIndices)
                tags.append(self.grammar.startIdForScope(contentScopeName))
            stack.append({
                'rule': ruleToPush,
                'scopeName': scopeName,
                'contentScopeName': contentScopeName,
                'zeroWidthMatch': zeroWidthMatch
            })
        else:
            if self.popRule:
                scopeName = stack.pop()['scopeName']
            if scopeName:
                tags.append(self.grammar.endIdForScope(scopeName))

        return tags

    def tagsForCaptureRule(self, rule, line, captureStart, captureEnd, stack):
        raise NotImplementedError
        captureText = line[captureStart:captureEnd]
        tags = rule.grammar.tokenizeLine(captureText, __slice.call(stack).concat([{rule: rule}]), False, True, False).tags

        # only accept non empty tokens that don't exceed the capture end
        openScopes = []
        captureTags = []
        offset = 0
        for tag in tags:
            if tag < 0 or (tag > 0 and offset < captureEnd):
                continue
            captureTags.append(tag)
            if tag >= 0:
                offset += tag
            else:
                if tag % 2 == 0:
                    openScopes.pop()
                else:
                    openScopes.append(tag)

        # close any scopes left open by matching this rule since we don't pass our stack
        while len(openScopes) > 0:
            captureTags.append(openScopes.pop() - 1)

        return captureTags

    def tagsForCaptureIndices(self, line, currentCaptureIndices, allCaptureIndices, stack):
        parentCapture = currentCaptureIndices.pop(0)
        parentCaptureScope = None

        tags = []
        scope = self.captures.get(str(parentCapture['index']))
        if scope and scope.get('name'):
            parentCaptureScope = self.resolveScopeName(scope['name'], line, allCaptureIndices)
            tags.append(self.grammar.startIdForScope(parentCaptureScope))

        captureRule = self.captures.get(str(parentCapture['index']))
        if captureRule and captureRule.get('rule'):
            captureTags = self.tagsForCaptureRule(captureRule['rule'], line, parentCapture['start'], parentCapture['end'], stack)
            tags.extend(captureTags)
            # Consume child captures
            while len(currentCaptureIndices) and currentCaptureIndices[0]['start'] < parentCapture['end']:
                currentCaptureIndices.pop(0)
        else:
            previousChildCaptureEnd = parentCapture['start']
            while len(currentCaptureIndices) and currentCaptureIndices[0]['start'] < parentCapture['end']:
                childCapture = currentCaptureIndices[0]

                emptyCapture = childCapture['end'] - childCapture['start'] == 0
                captureHasNoScope = not self.captures.get(str(childCapture['index']))
                if emptyCapture or captureHasNoScope:
                    currentCaptureIndices.pop(0)
                    continue

                if childCapture['start'] > previousChildCaptureEnd:
                    tags.append(childCapture['start'] - previousChildCaptureEnd)

                captureTags = self.tagsForCaptureIndices(line, currentCaptureIndices, allCaptureIndices, stack)
                tags.extend(captureTags)
                previousChildCaptureEnd = childCapture['end']

            if parentCapture['end'] > previousChildCaptureEnd:
                tags.append(parentCapture['end'] - previousChildCaptureEnd)

        if parentCaptureScope:
            if len(tags) > 1:
                tags.append(self.grammar.endIdForScope(parentCaptureScope))
            else:
                tags.pop()

        return tags
