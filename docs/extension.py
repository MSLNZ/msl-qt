"""Modifies the documentation for the Qt modules."""  # noqa: INP001

# cSpell: ignore griffe
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, override

import griffe

if TYPE_CHECKING:
    from ast import AST
    from typing import Any


class QtExtension(griffe.Extension):
    """Modifies the documentation for the Qt modules."""

    @override
    def on_module_members(  # noqa: PLR0915
        self,
        *,
        node: AST | griffe.ObjectNode,
        mod: griffe.Module,
        agent: griffe.Visitor | griffe.Inspector,
        **kwargs: Any,
    ) -> None:
        """Dynamically generate the Qt references when the docs are built.

        See https://mkdocstrings.github.io/griffe/reference/api/extensions/#griffe.Extension.on_module_members
        """
        if mod.path != "msl.qt.binding":
            return

        qt_core = griffe.Module(
            name="QtCore",
            filepath=Path("QtCore.py"),
            docstring=griffe.Docstring("Binding to the [Qt Core](https://doc.qt.io/qt-6/qtcore-index.html) module."),
        )

        qt_gui = griffe.Module(
            name="QtGui",
            docstring=griffe.Docstring("Binding to the [Qt GUI](https://doc.qt.io/qt-6/qtgui-index.html) module."),
        )

        qt_svg = griffe.Module(
            name="QtSvg",
            docstring=griffe.Docstring("Binding to the [Qt SVG](https://doc.qt.io/qt-6/qtsvg-index.html) module."),
        )

        qt_widgets = griffe.Module(
            name="QtWidgets",
            docstring=griffe.Docstring(
                "Binding to the [Qt Widgets](https://doc.qt.io/qt-6/qtwidgets-index.html) module."
            ),
        )

        qt_namespace = griffe.Module(
            name="Qt",
            docstring=griffe.Docstring("Binding to the [Qt](https://doc.qt.io/qt-6/qt.html) namespace."),
        )
        qt_core.set_member(qt_namespace.name, qt_namespace)

        q_byte_array = griffe.Class(
            name="QByteArray",
            docstring=griffe.Docstring("Binding to the [QByteArray](https://doc.qt.io/qt-6/qbytearray.html) class."),
        )
        qt_core.set_member(q_byte_array.name, q_byte_array)

        q_signal = griffe.Class(
            name="Signal",
            docstring=griffe.Docstring("Either the [PySide6.QtCore.Signal][] or [PyQt6.QtCore.pyqtSignal][] class."),
        )
        qt_core.set_member(q_signal.name, q_signal)

        q_signal_instance = griffe.Class(
            name="SignalInstance",
            docstring=griffe.Docstring("An instance of a [Signal][msl.qt.binding.QtCore.Signal]."),
        )
        qt_core.set_member(q_signal_instance.name, q_signal_instance)

        q_slot = griffe.Class(
            name="Slot",
            docstring=griffe.Docstring(
                "Either the [PySide6.QtCore.Slot][] or [PyQt6.QtCore.pyqtSlot](https://www.riverbankcomputing.com/static/Docs/PyQt6/signals_slots.html#PyQt6.QtCore.pyqtSlot) class."  # noqa: E501
            ),
        )
        qt_core.set_member(q_slot.name, q_slot)

        q_property = griffe.Class(
            name="Property",
            docstring=griffe.Docstring(
                "Either the [PySide6.QtCore.Property][] or [PyQt6.QtCore.pyqtProperty][] class."
            ),
        )
        qt_core.set_member(q_property.name, q_property)

        q_thread = griffe.Class(
            name="QThread",
            docstring=griffe.Docstring("Binding to the [QThread](https://doc.qt.io/qt-6/qthread.html) class."),
        )
        qt_core.set_member(q_thread.name, q_thread)

        q_timer = griffe.Class(
            name="QTimer",
            docstring=griffe.Docstring("Binding to the [QTimer](https://doc.qt.io/qt-6/qtimer.html) class."),
        )
        qt_core.set_member(q_timer.name, q_timer)

        q_icon = griffe.Class(
            name="QIcon",
            docstring=griffe.Docstring("Binding to the [QIcon](https://doc.qt.io/qt-6/qicon.html) class."),
        )
        qt_gui.set_member(q_icon.name, q_icon)

        q_image = griffe.Class(
            name="QImage",
            docstring=griffe.Docstring("Binding to the [QImage](https://doc.qt.io/qt-6/qimage.html) class."),
        )
        qt_gui.set_member(q_image.name, q_image)

        q_pixmap = griffe.Class(
            name="QPixmap",
            docstring=griffe.Docstring("Binding to the [QPixmap](https://doc.qt.io/qt-6/qpixmap.html) class."),
        )
        qt_gui.set_member(q_pixmap.name, q_pixmap)

        q_font = griffe.Class(
            name="QFont",
            docstring=griffe.Docstring("Binding to the [QFont](https://doc.qt.io/qt-6/qfont.html) class."),
        )
        qt_gui.set_member(q_font.name, q_font)

        q_color = griffe.Class(
            name="QColor",
            docstring=griffe.Docstring("Binding to the [QColor](https://doc.qt.io/qt-6/qcolor.html) class."),
        )
        qt_gui.set_member(q_color.name, q_color)

        q_image_writer = griffe.Class(
            name="QImageWriter",
            docstring=griffe.Docstring(
                "Binding to the [QImageWriter](https://doc.qt.io/qt-6/qimagewriter.html) class."
            ),
        )
        qt_gui.set_member(q_image_writer.name, q_image_writer)

        q_dialog = griffe.Class(
            name="QDialog",
            docstring=griffe.Docstring("Binding to the [QDialog](https://doc.qt.io/qt-6/qdialog.html) class."),
        )
        qt_widgets.set_member(q_dialog.name, q_dialog)

        q_application = griffe.Class(
            name="QApplication",
            docstring=griffe.Docstring(
                "Binding to the [QApplication](https://doc.qt.io/qt-6/qapplication.html) class."
            ),
        )
        qt_widgets.set_member(q_application.name, q_application)

        q_message_box = griffe.Class(
            name="QMessageBox",
            docstring=griffe.Docstring("Binding to the [QMessageBox](https://doc.qt.io/qt-6/qmessagebox.html) class."),
        )
        qt_widgets.set_member(q_message_box.name, q_message_box)

        q_main_window = griffe.Class(
            name="QMainWindow",
            docstring=griffe.Docstring("Binding to the [QMainWindow](https://doc.qt.io/qt-6/qmainwindow.html) class."),
        )
        qt_widgets.set_member(q_main_window.name, q_main_window)

        q_label = griffe.Class(
            name="QLabel",
            docstring=griffe.Docstring("Binding to the [QLabel](https://doc.qt.io/qt-6/qlabel.html) class."),
        )
        qt_widgets.set_member(q_label.name, q_label)

        q_style = griffe.Class(
            name="QStyle",
            docstring=griffe.Docstring("Binding to the [QStyle](https://doc.qt.io/qt-6/qstyle.html) class."),
        )
        qt_widgets.set_member(q_style.name, q_style)

        standard_pixmap = griffe.Class(
            name="StandardPixmap",
            docstring=griffe.Docstring(
                "Binding to the [StandardPixmap](https://doc.qt.io/qt-6/qstyle.html#StandardPixmap-enum) enum."
            ),
        )
        q_style.set_member(standard_pixmap.name, standard_pixmap)

        mod.set_member("QtCore", qt_core)
        mod.set_member("QtGui", qt_gui)
        mod.set_member("QtSvg", qt_svg)
        mod.set_member("QtWidgets", qt_widgets)
