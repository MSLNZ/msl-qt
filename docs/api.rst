.. _api:

========================
MSL-Qt API Documentation
========================

The root package is

.. autosummary::

    msl.qt

which has the following modules

.. autosummary::

   msl.qt.io
   msl.qt.prompt

the following :class:`QWidget`\'s

+----------------------------------+-------------------------------------------------------------------+
| :class:`msl.qt.Logger            | Displays :mod:`logging` messages.                                 |
| <msl.qt.logger>`                 |                                                                   |
+----------------------------------+-------------------------------------------------------------------+
| :class:`msl.qt.ToggleSwitch      | A toggle switch QWidget, |toggle_switch|                          |
| <msl.qt.toggle_switch>`          |                                                                   |
+----------------------------------+-------------------------------------------------------------------+

and the following classes

+----------------------------------+-------------------------------------------------------------------+
| :class:`msl.qt.LoopUntilAbort    | Repeatedly perform a task until aborted by the user.              |
| <msl.qt.loop_until_abort>`       |                                                                   |
+----------------------------------+-------------------------------------------------------------------+

Package Structure
-----------------

.. toctree::

   msl.qt <_api/msl.qt>
   msl.qt.io <_api/msl.qt.io>
   msl.qt.logger <_api/msl.qt.logger>
   msl.qt.loop_until_abort <_api/msl.qt.loop_until_abort>
   msl.qt.prompt <_api/msl.qt.prompt>
   msl.qt.toggle_switch <_api/msl.qt.toggle_switch>

.. |toggle_switch| image:: _static/toggle_switch.gif
   :scale: 40 %