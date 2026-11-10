"""Example to show the [comment][msl.qt.prompt.comment] prompt."""

from __future__ import annotations

import json
import random
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from msl.qt import prompt

adjectives = ["purple", "pink", "loud", "quiet", "big", "small", "blue", "electric", "wooden", "scented"]
nouns = ["house", "man", "cat", "dog", "door", "parrot", "lady", "plant", "kettle", "urn", "football"]
verbs = ["jumped", "slept", "ate", "meowed", "ran", "walked", "jogged", "talked", "whispered", "cried"]
adverbs = ["loudly", "quietly", "quickly", "slowly", "softly", "gingerly", "carefully", "magically"]
prepositions = ["after", "before", "in", "to", "on", "with", "without", "next to", "by"]


def show() -> None:
    """Create some random comments then show the prompt."""
    dummy = [
        {
            "timestamp": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "comment": "The {} {} {} {} {} the {}".format(
                *map(random.choice, (adjectives, nouns, verbs, adverbs, prepositions, nouns))
            ),
        }
        for i in range(1000)
    ]

    dummy_file = Path(tempfile.gettempdir()) / "msl-qt-comments-example.json"
    with dummy_file.open("w") as fp:
        json.dump(dummy, fp, indent=2, ensure_ascii=False)

    comment = prompt.comment(path=dummy_file)
    print(f"The comment is {comment!r}")

    dummy_file.unlink()


if __name__ == "__main__":
    show()
