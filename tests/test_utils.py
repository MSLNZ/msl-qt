import pytest

from msl.qt import Qt, QtGui, QtCore, QtWidgets, utils


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


def test_to_qcolor():

    def assert_rgba(c, r, g, b, a):
        assert c.red() == r
        assert c.green() == g
        assert c.blue() == b
        assert c.alpha() == a

    # no arguments
    assert isinstance(utils.to_qcolor(), QtGui.QColor)

    # QtGui.QColor
    color = QtGui.QColor(127, 127, 127)
    assert utils.to_qcolor(color) is not color
    assert utils.to_qcolor(color) == color

    # int or Qt.GlobalColor
    assert_rgba(utils.to_qcolor(7), 255, 0, 0, 255)
    assert_rgba(utils.to_qcolor(Qt.red), 255, 0, 0, 255)

    # string
    assert_rgba(utils.to_qcolor('red'), 255, 0, 0, 255)
    assert_rgba(utils.to_qcolor('#00FF00'), 0, 255, 0, 255)
    assert_rgba(utils.to_qcolor('#080000FF'), 0, 0, 255, 8)

    # float
    assert_rgba(utils.to_qcolor(0.0), 0, 0, 0, 255)
    assert_rgba(utils.to_qcolor(0.45), 114, 114, 114, 255)
    assert_rgba(utils.to_qcolor(0.5), 127, 127, 127, 255)
    assert_rgba(utils.to_qcolor(1.0), 255, 255, 255, 255)
    assert_rgba(utils.to_qcolor(1e9), 255, 255, 255, 255)
    assert_rgba(utils.to_qcolor(-1.0), 0, 0, 0, 255)
    assert_rgba(utils.to_qcolor(-0.1), 0, 0, 0, 255)

    # edge cases for int/float
    assert_rgba(utils.to_qcolor(0, 0, 0), 0, 0, 0, 255)
    assert_rgba(utils.to_qcolor(0.0, 0.0, 0.0), 0, 0, 0, 255)
    assert_rgba(utils.to_qcolor(1, 1, 1), 1, 1, 1, 255)
    assert_rgba(utils.to_qcolor(1., 1., 1.), 255, 255, 255, 255)
    assert_rgba(utils.to_qcolor(0, 1., 1), 0, 255, 1, 255)

    # tuple (can mix int 0-255 and float 0.0-1.0)
    assert_rgba(utils.to_qcolor((34, 58, 129)), 34, 58, 129, 255)
    assert_rgba(utils.to_qcolor((34, 58, 129, 50)), 34, 58, 129, 50)
    assert_rgba(utils.to_qcolor((34, 58/255., 129)), 34, 58, 129, 255)
    assert_rgba(utils.to_qcolor((34/255., 58/255., 129/255.)), 34, 58, 129, 255)
    assert_rgba(utils.to_qcolor((34/255., 58/255., 129/255., 0.45)), 34, 58, 129, 114)

    # wrong number of arguments
    for obj in [(1, 2), (1, 2, 3, 4, 5, 6, 7)]:
        with pytest.raises(TypeError):
            utils.to_qcolor(obj)


def test_screen_geometry():

    # just check that these don't raise an exception
    assert isinstance(utils.screen_geometry(), QtCore.QRect)
    assert isinstance(utils.screen_geometry(QtWidgets.QLabel()), QtCore.QRect)
    assert isinstance(utils.screen_geometry(QtWidgets.QLabel(parent=QtWidgets.QLabel())), QtCore.QRect)
