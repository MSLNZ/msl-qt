import pytest
from msl.qt import QtGui, utils


def test_to_qfont():

    with pytest.raises(TypeError):
        utils.to_qfont(None)

    # the tuple/list must have length == 2
    for obj in [(), [], (1,), [1]]:
        with pytest.raises(ValueError):
            utils.to_qfont(obj)

    font = QtGui.QFont()
    assert utils.to_qfont(font) is font

    font = utils.to_qfont(100)
    assert font.pointSize() == 100

    font = utils.to_qfont(12.3)
    assert font.pointSize() == 12
    assert font.pointSizeF() == 12.3

    font = utils.to_qfont('Papyrus')
    assert font.family() == 'Papyrus'

    font = utils.to_qfont(('Ariel', 48))
    assert font.family() == 'Ariel'
    assert font.pointSize() == 48

    # the second item in the list will be cast to an integer
    # also test that one can pass in a tuple or a list
    for obj in [('Comic Sans MS', 36), ['Comic Sans MS', 36.6], ('Comic Sans MS', '36')]:
        font = utils.to_qfont(obj)
        assert font.family() == 'Comic Sans MS'
        assert font.pointSize() == 36

    # the second item in the list cannot be cast to an integer
    with pytest.raises(ValueError):
        utils.to_qfont(['Ariel', 'xxx'])

    # the first item in the list must be a string
    for obj in [1, 23.4, 5j, True, [1]]:
        with pytest.raises(TypeError):
            utils.to_qfont((obj, 12))
