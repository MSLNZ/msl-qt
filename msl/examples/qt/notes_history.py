"""
A :func:`~msl.qt.notes_history.notes` example.
"""
import os
import json
import random
import datetime
import tempfile

from msl import qt

adjectives = ['purple','pink','loud','quiet','big','small','blue','electric','wooden','scented']
nouns = ['house','man','cat','dog','door','parrot','lady','plant','kettle','urn','football']
verbs = ['jumped','slept','ate','meowed','ran','walked','jogged','talked','whispered','cried']
adverbs = ['loudly','quietly','quickly','slowly','softly','gingerly','carefully','magically']
prepositions = ['after', 'before', 'in', 'to', 'on', 'with', 'without', 'next to', 'by']


def show():
    dummy = [
        {'timestamp': (datetime.datetime.now() + datetime.timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S'),
         'notes': 'The {} {} {} {} {} the {}'.format(
             *map(random.choice, (adjectives, nouns, verbs, adverbs, prepositions, nouns)))}
        for i in range(1000)
    ]

    dummy_file = os.path.join(tempfile.gettempdir(), 'msl-qt-notes-history-example.json')
    with open(dummy_file, 'wb') as fp:
        json.dump(dummy, fp, indent=2, ensure_ascii=False)

    print('The note entered is:\n' + qt.prompt.notes(dummy_file))
    os.remove(dummy_file)


if __name__ == '__main__':
    show()
