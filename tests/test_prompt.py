from __future__ import annotations

from msl.qt.prompt import _get_file_filters  # pyright: ignore[reportPrivateUsage]


def test_get_file_filters() -> None:
    assert _get_file_filters(None) == "All Files (*)"
    assert _get_file_filters("") == "All Files (*)"
    assert _get_file_filters([]) == "All Files (*)"
    assert _get_file_filters({}) == "All Files (*)"

    assert _get_file_filters("Text files (*.txt)") == "Text files (*.txt)"
    assert _get_file_filters(["Text files (*.txt)"]) == "Text files (*.txt)"
    assert _get_file_filters({"Text files": "*.txt"}) == "Text files (*.txt)"
    assert _get_file_filters({"Text files": ("*.txt",)}) == "Text files (*.txt)"
    assert _get_file_filters({"Text files": "txt"}) == "Text files (*.txt)"
    assert _get_file_filters({"Text files": ".txt"}) == "Text files (*.txt)"
    assert _get_file_filters({"Text files": "test*.txt"}) == "Text files (test*.txt)"

    assert _get_file_filters("ABC files (abc*)") == "ABC files (abc*)"
    assert _get_file_filters({"ABC files": "abc*"}) == "ABC files (abc*)"

    assert (
        _get_file_filters({"Data files": ("txt", ".xml", "*.csv", "my*.hdf5")})
        == "Data files (*.txt *.xml *.csv my*.hdf5)"
    )

    f1 = {"Data files": ("txt", "ab*.xml", "*.csv", "my*.hdf5"), "XML files": "xml"}
    assert _get_file_filters(f1) == "Data files (*.txt ab*.xml *.csv my*.hdf5);;XML files (*.xml)"

    f2 = {"Data files": "m*.xml", "All files": "*"}
    assert _get_file_filters(f2) == "Data files (m*.xml);;All files (*)"

    assert _get_file_filters("Image files (*.png);;") == "Image files (*.png)"

    assert (
        _get_file_filters("Image files (*.png *.jpg);;Text files (*.txt)")
        == "Image files (*.png *.jpg);;Text files (*.txt)"
    )

    assert (
        _get_file_filters(["Image files (*.png *.jpg)", "Text files (*.txt)"])
        == "Image files (*.png *.jpg);;Text files (*.txt)"
    )
