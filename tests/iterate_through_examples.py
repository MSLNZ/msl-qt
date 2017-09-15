"""
Run each example script one at a time.
"""
from msl.qt.prompt import question
import msl.examples.qt as ex

examples = [
    ex.equipment.configuration_viewer.show,
    ex.button.show,
    ex.equipment.message_based.show,
    ex.logger.show,
    ex.toggle_switch.show,
    ex.LoopExample,
    ex.ShowStandardIcons,
]

count = 1
n = len(examples)
for e in examples:
    e()
    if n-count > 0 and not question('{} examples remain.\nContinue?'.format(n-count)):
        break
    count += 1
