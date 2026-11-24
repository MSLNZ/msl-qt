# DoubleSpinBox

A [QDoubleSpinBox][msl.qt.binding.QtWidgets.QDoubleSpinBox] to enter a floating-point value.

In situations where the value of the [DoubleSpinBox] represents the position/value of equipment in the laboratory, one typically does not want to connect the [valueChanged][msl.qt.binding.QtWidgets.QDoubleSpinBox.valueChanged] signal of the [DoubleSpinBox] to change the position of the equipment because each numeric key press would be sent to the equipment. For example, if you want to set the position of a translation stage to 123 then typing the value 123 in the [DoubleSpinBox] would send three move commands to the equipment:

* 1 &mdash; move to position 1
* 12 &mdash; move to position 12
* 123 &mdash; move to position 123

The custom implementation emits the [editingFinished][msl.qt.binding.QtWidgets.QAbstractSpinBox.editingFinished] signal when any of the following events occur:

* the [DoubleSpinBox] loses focus
* the Enter key is pressed
* the Up, Down, PageUp or PageDown key is pressed
* the Increment or Decrement button is clicked

!!! example "Run the example"
    ```console
    python -c "from msl.examples.qt import run; run('SpinBox')"
    ```

    ??? abstract "Click to view the example source code"
        <!-- fmt: off -->
        ```python
        --8<-- "src/msl/examples/qt/spinbox.py"
        ```
        <!-- fmt: on -->

!!! note "See Also"
    [SpinBox][] to enter an integer value.

::: msl.qt.widgets.spinbox.DoubleSpinBox
    options:
        show_root_full_path: false
        show_root_heading: true
        filters: ["!(^_|fixup|stepBy|setValue|textFromValue|validate|valueFromText)"]

[DoubleSpinBox]: #msl.qt.widgets.spinbox.DoubleSpinBox
