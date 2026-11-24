# SpinBox

A [QSpinBox][msl.qt.binding.QtWidgets.QSpinBox] to enter an integer value.

In situations where the value of the [SpinBox] represents the position/value of equipment in the laboratory, one typically does not want to connect the [valueChanged][msl.qt.binding.QtWidgets.QSpinBox.valueChanged] signal of the [SpinBox] to change the position of the equipment because each numeric key press would be sent to the equipment. For example, if you want to set the position of a translation stage to 123 then typing the value 123 in the [SpinBox] would send three move commands to the equipment:

* 1 &mdash; move to position 1
* 12 &mdash; move to position 12
* 123 &mdash; move to position 123

The custom implementation emits the [editingFinished][msl.qt.binding.QtWidgets.QAbstractSpinBox.editingFinished] signal when any of the following events occur:

* the [SpinBox] loses focus
* the Enter key is pressed
* the Up, Down, PageUp or PageDown key is pressed
* the Increment or Decrement button is clicked

!!! example "Run the example"
    ```console
    python -c "from msl.examples.qt import run; run('SpinBox')"
    ```

    ??? abstract "Click to view the example source code"
        ```python
        --8 < --"src/msl/examples/qt/spinbox.py"
        ```

!!! note "See Also"
    [DoubleSpinBox][] to enter a floating-point value.

::: msl.qt.widgets.spinbox.SpinBox
    options:
        show_root_full_path: false
        show_root_heading: true
        filters: ["!(^_|stepBy)"]

[SpinBox]: #msl.qt.widgets.spinbox.SpinBox