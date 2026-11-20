# threading

Base classes for running a process in a background [QThread][msl.qt.binding.QtCore.QThread].

When you run a process in the main event loop of the application, the graphical user interface (GUI) will be frozen until the process completes. For long-running processes, this will make your GUI annoyingly unresponsive. The [Worker][msl.qt.threading.Worker] and [Thread][msl.qt.threading.Thread] classes provide a way to run a process in a background thread so that the main application window remains responsive.

The [Worker][msl.qt.threading.Worker] and [Thread][msl.qt.threading.Thread] classes are sub-classed in your application. The process to run is implemented in the overridden [Worker.process()][msl.qt.threading.Worker.process] method. These classes are importable at the top level, i.e.,

```pycon
>>> from msl.qt import Thread, Worker

```

As an example, [SleepWorker][msl.qt.threading.SleepWorker] is a class that implements [Worker][msl.qt.threading.Worker] and [Sleep][msl.qt.threading.Sleep] implements [Thread][msl.qt.threading.Thread].

!!! example "Run the example"
    ```console
    python -c "from msl.examples.qt import run; run('LoopSleep')"
    ```

    ??? abstract "Click to view the example source code"
        ```python
        --8 < --"src/msl/examples/qt/loop_until_abort_sleep.py"
        ```

::: msl.qt.threading.Worker
    options:
        show_root_heading: true

::: msl.qt.threading.Thread
    options:
        show_root_heading: true
        filters: ["!(^_[a-z])"]

::: msl.qt.threading.SleepWorker
    options:
        show_root_heading: true

::: msl.qt.threading.Sleep
    options:
        show_root_heading: true
