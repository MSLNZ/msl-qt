class OnigScanner(object):

    def __init__(self, patterns):
        self.patterns = patterns

    def findNextMatchSync(self, line, position):
        bestLocation = 0
        bestResult = None
        bestIndex = None
        for index, pattern in enumerate(self.patterns):
            result = pattern.match(line, offset=position)
            if result.hasMatch():
                location = result.capturedStart()
                if bestResult is None or location < bestLocation:
                    bestLocation = location
                    bestResult = result
                    bestIndex = index
                if location == position:
                    break

        if not bestResult:
            return None

        results = dict((('index', bestIndex), ('scanner', self)))
        results['captureIndices'] = []
        for index in range(len(bestResult.capturedTexts())):
            results['captureIndices'].append({
                'index': index,
                'start': max(0, bestResult.capturedStart(index)),
                'end': max(0, bestResult.capturedEnd(index)),
                'length': bestResult.capturedLength(index),
            })
        return results
