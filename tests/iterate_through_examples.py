"""
Run each example script one at a time.
"""
import os
os.environ['QT_API'] = 'PySide'

from msl import qt
import msl.examples.qt as example

examples = [
    example.loop_until_abort_sleep.main,
    example.comments.show,
    example.button.show,
    example.logger.show,
    example.toggle_switch.show,
    example.loop_until_abort.main,
    example.ShowStandardIcons,
    example.led.show,
]

count = 1
n = len(examples)
for run in examples:
    run()
    if n-count > 0 and not qt.prompt.yes_no('{} examples remain.\nContinue?'.format(n-count)):
        break
    count += 1
