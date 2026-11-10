"""Custom hook to change `msl.qt._qt` cross-reference targets to `PySide6`."""  # noqa: INP001


def on_page_content(html: str, **_: object) -> str:
    """Change `msl.qt._qt` cross-reference targets to `PySide6`.

    See https://www.mkdocs.org/dev-guide/plugins/#on_page_content
    """
    if html:
        replacements = [
            ("msl.qt._qt.SignalInstance", "PySide6.QtCore.Signal"),  # SignalInstance not in objects.inv
            ("msl.qt._qt.Signal", "PySide6.QtCore.Signal"),
            ("msl.qt._qt", "PySide6"),
        ]

        for old, new in replacements:
            html = html.replace(old, new)

    return html
