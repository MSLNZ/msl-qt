import math
import string

import pytest

from msl.qt import GREEK
from msl.qt import QtGui
from msl.qt import binding
from msl.qt.widgets import spinboxes


def test_si_prefix_validator():
    Acceptable = QtGui.QValidator.State.Acceptable
    Intermediate = QtGui.QValidator.State.Intermediate
    Invalid = QtGui.QValidator.State.Invalid

    validator = spinboxes._SIPrefixValidator()
    assert validator.validate('', 0) == Intermediate

    # must start with a digit, '+', '-' or '.'
    for c in string.ascii_letters + '~`!@#$%^&*()_= {[}]|\\:;"\'<,>?/':
        assert validator.validate(c, 1) == Invalid
    for c in string.digits:
        assert validator.validate(c, 1) == Acceptable
        assert validator.fixup(c) == c+'.0 '
    assert validator.validate('-', 1) == Intermediate
    assert validator.validate('+', 1) == Intermediate
    assert validator.validate('.', 1) == Intermediate

    assert validator.validate('+-', 2) == Invalid
    assert validator.validate('-+', 2) == Invalid
    assert validator.validate('++', 2) == Invalid
    assert validator.validate('--', 2) == Invalid
    assert validator.validate('..', 2) == Invalid

    assert validator.validate('-.', 2) == Intermediate

    assert validator.validate('+.', 2) == Intermediate

    assert validator.validate('-0.', 3) == Acceptable
    assert validator.fixup('-0.') == '-0.0 '

    assert validator.validate('+1.', 3) == Acceptable
    assert validator.fixup('-1.') == '-1.0 '

    assert validator.validate('-02.', 4) == Acceptable
    assert validator.fixup('-02.') == '-2.0 '

    assert validator.validate('+00001.', 7) == Acceptable
    assert validator.fixup('+00001.') == '1.0 '

    assert validator.validate('1e', 2) == Intermediate

    # SI prefix cannot follow a letter
    assert validator.validate('1ef', 3) == Invalid
    # exponential cannot follow a SI prefix
    assert validator.validate('1fe', 3) == Invalid

    assert validator.validate('1.23.', 5) == Invalid
    assert validator.validate('1.23+', 5) == Invalid
    assert validator.validate('1.23-', 5) == Invalid

    assert validator.validate('1ee', 3) == Invalid
    assert validator.validate('1eE', 3) == Invalid
    assert validator.validate('1e.', 3) == Invalid
    assert validator.validate('1.e', 3) == Intermediate
    assert validator.validate('1.1e', 4) == Intermediate
    assert validator.validate('-1.11436e', 9) == Intermediate
    assert validator.validate('-1.11436e2', 10) == Acceptable
    assert validator.fixup('1.11436e6') == '1.11436 M'

    # 'E' is an SI prefix (exa -> 1e18)
    assert validator.validate('1E', 2) == Acceptable
    assert validator.fixup('1E') == '1.0 E'
    assert validator.validate('1En', 3) == Invalid
    assert validator.validate('1E2', 3) == Acceptable
    assert validator.fixup('1E2') == '100.0 '
    assert validator.validate('-1.E-15', 7) == Acceptable
    assert validator.fixup('-1.E-15') == '-1.0 f'

    assert validator.validate('-1.2n', 5) == Acceptable
    assert validator.fixup('-1.2n') == '-1.2 n'
    assert validator.validate('-1.2 n', 6) == Acceptable
    assert validator.fixup('-1.2 n') == '-1.2 n'

    assert validator.validate('0.12f3', 6) == Invalid


def test_doublespinbox():
    dsb = spinboxes.DoubleSpinBox()
    assert dsb.value() == 0
    assert dsb.minimum() == 0
    assert dsb.maximum() == 100
    assert dsb.singleStep() == 1
    assert dsb.decimals() == 2
    assert dsb._validator is None
    assert dsb.suffix() == ''
    assert dsb.toolTip() == ''

    dsb = spinboxes.DoubleSpinBox(unit=GREEK.beta)
    assert dsb.suffix() == GREEK.beta.value

    dsb = spinboxes.DoubleSpinBox(
        value=4.3, minimum=-632, maximum=1e5, step=0.02,
        decimals=4, use_si_prefix=False, unit='C', tooltip='hi'
    )
    assert dsb.value() == 4.3
    assert dsb.minimum() == -632.0
    assert dsb.maximum() == 1.0e5
    assert dsb.singleStep() == 0.02
    assert dsb.decimals() == 4
    assert dsb._validator is None
    assert dsb.suffix() == 'C'
    assert dsb.toolTip() == 'hi'
    dsb.setValue(9876)
    assert dsb.value() == 9876.0

    # wrong number of arguments (get fatal crash with PySide6 during tests)
    if binding.name != 'PySide6':
        with pytest.raises(TypeError):
            dsb.setValue('12n')  # cannot us SI prefix

    dsb = spinboxes.DoubleSpinBox(use_si_prefix=True)
    assert dsb.minimum() == 0.0
    assert dsb.maximum() == 100.0
    assert isinstance(dsb._validator, spinboxes._SIPrefixValidator)

    dsb = spinboxes.DoubleSpinBox(minimum=-0.999999999999999e27, maximum=0.999999999999999e27, use_si_prefix=True)
    assert dsb.minimum() == -0.99999999999999e27
    assert dsb.maximum() == 0.99999999999999e27
    assert isinstance(dsb._validator, spinboxes._SIPrefixValidator)

    dsb = spinboxes.DoubleSpinBox(minimum=-math.inf, maximum=math.inf, use_si_prefix=True)
    assert dsb.minimum() == -0.99999999999999e27
    assert dsb.maximum() == 0.99999999999999e27
    assert isinstance(dsb._validator, spinboxes._SIPrefixValidator)

    dsb = spinboxes.DoubleSpinBox(minimum=0.99999999999e-25, maximum=1e30, use_si_prefix=True)
    assert dsb.minimum() == 0.0  # gets rounded by Qt
    assert dsb.maximum() == 0.99999999999999e27
    assert isinstance(dsb._validator, spinboxes._SIPrefixValidator)

    dsb = spinboxes.DoubleSpinBox(minimum=-1e-20, maximum=1e10, use_si_prefix=True)
    assert dsb.minimum() == 0.0  # gets rounded by Qt
    assert dsb.maximum() == 1e10
    assert isinstance(dsb._validator, spinboxes._SIPrefixValidator)

    dsb = spinboxes.DoubleSpinBox(minimum=-1e-6, maximum=1e10, decimals=7, use_si_prefix=True)
    assert dsb.minimum() == -1e-6
    assert dsb.maximum() == 1e10
    assert isinstance(dsb._validator, spinboxes._SIPrefixValidator)

    dsb = spinboxes.DoubleSpinBox(minimum=1e3, maximum=1e20, use_si_prefix=True)
    assert dsb.value() == 1e3
    assert dsb.minimum() == 1e3
    assert dsb.maximum() == 1e20
    assert isinstance(dsb._validator, spinboxes._SIPrefixValidator)

    dsb = spinboxes.DoubleSpinBox(minimum=-0.105, maximum=0.105, decimals=3, use_si_prefix=True)
    assert dsb.minimum() == -0.105
    assert dsb.maximum() == 0.105
    assert isinstance(dsb._validator, spinboxes._SIPrefixValidator)
    dsb.setValue('12n')
    assert dsb.value() == pytest.approx(12e-9)
    dsb.setValue(0.012)
    assert dsb.value() == 0.012
    for value in [-1e2, -math.inf, '-1e5', '-1P', -1.1e30]:
        dsb.setValue(value)
        assert dsb.value() == -0.105
    for steps in [-1, int(-1e30)]:
        dsb.stepBy(steps)
        assert dsb.value() == -0.105
    for value in [1e2, math.inf, '1e5', '1P', 1.1e30]:
        dsb.setValue(value)
        assert dsb.value() == 0.105
    for steps in [1, int(1e30)]:
        dsb.stepBy(steps)
        assert dsb.value() == 0.105

    dsb = spinboxes.DoubleSpinBox(minimum=-math.inf, maximum=math.inf, use_si_prefix=True)
    dsb.setValue('12n')
    assert dsb.value() == pytest.approx(12e-9)
    dsb.setValue('103.4m')
    assert dsb.value() == pytest.approx(0.1034)
    dsb.setValue('  -.4  a  ')
    assert dsb.value() == pytest.approx(-0.4e-18)
    dsb.setValue(3.4e-7)
    assert dsb.value() == pytest.approx(3.4e-7)
    dsb.setValue(3.4e21)
    assert dsb.value() == pytest.approx(3.4e21)
    dsb.setValue('-1000.00 Y')
    assert dsb.value() == pytest.approx(-1e27)
    dsb.stepBy(10)
    assert dsb.value() == pytest.approx(-9.9e+26)
    dsb.setValue('1000Y')
    assert dsb.value() == pytest.approx(1e27)
    dsb.stepBy(-10)
    assert dsb.value() == pytest.approx(9.9e+26)
    dsb.setValue(0.0)
    assert dsb.value() == 0.0
    dsb.stepBy(100)
    assert dsb.value() == 100.0
    dsb.stepBy(-1000)
    assert dsb.value() == -900.0
    dsb.setValue('1E')
    assert dsb.value() == pytest.approx(1e18)
    dsb.setValue('1E0')
    assert dsb.value() == pytest.approx(1.0)
