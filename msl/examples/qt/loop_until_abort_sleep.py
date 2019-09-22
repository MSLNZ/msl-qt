"""
Illustrates the use of the :class:`~msl.qt.loop_until_abort.LoopUntilAbort` class
in *single shot* mode using a random :class:`~msl.qt.sleep.Sleep` time.
"""
import random

from msl.qt import LoopUntilAbort, Sleep


class LoopExampleSleep(LoopUntilAbort):

    def __init__(self):
        """Initialize the LoopUntilAbort class in single-shot mode."""
        super(LoopExampleSleep, self).__init__(single_shot=True)

        # create the Sleep thread which uses SleepWorker as the worker class
        self.sleep = Sleep()

        # call self.update_status_bar_text when sleeping is finished
        self.sleep.finished.connect(self.update_status_bar_text)

        # just for fun, add another slot to be called when sleeping is finished
        self.sleep.finished.connect(self.countdown)

    def countdown(self):
        if self.iteration == 5:
            # stop being notified of the countdown
            self.sleep.finished.disconnect(self.countdown)
        print('countdown: ' + str(5 - self.iteration))

    def update_status_bar_text(self):
        print('finished loop #: ' + str(self.iteration))

        # you can access attributes from the SleepWorker class, i.e., self.sleep.seconds
        self.set_status_bar_text('Slept for {:.3f} seconds'.format(self.sleep.seconds))

        # run the loop one more time (only if the loop's QTimer still exists)
        # NOTE: do not call self.loop() directly, you should call self.loop_once()
        if self.loop_timer is not None:
            self.loop_once()

    def loop(self):
        """Overrides LoopUntilAbort.loop()"""

        print('started loop #: ' + str(self.iteration))

        # pick a random number of seconds to sleep for
        sleep_for_this_many_seconds = random.randint(100, 2000) * 1e-3

        # the `sleep_for_this_many_seconds` parameter gets passed to the
        # constructor of the SleepWorker class and the Sleep thread starts
        self.sleep.start(sleep_for_this_many_seconds)

        # the self.sleep.start() call does not block (if it did the GUI would freeze)
        # so any code that is after it will be executed immediately -- this is why
        # the text of the "label" gets updated immediately
        self.set_label_text('Sleeping for {:.3f} seconds'.format(sleep_for_this_many_seconds))

    def cleanup(self):
        """Overrides LoopUntilAbort.cleanup()"""

        # let's be nice and stop the Sleep thread before exiting the program
        # waiting for the thread to stop is a blocking call so the GUI will be frozen while it is closing
        self.sleep.stop()


def main():
    loop = LoopExampleSleep()
    loop.start()


if __name__ == '__main__':
    main()
