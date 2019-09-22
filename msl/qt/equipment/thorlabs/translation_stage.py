"""
A :class:`~QtWidgets.QWidget` for controlling a Thorlabs_ translation stage.

.. _Thorlabs: https://www.thorlabs.com/navigation.cfm?guide_id=2060
"""
import os
import time

from msl.qt import QtWidgets, QtCore, QtGui, Signal
from msl.qt import prompt
from msl.qt.io import get_icon
from msl.qt.equipment.thorlabs import show_hardware_info

try:
    from msl.equipment import Config
    from msl.equipment.resources.thorlabs import MotionControlCallback
    from msl.equipment.resources.thorlabs.kinesis.enums import UnitType

    import numpy as np  # a dependency of MSL Equipment

    class _Signaler(QtCore.QObject):
        """Used for sending a signal of the current position."""
        signal = Signal()

    signaler = _Signaler()

    @MotionControlCallback
    def callback():
        signaler.signal.emit()

except ImportError:
    signaler = None


class TranslationStage(QtWidgets.QWidget):

    def __init__(self, connection, config=None, parent=None):
        """A :class:`~QtWidgets.QWidget` for controlling a Thorlabs translation stage.

        Parameters
        ----------
        connection : :class:`~msl.equipment.connection.Connection`
            The connection to the translational stage motor controller
            (e.g., LTS150, LTS300, KST101, KDC101, ...).
        config : :class:`~msl.equipment.config.Config`, optional
            A configuration file.

            The following elements can be defined in a :class:`~msl.equipment.config.Config` file to
            initialize a :class:`TranslationStage`:

            .. code-block:: xml

                <!--
                  The following attributes can be defined for a "preset" and a "jog size" element.
                  For a "preset" you must define a name attribute:
                    units - can be either "mm" or "device". If omitted then the default unit value is "mm"
                    name - the text that will displayed in the GUI as the name of the preset
                  If multiple translation stages are being used then you can uniquely identify which stage will
                  have its properties updated by including one of the additional attributes:
                    serial - the serial number of the translation stage motor controller
                    alias - the same alias that is used in the <equipment> XML tag
                  If you do not include one of 'serial' or 'alias' then all stages will be updated to the XML element value.
                -->

                <thorlabs_translation_stage_preset name='Si-PD' serial="123456789">54.232</thorlabs_translation_stage_preset>
                <thorlabs_translation_stage_preset name='InGaAs-PD' units="mm" serial="123456789">75.2</thorlabs_translation_stage_preset>
                <thorlabs_translation_stage_preset name='Reference' units="device" serial="123456789">10503037</thorlabs_translation_stage_preset>

                <!-- Note: In the following you can also specify the calibration path to be a path relative to the configuration file -->
                <thorlabs_translation_stage_calibration_path serial="123456789">path/to/calibration/file.dat</thorlabs_translation_stage_calibration_path>

                <!-- Since the 'serial', 'alias' and 'unit' attributes are not defined then all stages will have the jog size set to 2.0 mm -->
                <thorlabs_translation_stage_jog_size>2.0</thorlabs_translation_stage_jog_size>

        parent : :class:`QtWidgets.QWidget`, optional
            The parent widget.
        """
        super(TranslationStage, self).__init__(parent=parent)

        if signaler is None:
            raise ImportError('This widget requires that the MSL-Equipment package is installed')

        if config is not None and not issubclass(config.__class__, Config):
            raise TypeError('Must pass in a MSL Equipment configuration object. Received {}'.format(config.__class__))

        self._connection = connection

        self._supports_calibration = hasattr(self._connection, 'set_calibration_file')
        self._uncalibrated_mm = np.array([])
        self._calibrated_mm = np.array([])
        self._calibration_label = ''

        # set the calibration file
        if config is not None and self._supports_calibration:
            elements = self._find_xml_elements(config, 'thorlabs_translation_stage_calibration_path')
            if elements:
                cal_path = elements[0].text
                rel_path = os.path.join(os.path.dirname(config.path), cal_path)
                if os.path.isfile(cal_path):
                    self.set_calibration_file(cal_path)
                elif os.path.isfile(rel_path):
                    self.set_calibration_file(rel_path)
                else:
                    prompt.critical('Cannot find calibration file\n' + cal_path)

        # set the presets
        self._preset_combobox = QtWidgets.QComboBox()
        self._preset_combobox.setToolTip('Preset positions')
        self._preset_combobox.addItems(['', 'Home'])
        self.preset_positions = {}
        if config is not None:
            for element in self._find_xml_elements(config, 'thorlabs_translation_stage_preset'):
                self.add_preset(element.attrib['name'], float(element.text), element.attrib.get('units', 'mm') == 'mm')

        self._min_pos_mm, self._max_pos_mm = self._connection.get_motor_travel_limits()

        self._position_display = QtWidgets.QLineEdit()
        self._position_display.setReadOnly(True)
        self._position_display.setFont(QtGui.QFont('Helvetica', 24))
        self._position_display.mouseDoubleClickEvent = self._ask_move_to
        fm = QtGui.QFontMetrics(self._position_display.font())
        self._position_display.setFixedWidth(fm.width(' {}.xxx'.format(int(self._max_pos_mm))))

        self._home_button = QtWidgets.QPushButton()
        self._home_button.setToolTip('Go to the Home position')
        self._home_button.clicked.connect(self.go_home)
        self._home_button.setIcon(get_icon('ieframe|0'))

        self._stop_button = QtWidgets.QPushButton('Stop')
        self._stop_button.setToolTip('Stop moving immediately')
        self._stop_button.clicked.connect(self._connection.stop_immediate)
        self._stop_button.setIcon(get_icon('wmploc|155'))

        if config is not None:
            elements = self._find_xml_elements(config, 'thorlabs_translation_stage_jog_size')
            if elements:
                element = elements[0]
                if element.attrib.get('units', 'mm') == 'mm':
                    jog_mm = float(element.text)
                    jog = self._connection.get_device_unit_from_real_value(jog_mm, UnitType.DISTANCE)
                    s = element.text + ' mm'
                else:
                    jog = int(float(element.text))
                    jog_mm = self._connection.get_real_value_from_device_unit(jog, UnitType.DISTANCE)
                    s = element.text + ' device units'
                if jog_mm > self._max_pos_mm or jog_mm < self._min_pos_mm:
                    prompt.critical('Invalid jog size of ' + s)
                else:
                    self._connection.set_jog_step_size(jog)

        self._jog_forward_button = QtWidgets.QPushButton()
        self._jog_forward_button.clicked.connect(lambda: self.jog_forward(False))
        self._jog_forward_button.setIcon(get_icon(QtWidgets.QStyle.SP_ArrowUp))

        self._jog_backward_button = QtWidgets.QPushButton()
        self._jog_backward_button.clicked.connect(lambda: self.jog_backward(False))
        self._jog_backward_button.setIcon(get_icon(QtWidgets.QStyle.SP_ArrowDown))

        settings_button = QtWidgets.QPushButton()
        settings_button.clicked.connect(self._show_settings)
        settings_button.setIcon(get_icon('shell32|71'))
        settings_button.setToolTip('Edit the jog and move settings')

        grid = QtWidgets.QGridLayout()
        grid.addWidget(QtWidgets.QLabel('Presets:'), 0, 0, alignment=QtCore.Qt.AlignRight)
        grid.addWidget(self._preset_combobox, 0, 1)
        grid.addWidget(self._stop_button, 0, 2, 1, 2)
        grid.addWidget(self._position_display, 1, 0, 2, 2)
        grid.addWidget(self._home_button, 1, 2)
        grid.addWidget(self._jog_forward_button, 1, 3)
        grid.addWidget(settings_button, 2, 2)
        grid.addWidget(self._jog_backward_button, 2, 3)
        grid.setSpacing(0)
        grid.setRowStretch(3, 1)
        grid.setColumnStretch(4, 1)
        self.setLayout(grid)

        self._connection.start_polling(200)
        self._polling_duration = self._connection.polling_duration() * 1e-3
        self._connection.register_message_callback(callback)
        signaler.signal.connect(self._update_display)

        self._requested_mm = None
        self._update_jog_tooltip()
        self._update_display()

        self._requested_mm = float(self._position_display.text())
        self._preset_combobox.setCurrentText(self._get_preset_name(self._requested_mm))
        self._preset_combobox.currentIndexChanged[str].connect(self._go_to_preset)

    def add_preset(self, name, position, millimeters=True):
        """Add a preset position.

        Parameters
        ----------
        name : :class:`str`
            The name of the preset.
        position : :class:`float` or :class:`int`
            The position.
        millimeters : :class:`bool`
            Whether the value of the `position` is in millimeters or in ``device units``.
        """
        if not millimeters:
            position = self._connection.get_real_value_from_device_unit(int(position), UnitType.DISTANCE)
        self.preset_positions[name] = float(position)
        self._preset_combobox.addItem(name)

    def closeEvent(self, event):
        """Overrides `closeEvent <https://doc.qt.io/qt-5/qwidget.html#closeEvent>`_."""
        self._connection.stop_polling()

    def get_jog(self, millimeters=True):
        """Get the jog step size.

        Parameters
        ----------
        millimeters : :class:`bool`, optional
            Whether to return the jog step size in ``device units`` or in ``real-world units``
            (i.e., in millimeters). The default is to return the value in millimeters.

        Returns
        -------
        :class:`int` or :class:`float`
            The jog step size in either device units (:class:`int`) or in millimeters
            (:class:`float`).
        """
        size = self._connection.get_jog_step_size()
        if not millimeters:
            return size
        return self._connection.get_real_value_from_device_unit(size, UnitType.DISTANCE)

    def get_position(self, millimeters=True):
        """Get the current position (calibrated).

        If no calibration file has been set then this function returns
        the same value as :meth:`get_position_raw`.

        Parameters
        ----------
        millimeters : :class:`bool`, optional
            Whether to return the current position in ``device units`` or in ``real-world units``
            (i.e., in millimeters). The default is to return the value in millimeters.

        Returns
        -------
        :class:`int` or :class:`float`
            The current position in either device units (:class:`int`) or in millimeters
            (:class:`float`).
        """
        pos = float(self._position_display.text())
        if not millimeters:
            return self._connection.get_device_unit_from_real_value(pos, UnitType.DISTANCE)
        return pos

    def get_position_raw(self, millimeters=True):
        """Get the current position (raw and uncalibrated).

        Parameters
        ----------
        millimeters : :class:`bool`, optional
            Whether to return the current position in ``device units`` or in ``real-world units``
            (i.e., in millimeters). The default is to return the value in millimeters.

        Returns
        -------
        :class:`int` or :class:`float`
            The current position (raw and uncalibrated) in either device units (:class:`int`)
            or in millimeters (:class:`float`).
        """
        pos = self._connection.get_position()
        if not millimeters:
            return pos
        return self._connection.get_real_value_from_device_unit(pos, UnitType.DISTANCE)

    def go_home(self, wait=True):
        """Send the motor home.

        Parameters
        ----------
        wait : :class:`bool`
            Wait until the move is finished before returning control to the calling program.
            If :data:`True` then this is a blocking method.
        """
        self._requested_mm = 0.0
        self._connection.home()
        if wait:
            self._wait(0)
        self._update_preset_text_block_signals(0.0)

    def jog_backward(self, wait=True):
        """Jog backward.

        Parameters
        ----------
        wait : :class:`bool`
            Wait until the move is finished before returning control to the calling program.
            If :data:`True` then this is a blocking method.
        """
        # prefer for the move request to go through the move_to method
        # rather than using "self._connection.move_jog(MOT_TravelDirection.MOT_Reverse)"
        pos = self.get_position() - self.get_jog()
        self.move_to(pos, wait=wait, millimeters=True)

    def jog_forward(self, wait=True):
        """Jog forward.

        Parameters
        ----------
        wait : :class:`bool`
            Wait until the move is finished before returning control to the calling program.
            If :data:`True` then this is a blocking method.
        """
        # prefer for the move request to go through the move_to method
        # rather than using "self._connection.move_jog(MOT_TravelDirection.MOT_Forwards)"
        pos = self.get_position() + self.get_jog()
        self.move_to(pos, wait=wait, millimeters=True)

    def move_by(self, value, wait=True, millimeters=True):
        """Move by a relative value.

        Parameters
        ----------
        value : :class:`int` or :class:`float`
            The relative value to move by.
        wait : :class:`bool`
            Wait until the move is finished before returning control to the calling program.
            If :data:`True` then this is a blocking method.
        millimeters : :class:`bool`, optional
            Whether the `value` is in ``device units`` or in ``real-world units`` (i.e., in millimeters).
        """
        # prefer for the move request to go through the move_to method
        # rather than using "self._connection.move_relative(displacement)"
        pos = self.get_position(millimeters) + value
        self.move_to(pos, wait=wait, millimeters=millimeters)

    def move_to(self, value, wait=True, millimeters=True):
        """Move to an absolute position.

        Parameters
        ----------
        value : :class:`int`, :class:`float` or :class:`str`
            If :class:`str` then the name of a preset. Otherwise an absolute position to move to.
        wait : :class:`bool`
            Wait until the move is finished before returning control to the calling program.
            If :data:`True` then this is a blocking method.
        millimeters : :class:`bool`, optional
            Whether the `value` is in ``device units`` or in ``real-world units`` (i.e., in millimeters).
        """
        if isinstance(value, str):
            if value not in self.preset_positions:
                prompt.critical('{} is not a preset. Must be one of: ' + ','.join(self.preset_positions.keys()))
                return
            value = self.preset_positions[value]
            millimeters = True  # the preset values are in real-world units

        if not self._connection.can_move_without_homing_first():
            res = prompt.question('The motor should be homed before a move can be performed.\n\nHome the motor?')
            if res:
                self.go_home(False)
                return

        if not millimeters:
            value_du = value
            value_mm = self._connection.get_real_value_from_device_unit(value, UnitType.DISTANCE)
        else:
            value_du = self._connection.get_device_unit_from_real_value(value, UnitType.DISTANCE)
            value_mm = value

        if self._min_pos_mm <= value_mm <= self._max_pos_mm:
            self._requested_mm = value_mm
            self._connection.move_to_position(value_du)
            if wait:
                self._wait(value_du)
            self._update_preset_text_block_signals(value)
        else:
            m = 'Invalid move request.\n\n{} is outside the allowed range [{}, {}]'
            prompt.critical(m.format(value, self._min_pos_mm, self._max_pos_mm))

    def set_calibration_file(self, path, enabled=True):
        """Set the calibration file.

        Parameters
        ----------
        path : :class:`str`
            The path to the calibration file.
        enabled : :class:`bool`, optional
            Whether to enable or disable the calibration file.
        """
        if not self._supports_calibration:
            prompt.critical('The translation stage, {}, does not support a calibration file'.format(self._connection))
            return

        try:
            self._connection.set_calibration_file(path, enabled)
        except IOError:
            prompt.critical('Cannot find calibration file\n' + path)

        if self._connection.is_calibration_active():
            device_cal_path = self._connection.get_calibration_file()
            self._uncalibrated_mm, self._calibrated_mm = np.loadtxt(device_cal_path, unpack=True)
            self._calibration_label = 'Calibration file: {}'.format(os.path.basename(device_cal_path))
        else:
            self._uncalibrated_mm, self._calibrated_mm = np.array([]), np.array([])
            self._calibration_label = ''

    def set_jog(self, value, millimeters=True):
        """Set the jog step size.

        Parameters
        ----------
        value : :class:`int` or :class:`float`
            The jog step size.
        millimeters : :class:`bool`, optional
            Whether the `value` is in ``device units`` or in ``real-world units`` (i.e., in millimeters).
        """
        if not millimeters:
            jog = int(value)
            jog_mm = self._connection.get_real_value_from_device_unit(jog, UnitType.DISTANCE)
            msg = '{} device units'.format(jog)
        else:
            jog_mm = float(value)
            jog = self._connection.get_device_unit_from_real_value(jog_mm, UnitType.DISTANCE)
            msg = '{} mm'.format(jog)
        if jog_mm > self._max_pos_mm or jog_mm < self._min_pos_mm:
            prompt.critical('Invalid jog size of ' + msg)
        else:
            self._connection.set_jog_step_size(jog)
            self._update_jog_tooltip()

    def _ask_move_to(self, event):
        msg = 'Move to position (min:{} max:{})'.format(self._min_pos_mm, self._max_pos_mm)
        current = float(self._position_display.text())
        value = prompt.double(msg, default=current, minimum=self._min_pos_mm, maximum=self._max_pos_mm, precision=3)
        if value is not None and value != current:
            self.move_to(value, wait=False, millimeters=True)

    def _find_xml_elements(self, config, element_name):
        elements = []
        record = self._connection.equipment_record
        for element in config.root.findall(element_name):
            serial = element.attrib.get('serial')
            alias = element.attrib.get('alias')
            if (serial is None) and (alias is None):
                elements.append(element)
            if (serial == record.serial) or (alias == record.alias):
                elements.append(element)
        return elements

    def _get_calibrated_mm(self, pos):
        """Perform a linear fit around the current position to determine the calibrated position"""
        if pos == 0:
            return 0.0
        idx = np.abs(self._uncalibrated_mm - pos).argmin()
        min_idx = int(max(0, idx-3))
        max_idx = int(min(self._uncalibrated_mm.size, idx+3))
        if max_idx - min_idx > 1:
            fit = np.polyfit(self._uncalibrated_mm[min_idx:max_idx], self._calibrated_mm[min_idx:max_idx], 1)
            return fit[0] * pos + fit[1]
        else:
            return pos

    def _get_preset_name(self, position):
        """Returns the preset name or '' if the position does not correspond to a preset position"""
        if position == 0:
            return 'Home'
        for name, value in self.preset_positions.items():
            if abs(value - position) < 0.0015:
                return name
        return ''

    def _go_to_preset(self, name):
        if name == 'Home':
            self.go_home(False)
        elif len(name) > 0:
            self.move_to(self.preset_positions[name], wait=False, millimeters=True)

    def _show_settings(self):
        settings = _Settings(self)
        settings.sig_update_jog_tooltip.connect(self._update_jog_tooltip)
        settings.exec_()

    def _update_display(self):
        raw_device_unit = self._connection.get_position()
        raw_real_value = self._connection.get_real_value_from_device_unit(raw_device_unit, UnitType.DISTANCE)
        if self._supports_calibration and self._connection.is_calibration_active():
            # When the move is finished we should get rid of rounding errors from the calculation of the
            # calibrated position so as to not confuse the user with the position value that is displayed
            if self._requested_mm is not None and self._connection.get_status_bits() == 2148533248:
                value = self._requested_mm
            else:
                value = self._get_calibrated_mm(raw_real_value)
            # update the tooltip text
            device_unit = self._connection.get_device_unit_from_real_value(value, UnitType.DISTANCE)
            tt = 'Device Unit: {}\n\n'.format(device_unit)
            tt += 'Device Unit: {} (uncalibrated)\n'.format(raw_device_unit)
            tt += 'Position: {} mm (uncalibrated)\n\n'.format(raw_real_value)
        else:
            value = raw_real_value
            tt = 'Device Unit: {}\n\n'.format(raw_device_unit)
        self._position_display.setText('{:8.3f}'.format(value))
        self._position_display.setToolTip(tt + self._calibration_label)

    def _update_jog_tooltip(self):
        jog = self.get_jog()
        self._jog_forward_button.setToolTip('Jog forward [{:.3f} mm]'.format(jog))
        self._jog_backward_button.setToolTip('Jog backward [{:.3f} mm]'.format(jog))

    def _update_preset_text_block_signals(self, position):
        """Update the preset combobox without emitting the signal"""
        self._preset_combobox.blockSignals(True)
        self._preset_combobox.setCurrentText(self._get_preset_name(position))
        self._preset_combobox.blockSignals(False)

    def _wait(self, device_unit):
        while self.get_position_raw(millimeters=False) != device_unit:
            time.sleep(self._polling_duration)


class _Settings(QtWidgets.QDialog):

    sig_update_jog_tooltip = Signal()

    def __init__(self, parent):
        """Display a QDialog to edit the settings"""
        super(_Settings, self).__init__(flags=QtCore.Qt.WindowCloseButtonHint)

        self.conn = parent._connection

        info = self.conn.get_hardware_info()
        self.setWindowTitle(info.modelNumber.decode('utf-8') + ' || ' + info.notes.decode('utf-8'))

        # move info
        max_vel, max_acc = self.conn.get_motor_velocity_limits()
        vel, acc = self.conn.get_vel_params()
        vel = self.conn.get_real_value_from_device_unit(vel, UnitType.VELOCITY)
        acc = self.conn.get_real_value_from_device_unit(acc, UnitType.ACCELERATION)
        backlash = self.conn.get_real_value_from_device_unit(self.conn.get_backlash(), UnitType.DISTANCE)

        # move widgets
        self.acc_spinbox = QtWidgets.QDoubleSpinBox()
        self.acc_spinbox.setMinimum(0)
        self.acc_spinbox.setMaximum(max_acc)
        self.acc_spinbox.setValue(acc)
        self.acc_spinbox.setToolTip('<html><b>Range:</b><br>0 - {} mm/s<sup>2</sup></html>'.format(max_acc))

        self.vel_spinbox = QtWidgets.QDoubleSpinBox()
        self.vel_spinbox.setMinimum(0)
        self.vel_spinbox.setMaximum(max_vel)
        self.vel_spinbox.setValue(vel)
        self.vel_spinbox.setToolTip('<html><b>Range:</b><br>0 - {} mm/s</html>'.format(max_vel))

        self.backlash_spinbox = QtWidgets.QDoubleSpinBox()
        self.backlash_spinbox.setMinimum(0)
        self.backlash_spinbox.setMaximum(5)
        self.backlash_spinbox.setValue(backlash)
        self.backlash_spinbox.setToolTip('<html><b>Range:</b><br>0 - 5 mm</html>')

        move_group = QtWidgets.QGroupBox('Move Parameters')
        move_grid = QtWidgets.QGridLayout()
        move_grid.addWidget(QtWidgets.QLabel('Backlash'), 0, 0, alignment=QtCore.Qt.AlignRight)
        move_grid.addWidget(self.backlash_spinbox, 0, 1)
        move_grid.addWidget(QtWidgets.QLabel('mm'), 0, 2, alignment=QtCore.Qt.AlignLeft)
        move_grid.addWidget(QtWidgets.QLabel('Maximum Velocity'), 1, 0, alignment=QtCore.Qt.AlignRight)
        move_grid.addWidget(self.vel_spinbox, 1, 1)
        move_grid.addWidget(QtWidgets.QLabel('mm/s'), 1, 2, alignment=QtCore.Qt.AlignLeft)
        move_grid.addWidget(QtWidgets.QLabel('Acceleration'), 2, 0, alignment=QtCore.Qt.AlignRight)
        move_grid.addWidget(self.acc_spinbox, 2, 1)
        move_grid.addWidget(QtWidgets.QLabel('mm/s<sup>2</sup>'), 2, 2, alignment=QtCore.Qt.AlignLeft)
        move_group.setLayout(move_grid)

        # jog info
        jog_size = self.conn.get_real_value_from_device_unit(self.conn.get_jog_step_size(), UnitType.DISTANCE)
        vel, acc = self.conn.get_jog_vel_params()
        jog_vel = self.conn.get_real_value_from_device_unit(vel, UnitType.VELOCITY)
        jog_acc = self.conn.get_real_value_from_device_unit(acc, UnitType.ACCELERATION)

        # jog widgets
        min_jog, max_jog = 0.002, parent._max_pos_mm/2.0
        self.jog_size_spinbox = QtWidgets.QDoubleSpinBox()
        self.jog_size_spinbox.setMinimum(min_jog)
        self.jog_size_spinbox.setMaximum(max_jog)
        self.jog_size_spinbox.setDecimals(3)
        self.jog_size_spinbox.setValue(jog_size)
        self.jog_size_spinbox.setToolTip('<html><b>Range:</b><br>{} - {} mm</html>'.format(min_jog, max_jog))

        self.jog_acc_spinbox = QtWidgets.QDoubleSpinBox()
        self.jog_acc_spinbox.setMinimum(0)
        self.jog_acc_spinbox.setMaximum(max_acc)
        self.jog_acc_spinbox.setValue(jog_acc)
        self.jog_acc_spinbox.setToolTip('<html><b>Range:</b><br>0 - {} mm/s<sup>2</sup></html>'.format(max_acc))

        self.jog_vel_spinbox = QtWidgets.QDoubleSpinBox()
        self.jog_vel_spinbox.setMinimum(0)
        self.jog_vel_spinbox.setMaximum(max_vel)
        self.jog_vel_spinbox.setValue(jog_vel)
        self.jog_vel_spinbox.setToolTip('<html><b>Range:</b><br>0 - {} mm/s</html>'.format(max_vel))

        jog_group = QtWidgets.QGroupBox('Jog Parameters')
        jog_grid = QtWidgets.QGridLayout()
        jog_grid.addWidget(QtWidgets.QLabel('Step Size'), 0, 0, alignment=QtCore.Qt.AlignRight)
        jog_grid.addWidget(self.jog_size_spinbox, 0, 1)
        jog_grid.addWidget(QtWidgets.QLabel('mm'), 0, 2, alignment=QtCore.Qt.AlignLeft)
        jog_grid.addWidget(QtWidgets.QLabel('Maximum Velocity'), 1, 0, alignment=QtCore.Qt.AlignRight)
        jog_grid.addWidget(self.jog_vel_spinbox, 1, 1)
        jog_grid.addWidget(QtWidgets.QLabel('mm/s'), 1, 2, alignment=QtCore.Qt.AlignLeft)
        jog_grid.addWidget(QtWidgets.QLabel('Acceleration'), 2, 0, alignment=QtCore.Qt.AlignRight)
        jog_grid.addWidget(self.jog_acc_spinbox, 2, 1)
        jog_grid.addWidget(QtWidgets.QLabel('mm/s<sup>2</sup>'), 2, 2, alignment=QtCore.Qt.AlignLeft)
        jog_group.setLayout(jog_grid)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(move_group)
        hbox.addWidget(jog_group)

        update_button = QtWidgets.QPushButton('Update')
        update_button.setToolTip('Update the device settings')
        update_button.clicked.connect(self.update_settings)

        cancel_button = QtWidgets.QPushButton('Cancel')
        cancel_button.setToolTip('Update the device settings')
        cancel_button.clicked.connect(self.close)

        info_button = QtWidgets.QPushButton()
        info_button.setIcon(get_icon('imageres|109'))
        info_button.clicked.connect(lambda: show_hardware_info(parent._connection))
        info_button.setToolTip('Display the hardware information')

        button_layout = QtWidgets.QGridLayout()
        button_layout.addWidget(cancel_button, 0, 0)
        button_layout.addItem(QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding), 0, 1)
        button_layout.addWidget(update_button, 0, 2)
        button_layout.addWidget(info_button, 0, 3)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(button_layout)
        self.setLayout(vbox)

    def update_settings(self):
        vel = self.conn.get_device_unit_from_real_value(self.vel_spinbox.value(), UnitType.VELOCITY)
        acc = self.conn.get_device_unit_from_real_value(self.acc_spinbox.value(), UnitType.ACCELERATION)
        self.conn.set_vel_params(vel, acc)

        backlash = self.conn.get_device_unit_from_real_value(self.backlash_spinbox.value(), UnitType.DISTANCE)
        self.conn.set_backlash(backlash)

        jog_vel = self.conn.get_device_unit_from_real_value(self.jog_vel_spinbox.value(), UnitType.VELOCITY)
        jog_acc = self.conn.get_device_unit_from_real_value(self.jog_acc_spinbox.value(), UnitType.ACCELERATION)
        self.conn.set_jog_vel_params(jog_vel, jog_acc)

        jog_size = self.conn.get_device_unit_from_real_value(self.jog_size_spinbox.value(), UnitType.DISTANCE)
        self.conn.set_jog_step_size(jog_size)

        self.sig_update_jog_tooltip.emit()

        self.close()
