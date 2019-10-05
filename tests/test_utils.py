import pytest
from msl.qt import QtGui, utils


def test_to_qfont():

    assert isinstance(utils.to_qfont(), QtGui.QFont)

    font = QtGui.QFont()
    assert utils.to_qfont(font) is not font
    assert utils.to_qfont(font).isCopyOf(font)

    assert utils.to_qfont(100).pointSize() == 100

    assert utils.to_qfont(12.3).pointSize() == 12
    assert utils.to_qfont(12.3).pointSizeF() == 12.3

    assert utils.to_qfont('Papyrus').family() == 'Papyrus'

    f = utils.to_qfont('Ariel')
    assert f.family() == 'Ariel'
    assert f.weight() == QtGui.QFont.Normal
    assert not f.italic()

    f = utils.to_qfont('Ariel', 48)
    assert f.family() == 'Ariel'
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Normal
    assert not f.italic()

    f = utils.to_qfont('Ariel', 48, QtGui.QFont.Bold)
    assert f.family() == 'Ariel'
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Bold
    assert not f.italic()

    f = utils.to_qfont('Ariel', 48, QtGui.QFont.Bold, True)
    assert f.family() == 'Ariel'
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Bold
    assert f.italic()

    # pass in an already-created list as a single argument
    f = utils.to_qfont(['Ariel'])
    assert f.family() == 'Ariel'
    assert f.weight() == QtGui.QFont.Normal
    assert not f.italic()

    f = utils.to_qfont(['Ariel', 48])
    assert f.family() == 'Ariel'
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Normal
    assert not f.italic()

    f = utils.to_qfont(['Ariel', 48, QtGui.QFont.Bold])
    assert f.family() == 'Ariel'
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Bold
    assert not f.italic()

    f = utils.to_qfont(['Ariel', 48, QtGui.QFont.Bold, True])
    assert f.family() == 'Ariel'
    assert f.pointSize() == 48
    assert f.weight() == QtGui.QFont.Bold
    assert f.italic()

    # the second item in the list will be cast to an integer
    # also test that one can pass in a tuple or a list
    for obj in [('Comic Sans MS', 36), ['Comic Sans MS', 36.6], ('Comic Sans MS', '36')]:
        f = utils.to_qfont(obj)
        assert f.family() == 'Comic Sans MS'
        assert f.pointSize() == 36
        assert f.weight() == QtGui.QFont.Normal
        assert not f.italic()
        f = utils.to_qfont(*obj)
        assert f.family() == 'Comic Sans MS'
        assert f.pointSize() == 36
        assert f.weight() == QtGui.QFont.Normal
        assert not f.italic()

    # the first item in the list must be a string
    for obj in [None, 1, 23.4, 5j, True, [1]]:
        with pytest.raises(TypeError) as err:
            utils.to_qfont(obj, 12)
        assert str(err.value).endswith('(as a string)')
        with pytest.raises(TypeError) as err:
            utils.to_qfont((obj, 12))
        assert str(err.value).endswith('(as a string)')

    # the first argument is not a QFont, int, float or string
    for obj in [None, 1+6j]:
        with pytest.raises(TypeError) as err:
            utils.to_qfont(obj)
        assert str(err.value).startswith('Cannot create')

    # the second item cannot be cast to an integer
    with pytest.raises(ValueError):
        utils.to_qfont(['Ariel', 'xxx'])

    # the third item cannot be cast to an integer
    with pytest.raises(ValueError):
        utils.to_qfont('Ariel', 12, 'xxx')
