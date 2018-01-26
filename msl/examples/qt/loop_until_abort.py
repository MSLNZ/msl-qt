"""
Example script to repeatedly write data to a file until aborted by the user.
"""
import tempfile

from msl.qt import prompt, LoopUntilAbort


class LoopExample(LoopUntilAbort):

    def __init__(self):
        """Initialize the LoopUntilAbort class and create a file to write data to.

        Use a 250 ms delay between successive calls to the `loop` method.
        """
        super(LoopExample, self).__init__(loop_delay=250)

        self.output_path = tempfile.gettempdir() + '/msl-qt-loop-until-abort.txt'
        self.f = open(self.output_path, 'w')
        self.f.write('Started at {}\n'.format(self.current_time))

    def loop(self):
        """This method gets called repeatedly in a loop (every `loop_delay` ms)."""
        self.f.write('Iteration: {}\n'.format(self.iteration))
        self.f.write('Elapsed time: {}\n'.format(self.elapsed_time))
        self.set_label_text('The current time is\n' + str(self.current_time))

    def cleanup(self):
        """This method gets called when the LoopExample window is closing."""
        self.f.write('Stopped at {}\n'.format(self.current_time))
        self.f.close()
        msg = 'The data was save to\n{}\n\n... in case you want to look at it'
        prompt.information(msg.format(self.output_path))


def main():
    loop = LoopExample()
    loop.start()


if __name__ == '__main__':
    main()
