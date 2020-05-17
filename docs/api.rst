.. _msl-qt-api:

========================
MSL-Qt API Documentation
========================

The root package is

.. autosummary::

    msl.qt

which has the following modules

.. autosummary::

   msl.qt.constants
   msl.qt.convert
   msl.qt.exceptions
   msl.qt.prompt
   msl.qt.threading
   msl.qt.utils

the following custom :class:`~QtWidgets.QWidget`\'s

.. autosummary::

   ~msl.qt.widgets.button.Button
   ~msl.qt.widgets.led.LED
   ~msl.qt.widgets.logger.Logger
   ~msl.qt.widgets.toggle_switch.ToggleSwitch
   ~msl.qt.widgets.spinboxes.DoubleSpinBox
   ~msl.qt.widgets.spinboxes.SpinBox

and the following convenience classes

.. autosummary::

   ~msl.qt.loop_until_abort.LoopUntilAbort
   ~msl.qt.sleep.Sleep

Package Structure
-----------------

.. toctree::
   :maxdepth: 1

   msl.qt <_api/msl.qt>
   msl.qt.constants <_api/msl.qt.constants>
   msl.qt.convert <_api/msl.qt.convert>
   msl.qt.exceptions <_api/msl.qt.exceptions>
   msl.qt.loop_until_abort <_api/msl.qt.loop_until_abort>
   msl.qt.prompt <_api/msl.qt.prompt>
   msl.qt.sleep <_api/msl.qt.sleep>
   msl.qt.threading <_api/msl.qt.threading>
   msl.qt.utils <_api/msl.qt.utils>
   msl.qt.widgets <_api/msl.qt.widgets>

.. |toggle_switch| image:: _static/toggle_switch.gif
   :scale: 40 %

.. |led_widget| image:: _static/led_widget.gif
   :scale: 40 %
