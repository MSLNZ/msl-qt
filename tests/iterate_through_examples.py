"""
Run each example script one at a time.
"""
from msl import qt
import msl.examples.qt as example

examples = [
    example.loop_until_abort_sleep.main,
    example.notes_history.show,
    example.equipment.configuration_viewer.show,
    example.button.show,
    example.equipment.message_based.show,
    example.logger.show,
    example.toggle_switch.show,
    example.loop_until_abort.main,
    example.ShowStandardIcons,
]

count = 1
n = len(examples)
for run in examples:
    run()
    if n-count > 0 and not qt.prompt.question('{} examples remain.\nContinue?'.format(n-count)):
        break
    count += 1
