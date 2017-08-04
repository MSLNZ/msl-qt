"""
Example script to repeatedly write data to a file until aborted by the user.
"""
from msl.qt import LoopUntilAbort


class LoopExample(LoopUntilAbort):

    def __init__(self):
        """Initialize the dialog window.

        Use a 250 ms delay between successive calls to the loop method."""
        super(LoopExample, self).__init__(loop_delay=250)

    def setup(self):
        """This method gets called before looping starts."""
        self.f = open('loop_until_abort.txt', 'w')
        self.f.write('Started: {}\n'.format(self.start_time))

    def loop(self):
        """This method gets called repeatedly in a loop."""
        self.f.write('Counter: {}\n'.format(self.counter))
        self.f.write('Elapsed: {}\n'.format(self.elapsed_time))
        self.update_label('The current time is\n{}'.format(self.current_time))

    def teardown(self):
        """This method gets called after looping stops."""
        self.f.write('Stopped: {}\n'.format(self.current_time))
        self.f.close()


if __name__ == '__main__':
    LoopExample()
