"""Example to show the `comment` prompt."""

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
    comments = [
        [
            (datetime.now() - timedelta(days=i)).isoformat(sep=" ", timespec="seconds"),
            "The {} {} {} {} {} the {}".format(
                *map(random.choice, (adjectives, nouns, verbs, adverbs, prepositions, nouns))
            ),
        ]
        for i in range(1000)
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = Path(tmp_dir) / "msl-qt-comments-example.json"
        with tmp_file.open("w") as fp:
            json.dump(comments, fp, indent=2, ensure_ascii=False)

        comment = prompt.comment(path=tmp_file, title="Enter a comment")
        print(f"The comment is {comment!r}")


if __name__ == "__main__":
    show()
