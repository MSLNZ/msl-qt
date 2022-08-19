"""
Example script to repeatedly write data to a file until aborted by the user.
"""
import tempfile

from msl.qt import (
    prompt,
    LoopUntilAbort
)


class LoopExample(LoopUntilAbort):

    def __init__(self):
        """Initialize the LoopUntilAbort class and create a file to write data to.

        Use a 250 ms delay between successive calls to the `loop` method.
        """
        super(LoopExample, self).__init__(loop_delay=250)

        self.output_path = tempfile.gettempdir() + '/msl-qt-loop-until-abort.txt'
        self.f = open(self.output_path, mode='wt')
        self.f.write(f'Started at {self.current_time}\n')

    def loop(self):
        """Overrides LoopUntilAbort.loop()

        This method gets called repeatedly in a loop (every `loop_delay` ms).
        """
        self.f.write(f'Iteration: {self.iteration}\n')
        self.f.write(f'Elapsed time: {self.elapsed_time}\n')
        self.set_label_text(f'The current time is\n{self.current_time}')

    def cleanup(self):
        """Overrides LoopUntilAbort.cleanup()

        This method gets called when the LoopExample window is closing.
        """
        self.f.write(f'Stopped at {self.current_time}\n')
        self.f.close()
        prompt.information(f'The data was save to\n{self.output_path}\n\n'
                           f'... in case you want to look at it')


def main():
    loop = LoopExample()
    loop.start()


if __name__ == '__main__':
    main()
