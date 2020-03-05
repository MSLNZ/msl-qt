import math

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


def test_number_to_si():

    def check(args, number, string):
        value, prefix = args
        if math.isnan(number):
            assert math.isnan(value)
            assert prefix == ''
        elif math.isinf(number):
            assert math.isinf(value)
            assert prefix == ''
        else:
            assert number == pytest.approx(value, abs=1e-12)
            assert prefix == string

    check(utils.number_to_si(math.nan), math.nan, '')
    check(utils.number_to_si(math.inf), math.inf, '')
    check(utils.number_to_si(-math.inf), -math.inf, '')

    with pytest.raises(ValueError) as e:
        utils.number_to_si(0.0012e-24)
    assert 'cannot be expressed' in str(e.value)

    check(utils.number_to_si(-12.34e-25), -1.234, 'y')
    check(utils.number_to_si(0.123e-20), 1.23, 'z')
    check(utils.number_to_si(-123456e-23), -1.23456, 'a')
    check(utils.number_to_si(1.23e-13), 123.0, 'f')
    check(utils.number_to_si(-1.23e-12), -1.23, 'p')
    check(utils.number_to_si(123.e-12), 123., 'p')
    check(utils.number_to_si(-12.3e-10), -1.23, 'n')
    check(utils.number_to_si(1.23e-8), 12.3, 'n')
    check(utils.number_to_si(-0.123e-7), -12.3, 'n')
    check(utils.number_to_si(0.123e-5), 1.23, '\u00b5')
    check(utils.number_to_si(-0.0123), -12.3, 'm')
    check(utils.number_to_si(123.4), 123.4, '')
    check(utils.number_to_si(0), 0, '')
    check(utils.number_to_si(-123456.789), -123.456789, 'k')
    check(utils.number_to_si(1.23e8), 123., 'M')
    check(utils.number_to_si(-0.123e10), -1.23, 'G')
    check(utils.number_to_si(1.23e14), 123., 'T')
    check(utils.number_to_si(-1.23e12), -1.23, 'T')
    check(utils.number_to_si(12.3e15), 12.3, 'P')
    check(utils.number_to_si(-712.123e14), -71.2123, 'P')
    check(utils.number_to_si(1234.56e16), 12.3456, 'E')
    check(utils.number_to_si(-12.3e18), -12.3, 'E')
    check(utils.number_to_si(0.123e20), 12.3, 'E')
    check(utils.number_to_si(-12.3e20), -1.23, 'Z')
    check(utils.number_to_si(-1.754e21), -1.754, 'Z')
    check(utils.number_to_si(123.456e20), 12.3456, 'Z')
    check(utils.number_to_si(123.456e21), 123.456, 'Z')
    check(utils.number_to_si(-0.42e24), -420., 'Z')
    check(utils.number_to_si(1.234e24), 1.234, 'Y')
    check(utils.number_to_si(12.678e24), 12.678, 'Y')
    check(utils.number_to_si(12345.678e22), 123.45678, 'Y')

    with pytest.raises(ValueError) as e:
        utils.number_to_si(12345.678e24)
    assert 'cannot be expressed' in str(e.value)

    check(utils.number_to_si(-0), 0., '')
    check(utils.number_to_si(0), 0., '')
    check(utils.number_to_si(1), 1., '')
    check(utils.number_to_si(-1), -1., '')
    check(utils.number_to_si(12), 12., '')
    check(utils.number_to_si(123), 123., '')
    check(utils.number_to_si(1234), 1.234, 'k')
    check(utils.number_to_si(12345), 12.345, 'k')
    check(utils.number_to_si(123456), 123.456, 'k')
    check(utils.number_to_si(1234567), 1.234567, 'M')
    check(utils.number_to_si(12345678), 12.345678, 'M')
    check(utils.number_to_si(123456789), 123.456789, 'M')
    check(utils.number_to_si(-123456789), -123.456789, 'M')
    check(utils.number_to_si(1234567890), 1.234567890, 'G')
    check(utils.number_to_si(12345678901), 12.345678901, 'G')
    check(utils.number_to_si(123456789012), 123.456789012, 'G')
    check(utils.number_to_si(1234567890123), 1.234567890123, 'T')
    check(utils.number_to_si(12345678901234), 12.345678901234, 'T')
    check(utils.number_to_si(123456789012345), 123.456789012345, 'T')
    check(utils.number_to_si(1234567890123456), 1.234567890123456, 'P')
    check(utils.number_to_si(-1234567890123456), -1.234567890123456, 'P')
    check(utils.number_to_si(12345678901234567), 12.345678901234567, 'P')
    check(utils.number_to_si(123456789012345678), 123.456789012345678, 'P')
    check(utils.number_to_si(1234567890123456789), 1.234567890123456789, 'E')
    check(utils.number_to_si(12345678901234567890), 12.345678901234567890, 'E')
    check(utils.number_to_si(123456789012345678901), 123.456789012345678901, 'E')
    check(utils.number_to_si(1234567890123456789012), 1.234567890123456789012, 'Z')
    check(utils.number_to_si(12345678901234567890123), 12.345678901234567890123, 'Z')
    check(utils.number_to_si(123456789012345678901234), 123.456789012345678901234, 'Z')
    check(utils.number_to_si(1234567890123456789012345), 1.234567890123456789012345, 'Y')
    check(utils.number_to_si(12345678901234567890123456), 12.345678901234567890123456, 'Y')
    check(utils.number_to_si(123456789012345678901234567), 123.456789012345678901234567, 'Y')
    check(utils.number_to_si(-123456789012345678901234567), -123.456789012345678901234567, 'Y')

    with pytest.raises(ValueError) as e:
        utils.number_to_si(1234567890123456789012345678)
    assert 'cannot be expressed' in str(e.value)


def test_si_to_number():

    def check(string, value):
        assert utils.si_to_number(string) == pytest.approx(value)

    check('12.3m', 0.0123)
    check('123.456789k', 123456.789)
    check('71.2123P', 712.123e14)
    check('123f', 1.23e-13)

    check('0.12Y', 1.2e23)
    check('1.2Y', 1.2e24)
    check('-123.4Y', -1.234e26)
    check('0.12Z', 1.2e20)
    check('-1.2Z', -1.2e21)
    check('-123.4Z', -1.234e23)
    check('-0.12E', -1.2e17)
    check('1.2E', 1.2e18)
    check('123.4E', 1.234e20)
    check('-0.12P', -1.2e14)
    check('1.2P', 1.2e15)
    check('123.4P', 1.234e17)
    check('0.12T', 1.2e11)
    check('-1.2T', -1.2e12)
    check('123.4T', 1.234e14)
    check('-0.12G', -1.2e8)
    check('1.2G', 1.2e9)
    check('123.4G', 1.234e11)
    check('0.12M', 1.2e5)
    check('1.2M', 1.2e6)
    check('-123.4M', -1.234e8)
    check('-0.12k', -1.2e2)
    check('1.2k', 1.2e3)
    check('123.4k', 1.234e5)
    check('-0.12', -0.12)
    check('0', 0)
    check('123456789', 123456789.0)
    check('1.2', 1.2)
    check('123.4', 123.4)
    check('0.12m', 1.2e-4)
    check('-1.2m', -1.2e-3)
    check('123.4m', 1.234e-1)
    check('-0.12\u00b5', -1.2e-7)
    check('1.2\u00b5', 1.2e-6)
    check('123.4\u00b5', 1.234e-4)
    check('-0.12u', -1.2e-7)
    check('1.2u', 1.2e-6)
    check('123.4u', 1.234e-4)
    check('0.12n', 1.2e-10)
    check('1.2n', 1.2e-9)
    check('-123.4n', -1.234e-7)
    check('0.12p', 1.2e-13)
    check('1.2p', 1.2e-12)
    check('-123.4p', -1.234e-10)
    check('0.12f', 1.2e-16)
    check('-1.2f', -1.2e-15)
    check('123.4f', 1.234e-13)
    check('0.12a', 1.2e-19)
    check('-1.2a', -1.2e-18)
    check('123.4a', 1.234e-16)
    check('-0.12z', -1.2e-22)
    check('-1.2z', -1.2e-21)
    check('123.4z', 1.234e-19)
    check('0.12y', 1.2e-25)
    check('1.2y', 1.2e-24)
    check('-123.4y', -1.234e-22)

    # spaces
    check('123.4 m', 1.234e-1)
    check('123.4   m    ', 1.234e-1)
    check('  123.4   m    ', 1.234e-1)
    for item in ['', '    ', '\t', ' \t  ']:
        with pytest.raises(ValueError) as err:
            utils.si_to_number(item)
        assert str(err.value).startswith("could not convert string to float: ''")

    # nan, +/-inf
    assert math.isnan(utils.si_to_number('nan'))
    value = utils.si_to_number('inf')
    assert math.isinf(value) and value > 0
    value = utils.si_to_number('+inf')
    assert math.isinf(value) and value > 0
    value = utils.si_to_number('-inf')
    assert math.isinf(value) and value < 0

    for c in 'bcdeghijloqrstvwxABCDFHIJKLNOQRSUVWX':
        with pytest.raises(ValueError) as err:
            utils.si_to_number('1.2'+c)
        assert str(err.value).startswith('could not convert string to float: {!r}'.format('1.2'+c))

        for prefix in 'yzafpnu\u00b5mkMGTPEZY':
            with pytest.raises(ValueError) as err:
                utils.si_to_number('1.2'+c+prefix)
            # the prefix is not at the end of the error message
            assert str(err.value).startswith('could not convert string to float: {!r}'.format('1.2'+c))
