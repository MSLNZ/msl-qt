"""
A :func:`~msl.qt.prompt.comments` example.
"""
import os
import json
import random
import datetime
import tempfile

from msl import qt

adjectives = ['purple', 'pink', 'loud', 'quiet', 'big', 'small', 'blue', 'electric', 'wooden', 'scented']
nouns = ['house', 'man', 'cat', 'dog', 'door', 'parrot', 'lady', 'plant', 'kettle', 'urn', 'football']
verbs = ['jumped', 'slept', 'ate', 'meowed', 'ran', 'walked', 'jogged', 'talked', 'whispered', 'cried']
adverbs = ['loudly', 'quietly', 'quickly', 'slowly', 'softly', 'gingerly', 'carefully', 'magically']
prepositions = ['after', 'before', 'in', 'to', 'on', 'with', 'without', 'next to', 'by']


def show():
    dummy = [
        {'timestamp': (datetime.datetime.now() + datetime.timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S'),
         'comment': 'The {} {} {} {} {} the {}'.format(
             *map(random.choice, (adjectives, nouns, verbs, adverbs, prepositions, nouns)))}
        for i in range(1000)
    ]

    dummy_file = os.path.join(tempfile.gettempdir(), 'msl-qt-comments-example.json')
    with open(dummy_file, 'w') as fp:
        json.dump(dummy, fp, indent=2, ensure_ascii=False)

    comment = qt.prompt.comments(path=dummy_file)
    print('The comment entered is: {!r}'.format(comment))

    os.remove(dummy_file)


if __name__ == '__main__':
    show()
