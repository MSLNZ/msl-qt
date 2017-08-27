"""
Run each example script one at a time.
"""
from msl.qt.prompt import question
import msl.examples.qt as ex

examples = [
    ex.LoopExample,
    ex.logger.show,
    ex.toggle_switch.show,
    ex.ShowStandardIcons,
]

count = 1
n = len(examples)
for e in examples:
    e()
    if n-count > 0 and not question('{} examples remain.\nContinue?'.format(n-count)):
        break
    count += 1
