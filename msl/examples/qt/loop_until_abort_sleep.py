"""
Illustrates the use of the :class:`~msl.qt.loop_until_abort.LoopUntilAbort` class
in *single shot* mode using a random :class:`~msl.qt.sleep.Sleep` time.
"""
import random

from msl.qt import LoopUntilAbort, Sleep


class LoopExampleSleep(LoopUntilAbort):

    def __init__(self):
        # initialize the LoopUntilAbort class in single-shot mode
        super(LoopExampleSleep, self).__init__(single_shot=True)

        # create the Sleep thread which uses SleepWorker as the worker class
        self.sleep = Sleep()

        # call self.update_status_bar_text when sleeping is done
        self.sleep.add_callback(self.update_status_bar_text)

        # just for fun, add another callback to be called when sleeping is finished
        self.sleep.add_callback(self.countdown)

    def countdown(self):
        if self.iteration == 10:
            # stop being notified of the countdown
            self.sleep.remove_callback(self.countdown)
        print('countdown: ' + str(10 - self.iteration))

    def update_status_bar_text(self):
        print('finished loop #: ' + str(self.iteration))

        # you can access attributes from the SleepWorker class
        self.set_status_bar_text('Slept for {:.3f} seconds'.format(self.sleep.seconds))

        # run the loop one more time (only if the loop's QTimer still exists)
        # NOTE: do not call self.loop() directly, you should call self.loop_once()
        if self.loop_timer is not None:
            self.loop_once()

    def loop(self):
        print('started loop #: ' + str(self.iteration))

        # pick a random number of seconds to sleep for
        callback_after_this_many_seconds = random.randint(100, 2000) * 1e-3

        # the `callback_after_this_many_seconds` parameter gets passed to the
        # constructor of the SleepWorker class and the Sleep thread starts
        self.sleep.start(callback_after_this_many_seconds)

        # the self.sleep.start() call does not block (if it did the GUI would freeze)
        # so any code that is after it will be executed immediately -- this is why
        # the text of the "label" gets updated immediately
        self.set_label_text('Sleeping for {:.3f} seconds'.format(callback_after_this_many_seconds))

        # since we added callbacks to the self.sleep instance the callbacks
        # will be called after `callback_after_this_many_seconds` seconds
        # and then the loop is run again

    def cleanup(self):
        # let's be nice and wait for the Sleep thread to finish before exiting the program
        # waiting is a blocking call so the GUI will be frozen while it is closing
        self.sleep.remove_callback(self.update_status_bar_text)  # not really necessary...
        self.sleep.quit()
        self.sleep.wait()


def main():
    loop = LoopExampleSleep()
    loop.start()


if __name__ == '__main__':
    main()
