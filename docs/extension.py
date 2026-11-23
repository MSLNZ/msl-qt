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

    check_state = griffe.Class(
        name="CheckState",
        docstring=griffe.Docstring(
            "Binding to the [CheckState](https://doc.qt.io/qt-6/qt.html#CheckState-enum) enum "
            "(via [PySide6][PySide6.QtCore.Qt.CheckState] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtcore/qt.html#CheckState))."
        ),
    )
    qt_namespace.set_member(check_state.name, check_state)

    alignment_flag = griffe.Class(
        name="AlignmentFlag",
        docstring=griffe.Docstring(
            "Binding to the [AlignmentFlag](https://doc.qt.io/qt-6/qt.html#AlignmentFlag-enum) enum "
            "(via [PySide6][PySide6.QtCore.Qt.AlignmentFlag] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtcore/qt.html#AlignmentFlag))."
        ),
    )
    qt_namespace.set_member(alignment_flag.name, alignment_flag)

    global_color = griffe.Class(
        name="GlobalColor",
        docstring=griffe.Docstring(
            "Binding to the [GlobalColor](https://doc.qt.io/qt-6/qt.html#GlobalColor-enum) enum "
            "(via [PySide6][PySide6.QtCore.Qt.GlobalColor] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtcore/qt.html#GlobalColor))."
        ),
    )
    qt_namespace.set_member(global_color.name, global_color)

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

    q_size = griffe.Class(
        name="QSize",
        docstring=griffe.Docstring(
            "Binding to the [QSize](https://doc.qt.io/qt-6/qsize.html) class "
            "(via [PySide6][PySide6.QtCore.QSize] or [PyQt6][PyQt6.QtCore.QSize])."
        ),
    )
    qt_core.set_member(q_size.name, q_size)


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

    weight = griffe.Class(
        name="Weight",
        docstring=griffe.Docstring(
            "Binding to the [Weight](https://doc.qt.io/qt-6/qfont.html#Weight-enum) enum "
            "(via [PySide6][PySide6.QtGui.QFont.Weight] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtgui/qfont.html#Weight))."
        ),
    )
    q_font.set_member(weight.name, weight)

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

    q_rgba_64 = griffe.Class(
        name="QRgba64",
        docstring=griffe.Docstring(
            "Binding to the [QRgba64](https://doc.qt.io/qt-6/qrgba64.html) class "
            "(via [PySide6][PySide6.QtGui.QRgba64] or [PyQt6][PyQt6.QtGui.QRgba64])."
        ),
    )
    qt_gui.set_member(q_rgba_64.name, q_rgba_64)


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

    q_file_dialog = griffe.Class(
        name="QFileDialog",
        docstring=griffe.Docstring(
            "Binding to the [QFileDialog](https://doc.qt.io/qt-6/qfiledialog.html) class "
            "(via [PySide6][PySide6.QtWidgets.QFileDialog] or [PyQt6][PyQt6.QtWidgets.QFileDialog])."
        ),
    )
    qt_widgets.set_member(q_file_dialog.name, q_file_dialog)

    option = griffe.Class(
        name="Option",
        docstring=griffe.Docstring(
            "Binding to the [Option](https://doc.qt.io/qt-6/qfiledialog.html#Option-enum) enum "
            "(via [PySide6][PySide6.QtWidgets.QFileDialog.Option] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtwidgets/qfiledialog.html#Option))."
        ),
    )
    q_file_dialog.set_member(option.name, option)

    q_line_edit = griffe.Class(
        name="QLineEdit",
        docstring=griffe.Docstring(
            "Binding to the [QLineEdit](https://doc.qt.io/qt-6/qlineedit.html) class "
            "(via [PySide6][PySide6.QtWidgets.QLineEdit] or [PyQt6][PyQt6.QtWidgets.QLineEdit])."
        ),
    )
    qt_widgets.set_member(q_line_edit.name, q_line_edit)

    text_changed = griffe.Function(
        name="textChanged",
        docstring=griffe.Docstring(
            "Binding to the [textChanged](https://doc.qt.io/qt-6/qlineedit.html#textChanged) function "
            "(via [PySide6][PySide6.QtWidgets.QLineEdit.textChanged] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtwidgets/qlineedit.html#textChanged))."
        ),
        parameters=griffe.Parameters(
            griffe.Parameter(
                "text",
                annotation=griffe.ExprName("str"),
            ),
        ),
    )
    q_line_edit.set_member(text_changed.name, text_changed)

    echo_mode = griffe.Class(
        name="EchoMode",
        docstring=griffe.Docstring(
            "Binding to the [EchoMode](https://doc.qt.io/qt-6/qlineedit.html#EchoMode-enum) enum "
            "(via [PySide6][PySide6.QtWidgets.QLineEdit.EchoMode] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtwidgets/qlineedit.html#EchoMode))."
        ),
    )
    q_line_edit.set_member(echo_mode.name, echo_mode)

    q_abstract_button = griffe.Class(
        name="QAbstractButton",
        docstring=griffe.Docstring(
            "Binding to the [QAbstractButton](https://doc.qt.io/qt-6/qabstractbutton.html) class "
            "(via [PySide6][PySide6.QtWidgets.QAbstractButton] or [PyQt6][PyQt6.QtWidgets.QAbstractButton])."
        ),
    )
    qt_widgets.set_member(q_abstract_button.name, q_abstract_button)

    toggled = griffe.Function(
        name="toggled",
        docstring=griffe.Docstring(
            "Binding to the [toggled](https://doc.qt.io/qt-6/qabstractbutton.html#toggled) function "
            "(via [PySide6][PySide6.QtWidgets.QAbstractButton.toggled] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtwidgets/qabstractbutton.html#toggled))."
        ),
        parameters=griffe.Parameters(
            griffe.Parameter(
                "checked",
                annotation=griffe.ExprName("bool"),
            ),
        ),
    )
    q_abstract_button.set_member(toggled.name, toggled)

    q_checkbox = griffe.Class(
        name="QCheckBox",
        docstring=griffe.Docstring(
            "Binding to the [QCheckBox](https://doc.qt.io/qt-6/qcheckbox.html) class "
            "(via [PySide6][PySide6.QtWidgets.QCheckBox] or [PyQt6][PyQt6.QtWidgets.QCheckBox])."
        ),
    )
    qt_widgets.set_member(q_checkbox.name, q_checkbox)

    check_state_changed = griffe.Function(
        name="checkStateChanged",
        docstring=griffe.Docstring(
            "Binding to the [checkStateChanged](https://doc.qt.io/qt-6/qcheckbox.html#checkStateChanged) function "
            "(via [PySide6][PySide6.QtWidgets.QCheckBox.checkStateChanged] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtwidgets/qcheckbox.html#checkStateChanged))."
        ),
        parameters=griffe.Parameters(
            griffe.Parameter(
                "state",
                annotation=griffe.ExprName("CheckState", parent="msl.qt.binding.QtCore.Qt"),
            ),
        ),
    )
    q_checkbox.set_member(check_state_changed.name, check_state_changed)

    q_combobox = griffe.Class(
        name="QComboBox",
        docstring=griffe.Docstring(
            "Binding to the [QComboBox](https://doc.qt.io/qt-6/qcombobox.html) class "
            "(via [PySide6][PySide6.QtWidgets.QComboBox] or [PyQt6][PyQt6.QtWidgets.QComboBox])."
        ),
    )
    qt_widgets.set_member(q_combobox.name, q_combobox)

    current_index_changed = griffe.Function(
        name="currentIndexChanged",
        docstring=griffe.Docstring(
            "Binding to the [currentIndexChanged](https://doc.qt.io/qt-6/qcombobox.html#currentIndexChanged) function "
            "(via [PySide6][PySide6.QtWidgets.QComboBox.currentIndexChanged] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtwidgets/qcombobox.html#currentIndexChanged))."
        ),
        parameters=griffe.Parameters(
            griffe.Parameter(
                "index",
                annotation=griffe.ExprName("int"),
            ),
        ),
    )
    q_combobox.set_member(current_index_changed.name, current_index_changed)

    current_text_changed = griffe.Function(
        name="currentTextChanged",
        docstring=griffe.Docstring(
            "Binding to the [currentTextChanged](https://doc.qt.io/qt-6/qcombobox.html#currentTextChanged) function "
            "(via [PySide6][PySide6.QtWidgets.QComboBox.currentTextChanged] or [PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/api/qtwidgets/qcombobox.html#currentTextChanged))."
        ),
        parameters=griffe.Parameters(
            griffe.Parameter(
                "text",
                annotation=griffe.ExprName("str"),
            ),
        ),
    )
    q_combobox.set_member(current_text_changed.name, current_text_changed)
