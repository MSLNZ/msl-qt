from msl.qt import Signal, Slot, Thread, Worker


class MyWorker(Worker):
    value_changed: Signal = Signal(float, name="valueChanged")

    def process(self) -> None:
        """Implement the blocking code here."""


@Slot(float)
def on_value_changed(value: float) -> None:
    """Slot to handle the `MyWorker.valueChanged` signal."""


t = Thread(worker=MyWorker)

# These are equivalent ways to connect the Signal of MyWorker to the Slot
# after `MyWorker` has been moved to the QThread
t.worker_connect("value_changed", on_value_changed)  # class attribute name
t.worker_connect("valueChanged", on_value_changed)  # Signal name parameter
t.worker_connect(MyWorker.value_changed, on_value_changed)  # Signal object

t.start()


# The following lines are excluded from the docstring.
#
# Fixes
#   RuntimeError: wrapped C/C++ object of type MyWorker has been deleted
# when running the tests on GitHub when using macOS as the runner image
from msl.qt import application  # noqa: E402

app = application()
while t.is_running():
    _ = t.wait(100)
    app.processEvents()
