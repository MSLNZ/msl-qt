"""Sequentially run each example and prompt function."""

from __future__ import annotations

from functools import partial
from inspect import getmembers, isfunction

from msl.examples.qt import mapping
from msl.qt import binding, prompt


def run() -> None:
    for name, item in getmembers(prompt, isfunction):
        if name.startswith("_") or name in {"application", "screen_geometry", "to_qcolor", "to_qfont"}:
            continue

        if name in ["comment", "file", "files", "folder", "save"]:
            mapping[name] = item
        elif name == "item":
            mapping[name] = partial(item, name, items=[1, 2, 3])
        else:
            mapping[name] = partial(item, name)

    print(f"Using {binding}")  # noqa: T201
    n = len(mapping)
    for i, example in enumerate(mapping.values(), start=1):
        example()
        if not prompt.yes_no(f"{n - i} examples remain.\nContinue?"):
            break


if __name__ == "__main__":
    run()
