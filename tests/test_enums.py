import pytest

from msl.qt import Qt
from msl.qt import QtGui
from msl.qt import QtWidgets


@pytest.mark.parametrize('style', (QtWidgets.QStyle, QtWidgets.QCommonStyle))
def test_qstyle(style):
    assert style.State_None == style.StateFlag.State_None
    assert style.PE_PanelButtonCommand == style.PrimitiveElement.PE_PanelButtonCommand
    assert style.CE_PushButton == style.ControlElement.CE_PushButton
    assert style.SE_PushButtonContents == style.SubElement.SE_PushButtonContents
    assert style.CC_SpinBox == style.ComplexControl.CC_SpinBox
    assert style.SC_None == style.SubControl.SC_None
    assert style.PM_ButtonIconSize == style.PixelMetric.PM_ButtonIconSize
    assert style.CT_CheckBox == style.ContentsType.CT_CheckBox
    assert style.RSIP_OnMouseClick == style.RequestSoftwareInputPanel.RSIP_OnMouseClick
    assert style.SH_EtchDisabledText == style.StyleHint.SH_EtchDisabledText
    assert style.SP_TrashIcon == style.StandardPixmap.SP_TrashIcon


def test_qt():
    assert Qt.AlignmentFlag.AlignLeft == Qt.AlignLeft
    assert Qt.AspectRatioMode.KeepAspectRatio == Qt.KeepAspectRatio
    assert Qt.GlobalColor.green == Qt.green


def test_qpainter():
    QPainter = QtGui.QPainter
    assert QPainter.RenderHint.Antialiasing == QPainter.Antialiasing
