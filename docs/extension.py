"""Modifies the documentation for the Qt modules."""  # noqa: INP001

# cSpell: ignore griffe
# pyright: reportImplicitStringConcatenation=false
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
    def on_module_members(
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
            docstring=griffe.Docstring(
                "Binding to the [Qt Core](https://doc.qt.io/qt-6/qtcore-index.html) module "
                "(via [PySide6][PySide6.QtCore] or [PyQt6][PyQt6.QtCore])."
            ),
        )
        update_qt_core(qt_core)

        qt_gui = griffe.Module(
            name="QtGui",
            filepath=Path("QtGui.py"),
            docstring=griffe.Docstring(
                "Binding to the [Qt GUI](https://doc.qt.io/qt-6/qtgui-index.html) module "
                "(via [PySide6][PySide6.QtGui] or [PyQt6][PyQt6.QtGui])."
            ),
        )
        update_qt_gui(qt_gui)

        qt_svg = griffe.Module(
            name="QtSvg",
            filepath=Path("QtSvg.py"),
            docstring=griffe.Docstring(
                "Binding to the [Qt SVG](https://doc.qt.io/qt-6/qtsvg-index.html) module "
                "(via [PySide6][PySide6.QtSvg] or [PyQt6][PyQt6.QtSvg])."
            ),
        )
        update_qt_svg(qt_svg)

        qt_widgets = griffe.Module(
            name="QtWidgets",
            filepath=Path("QtWidgets.py"),
            docstring=griffe.Docstring(
                "Binding to the [Qt Widgets](https://doc.qt.io/qt-6/qtwidgets-index.html) module "
                "(via [PySide6][PySide6.QtWidgets] or [PyQt6][PyQt6.QtWidgets])."
            ),
        )
        update_qt_widgets(qt_widgets)

        prop = griffe.Class(
            name="Property",
            docstring=griffe.Docstring(
                "Binding to the [Q_PROPERTY](https://doc.qt.io/qt-6/properties.html) macro "
                "(via [PySide6][PySide6.QtCore.Property] or [PyQt6][PyQt6.QtCore.pyqtProperty])."
            ),
        )

        signal = griffe.Class(
            name="Signal",
            docstring=griffe.Docstring(
                "Binding to the [Signal](https://doc.qt.io/qt-6/signalsandslots.html) class "
                "(via [PySide6][PySide6.QtCore.Signal] or [PyQt6][PyQt6.QtCore.pyqtSignal])."
            ),
        )

        slot = griffe.Class(
            name="Slot",
            docstring=griffe.Docstring(
                "Binding to the [Slot](https://doc.qt.io/qt-6/signalsandslots.html) class "
                "(via [PySide6][PySide6.QtCore.Slot] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/signals_slots.html#PyQt6.QtCore.pyqtSlot))."
            ),
        )

        mod.set_member(prop.name, prop)
        mod.set_member(signal.name, signal)
        mod.set_member(slot.name, slot)
        mod.set_member(qt_core.name, qt_core)
        mod.set_member(qt_gui.name, qt_gui)
        mod.set_member(qt_svg.name, qt_svg)
        mod.set_member(qt_widgets.name, qt_widgets)


def update_qt_core(qt_core: griffe.Module) -> None:
    """Update the QtCore module."""
    qt_namespace = griffe.Module(
        name="Qt",
        filepath=Path("Qt.py"),
        docstring=griffe.Docstring(
            "Binding to the [Qt](https://doc.qt.io/qt-6/qt.html) namespace "
            "(via [PySide6][PySide6.QtCore.Qt] or [PyQt6][PyQt6.QtCore.Qt])."
        ),
    )
    qt_core.set_member(qt_namespace.name, qt_namespace)

    connection_type = griffe.Class(
        name="ConnectionType",
        docstring=griffe.Docstring(
            "Binding to the [ConnectionType](https://doc.qt.io/qt-6/qt.html#ConnectionType-enum) enum "
            "(via [PySide6][PySide6.QtCore.Qt.ConnectionType] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtcore/qt.html#ConnectionType))."
        ),
    )
    qt_namespace.set_member(connection_type.name, connection_type)

    q_byte_array = griffe.Class(
        name="QByteArray",
        docstring=griffe.Docstring(
            "Binding to the [QByteArray](https://doc.qt.io/qt-6/qbytearray.html) class "
            "(via [PySide6][PySide6.QtCore.QByteArray] or [PyQt6][PyQt6.QtCore.QByteArray])."
        ),
    )
    qt_core.set_member(q_byte_array.name, q_byte_array)

    q_thread = griffe.Class(
        name="QThread",
        docstring=griffe.Docstring(
            "Binding to the [QThread](https://doc.qt.io/qt-6/qthread.html) class "
            "(via [PySide6][PySide6.QtCore.QThread] or [PyQt6][PyQt6.QtCore.QThread])."
        ),
    )
    qt_core.set_member(q_thread.name, q_thread)

    q_timer = griffe.Class(
        name="QTimer",
        docstring=griffe.Docstring(
            "Binding to the [QTimer](https://doc.qt.io/qt-6/qtimer.html) class "
            "(via [PySide6][PySide6.QtCore.QTimer] or [PyQt6][PyQt6.QtCore.QTimer])."
        ),
    )
    qt_core.set_member(q_timer.name, q_timer)

    q_object = griffe.Class(
        name="QObject",
        docstring=griffe.Docstring(
            "Binding to the [QObject](https://doc.qt.io/qt-6/qobject.html) class "
            "(via [PySide6][PySide6.QtCore.QObject] or [PyQt6][PyQt6.QtCore.QObject])."
        ),
    )
    qt_core.set_member(q_object.name, q_object)


def update_qt_gui(qt_gui: griffe.Module) -> None:
    """Update the QtGui module."""
    q_icon = griffe.Class(
        name="QIcon",
        docstring=griffe.Docstring(
            "Binding to the [QIcon](https://doc.qt.io/qt-6/qicon.html) class "
            "(via [PySide6][PySide6.QtGui.QIcon] or [PyQt6][PyQt6.QtGui.QIcon])."
        ),
    )
    qt_gui.set_member(q_icon.name, q_icon)

    q_image = griffe.Class(
        name="QImage",
        docstring=griffe.Docstring(
            "Binding to the [QImage](https://doc.qt.io/qt-6/qimage.html) class "
            "(via [PySide6][PySide6.QtGui.QImage] or [PyQt6][PyQt6.QtGui.QImage])."
        ),
    )
    qt_gui.set_member(q_image.name, q_image)

    q_pixmap = griffe.Class(
        name="QPixmap",
        docstring=griffe.Docstring(
            "Binding to the [QPixmap](https://doc.qt.io/qt-6/qpixmap.html) class "
            "(via [PySide6][PySide6.QtGui.QPixmap] or [PyQt6][PyQt6.QtGui.QPixmap])."
        ),
    )
    qt_gui.set_member(q_pixmap.name, q_pixmap)

    q_font = griffe.Class(
        name="QFont",
        docstring=griffe.Docstring(
            "Binding to the [QFont](https://doc.qt.io/qt-6/qfont.html) class "
            "(via [PySide6][PySide6.QtGui.QFont] or [PyQt6][PyQt6.QtGui.QFont])."
        ),
    )
    qt_gui.set_member(q_font.name, q_font)

    q_color = griffe.Class(
        name="QColor",
        docstring=griffe.Docstring(
            "Binding to the [QColor](https://doc.qt.io/qt-6/qcolor.html) class "
            "(via [PySide6][PySide6.QtGui.QColor] or [PyQt6][PyQt6.QtGui.QColor])."
        ),
    )
    qt_gui.set_member(q_color.name, q_color)

    q_image_writer = griffe.Class(
        name="QImageWriter",
        docstring=griffe.Docstring(
            "Binding to the [QImageWriter](https://doc.qt.io/qt-6/qimagewriter.html) class "
            "(via [PySide6][PySide6.QtGui.QImageWriter] or [PyQt6][PyQt6.QtGui.QImageWriter])."
        ),
    )
    qt_gui.set_member(q_image_writer.name, q_image_writer)


def update_qt_svg(_: griffe.Module) -> None:
    """Update the QtSvg module."""


def update_qt_widgets(qt_widgets: griffe.Module) -> None:
    """Update the QtWidgets module."""
    q_dialog = griffe.Class(
        name="QDialog",
        docstring=griffe.Docstring(
            "Binding to the [QDialog](https://doc.qt.io/qt-6/qdialog.html) class "
            "(via [PySide6][PySide6.QtWidgets.QDialog] or [PyQt6][PyQt6.QtWidgets.QDialog])."
        ),
    )
    qt_widgets.set_member(q_dialog.name, q_dialog)

    q_application = griffe.Class(
        name="QApplication",
        docstring=griffe.Docstring(
            "Binding to the [QApplication](https://doc.qt.io/qt-6/qapplication.html) class "
            "(via [PySide6][PySide6.QtWidgets.QApplication] or [PyQt6][PyQt6.QtWidgets.QApplication])."
        ),
    )
    qt_widgets.set_member(q_application.name, q_application)

    q_message_box = griffe.Class(
        name="QMessageBox",
        docstring=griffe.Docstring(
            "Binding to the [QMessageBox](https://doc.qt.io/qt-6/qmessagebox.html) class "
            "(via [PySide6][PySide6.QtWidgets.QMessageBox] or [PyQt6][PyQt6.QtWidgets.QMessageBox])."
        ),
    )
    qt_widgets.set_member(q_message_box.name, q_message_box)

    q_main_window = griffe.Class(
        name="QMainWindow",
        docstring=griffe.Docstring(
            "Binding to the [QMainWindow](https://doc.qt.io/qt-6/qmainwindow.html) class "
            "(via [PySide6][PySide6.QtWidgets.QMainWindow] or [PyQt6][PyQt6.QtWidgets.QMainWindow])."
        ),
    )
    qt_widgets.set_member(q_main_window.name, q_main_window)

    q_label = griffe.Class(
        name="QLabel",
        docstring=griffe.Docstring(
            "Binding to the [QLabel](https://doc.qt.io/qt-6/qlabel.html) class "
            "(via [PySide6][PySide6.QtWidgets.QLabel] or [PyQt6][PyQt6.QtWidgets.QLabel])."
        ),
    )
    qt_widgets.set_member(q_label.name, q_label)

    q_style = griffe.Class(
        name="QStyle",
        docstring=griffe.Docstring(
            "Binding to the [QStyle](https://doc.qt.io/qt-6/qstyle.html) class "
            "(via [PySide6][PySide6.QtWidgets.QStyle] or [PyQt6][PyQt6.QtWidgets.QStyle])."
        ),
    )
    qt_widgets.set_member(q_style.name, q_style)

    standard_pixmap = griffe.Class(
        name="StandardPixmap",
        docstring=griffe.Docstring(
            "Binding to the [StandardPixmap](https://doc.qt.io/qt-6/qstyle.html#StandardPixmap-enum) enum "
            "(via [PySide6][PySide6.QtWidgets.QStyle.StandardPixmap] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtwidgets/qstyle.html#StandardPixmap))."
        ),
    )
    q_style.set_member(standard_pixmap.name, standard_pixmap)

    q_tool_button = griffe.Class(
        name="QToolButton",
        docstring=griffe.Docstring(
            "Binding to the [QToolButton](https://doc.qt.io/qt-6/qtoolbutton.html) class "
            "(via [PySide6][PySide6.QtWidgets.QToolButton] or [PyQt6][PyQt6.QtWidgets.QToolButton])."
        ),
    )
    qt_widgets.set_member(q_tool_button.name, q_tool_button)

    q_widget = griffe.Class(
        name="QWidget",
        docstring=griffe.Docstring(
            "Binding to the [QWidget](https://doc.qt.io/qt-6/qwidget.html) class "
            "(via [PySide6][PySide6.QtWidgets.QWidget] or [PyQt6][PyQt6.QtWidgets.QWidget])."
        ),
    )
    qt_widgets.set_member(q_widget.name, q_widget)
