"""
Run each example script one at a time.
"""
import os
import sys
from inspect import getmembers, isfunction

if 'QT_API' not in os.environ:
    os.environ['QT_API'] = 'PySide6' if sys.version_info.minor > 5 else 'PySide2'

from msl import qt
import msl.examples.qt as example

print('Using {}'.format(qt.binding))

examples = [
    example.comments.show,
    example.button.show,
    example.logger.show,
    example.toggle_switch.show,
    example.loop_until_abort.main,
    example.loop_until_abort_sleep.main,
    example.ShowStandardIcons,
    example.led.show,
]

for name, item in getmembers(qt.prompt, isfunction):
    if name.startswith('_') or name in ['application', 'to_qfont']:
        continue

    if name in ['comments', 'filename', 'folder', 'save']:
        examples.append(item)
    elif name == 'item':
        examples.append(lambda message=name, fcn=item: fcn(message, items=[1, 2, 3]))
    else:
        examples.append(lambda message=name, fcn=item: fcn(message))

n = len(examples)
for i, example in enumerate(examples, start=1):
    example()
    if i < n and not qt.prompt.yes_no('{} examples remain.\nContinue?'.format(n-i)):
        break
