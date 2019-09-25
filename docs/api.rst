.. _api:

========================
MSL-Qt API Documentation
========================

The root package is

.. autosummary::

    msl.qt

which has the following modules

.. autosummary::

   msl.qt.exceptions
   msl.qt.io
   msl.qt.prompt
   msl.qt.threading

the following custom :class:`~QtWidgets.QWidget`\'s

.. autosummary::

   ~msl.qt.widgets.button.Button
   ~msl.qt.widgets.logger.Logger
   ~msl.qt.widgets.toggle_switch.ToggleSwitch
   ~msl.qt.widgets.spinboxes.DoubleSpinBox
   ~msl.qt.widgets.spinboxes.SpinBox

the following :class:`~QtWidgets.QWidget`\'s that are compatible with the :ref:`msl-equipment-welcome`
package

.. autosummary::

   ~msl.qt.equipment.configuration_viewer.ConfigurationViewer
   ~msl.qt.equipment.message_based.MessageBased
   ~msl.qt.equipment.thorlabs.translation_stage.TranslationStage

and the following convenience classes

.. autosummary::

   ~msl.qt.loop_until_abort.LoopUntilAbort
   ~msl.qt.sleep.Sleep

Package Structure
-----------------

.. toctree::
   :maxdepth: 1

   msl.qt <_api/msl.qt>
   msl.qt.exceptions <_api/msl.qt.exceptions>
   msl.qt.io <_api/msl.qt.io>
   msl.qt.loop_until_abort <_api/msl.qt.loop_until_abort>
   msl.qt.prompt <_api/msl.qt.prompt>
   msl.qt.sleep <_api/msl.qt.sleep>
   msl.qt.threading <_api/msl.qt.threading>
   msl.qt.equipment <_api/msl.qt.equipment>
   msl.qt.widgets <_api/msl.qt.widgets>

.. |toggle_switch| image:: _static/toggle_switch.gif
   :scale: 40 %
