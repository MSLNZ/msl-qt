"""Examples showing the custom widgets."""

from __future__ import annotations

from typing import Callable

from . import (
    button,
    checkbox,
    combobox,
    comment,
    led,
    line_edit,
    logger,
    loop_until_abort,
    loop_until_abort_sleep,
    standard_icons,
    toggle_switch,
)

__all__: list[str] = [
    "button",
    "checkbox",
    "combobox",
    "comment",
    "led",
    "line_edit",
    "logger",
    "loop_until_abort",
    "loop_until_abort_sleep",
    "standard_icons",
    "toggle_switch",
]

mapping: dict[str, Callable[[], None]] = {
    "Button": button.show,
    "CheckBox": checkbox.show,
    "ComboBox": combobox.show,
    "Comment": comment.show,
    "LED": led.show,
    "LineEdit": line_edit.show,
    "Logger": logger.show,
    "Loop": loop_until_abort.show,
    "LoopSleep": loop_until_abort_sleep.show,
    "StandardIcons": standard_icons.show,
    "ToggleSwitch": toggle_switch.show,
}


def show(name: str = "") -> None:
    """Show an example widget."""
    fcn = mapping.get(name)
    if fcn is None:
        from msl.qt.prompt import item  # noqa: PLC0415

        msg = ""
        if name:
            msg += f"Unknown example name {name!r}\n\n"
        msg += "Select an example to run:"

        name = item(
            message=msg,
            title="Select an example",
            items=list(mapping.keys()),
        )
        if name:
            show(name)
    else:
        fcn()
