from .... import QtCore
from .onig_scanner import OnigScanner


class Scanner(object):

    def __init__(self, patterns):
        # Wrapper class for {OnigScanner} that caches them based on the presence of any
        # anchor characters that change based on the current position being scanned.
        #
        # See {Pattern::replaceAnchor} for more details.
        self.patterns = patterns if patterns else []
        self.anchored = False
        for pattern in self.patterns:
            if not pattern.anchored:
                continue
            self.anchored = True
            break

        self.anchoredScanner = None
        self.firstLineAnchoredScanner = None
        self.firstLineScanner = None
        self.scanner = None

    # def __repr__(self):
    #     space = ' '
    #     s = [self.__class__.__name__ + ' {']
    #     for item in sorted(vars(self)):
    #         obj = getattr(self, item)
    #         s.append(space * 2 + item + ': ' + str(obj))
    #     s.append('}')
    #     return '\n'.join(s)

    def createScanner(self, firstLine, position, anchorPosition):
        # Create a new {OnigScanner} with the given options.
        patterns = [QtCore.QRegularExpression(pattern.getRegex(firstLine, position, anchorPosition))
                    for pattern in self.patterns]
        scanner = OnigScanner(patterns)
        return scanner

    def getScanner(self, firstLine, position, anchorPosition):
        # Get the {OnigScanner} for the given position and options.
        if not self.anchored:
            if not self.scanner:
                self.scanner = self.createScanner(firstLine, position, anchorPosition)
            return self.scanner

        if firstLine:
            if position == anchorPosition:
                if not self.firstLineAnchoredScanner:
                    self.firstLineAnchoredScanner = self.createScanner(firstLine, position, anchorPosition)
                return self.firstLineAnchoredScanner
            else:
                if not self.firstLineScanner:
                    self.firstLineScanner = self.createScanner(firstLine, position, anchorPosition)
                return self.firstLineScanner
        elif position == anchorPosition:
            if not self.anchoredScanner:
                self.anchoredScanner = self.createScanner(firstLine, position, anchorPosition)
            return self.anchoredScanner
        else:
            if not self.scanner:
                self.scanner = self.createScanner(firstLine, position, anchorPosition)
            return self.scanner

    def findNextMatch(self, line, firstLine, position, anchorPosition):
        # Public: Find the next match on the line start at the given position
        #
        # line - the string being scanned.
        # firstLine - true if the first line is being scanned.
        # position - numeric position to start scanning at.
        # anchorPosition - numeric position of the last anchored match.
        #
        # Returns an Object with details about the match or null if no match found.
        scanner = self.getScanner(firstLine, position, anchorPosition)
        match = scanner.findNextMatchSync(line, position)
        if match:
            match['scanner'] = self
        return match

    def handleMatch(self, match, stack, line, rule, endPatternMatch):
        # Public: Handle the given match by calling `handleMatch` on the
        # matched {Pattern}.
        #
        # match - An object returned from a previous call to `findNextMatch`.
        # stack - An array of {Rule} objects.
        # line - The string being scanned.
        # rule - The rule that matched.
        # endPatternMatch - true if the rule's end pattern matched.
        #
        # Returns an array of tokens representing the match.
        pattern = self.patterns[match['index']]
        return pattern.handleMatch(stack, line, match['captureIndices'], rule, endPatternMatch)
