"""
A :class:`~msl.qt.widget.button.Button` example.
"""
from msl.qt import application, Button


def left():
    print('left click')


def right():
    print('right click')


def item1():
    print('item #1 selected')


def item2():
    print('item #2 selected')


def item3():
    print('item #3 selected')


def item4():
    print('item #4 selected')


def show():
    app = application()
    b = Button(text='My button', icon=32, icon_size=4., left_click=left, tooltip='Example button')
    b.set_right_click(right)
    b.add_menu_item(text='My item #1', triggered=item1, shortcut='CTRL+I', icon=43)
    b.add_menu_item(text='My item #2', triggered=item2, icon=47, tooltip='Second')
    b.add_menu_item(text='My item #3', shortcut='CTRL+Z', icon=46, tooltip='Visible but disabled (triggered not set)')
    b.add_menu_separator()
    b.add_menu_item(text='My item #4', triggered=item4, tooltip='Fourth')
    b.show()
    app.exec_()


if __name__ == '__main__':
    show()
