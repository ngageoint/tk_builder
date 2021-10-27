"""
Some commonly used derived widgets ready for extension.
"""

__classification__ = 'UNCLASSIFIED'
__author__ = "Thomas McCullough"

import tkinter
from tk_builder.widgets.basic_widgets import Frame, Scrollbar, Treeview, Text
from tk_builder.widgets.widget_descriptors import TypedDescriptor


class TreeviewWithScrolling(Treeview):
    """
    A treeview widget with integrated vertical and horizontal
    scrollbars embedded in a frame.

    IMPORTANT! This treeview is implicitly embedded in a frame, so you have
    to apply pack commands to <instance>.frame versus <instance>.
    """

    frame = TypedDescriptor('frame', Frame)
    xscroll = TypedDescriptor('xscroll', Scrollbar)  # type: Scrollbar
    yscroll = TypedDescriptor('yscroll', Scrollbar)  # type: Scrollbar

    def __init__(self, master, **kwargs):
        self.frame = Frame(master)

        # instantiate the scroll bar and bind scrolling commands
        self.yscroll = Scrollbar(self.frame, orient=tkinter.VERTICAL)
        self.yscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.xscroll = Scrollbar(self.frame, orient=tkinter.HORIZONTAL)
        self.xscroll.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        kwargs.update({'yscrollcommand': self.yscroll.set, 'xscrollcommand': self.xscroll.set})

        Treeview.__init__(self, self.frame, **kwargs)
        self.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
        self.yscroll['command'] = self.yview
        self.xscroll['command'] = self.xview

    def set_selection_with_expansion(self, item_id):
        def expand_parent(iid):
            parent = self.parent(iid)
            if parent == '':
                return
            else:
                self.item(parent, open=True)
                expand_parent(parent)
        if item_id is None or item_id == '':
            return
        expand_parent(item_id)
        self.selection_set(item_id)
        self.focus(item_id)

    def __str__(self):
        return str(self.frame)


class TextWithScrolling(Text):
    """
    A text widget with integrated vertical and horizontal scrollbars, embedded in a frame.

    IMPORTANT! This treeview is implicitly embedded in a frame, so you have
    to apply pack commands to <instance>.frame versus <instance>.
    """

    frame = TypedDescriptor('frame', Frame)
    xscroll = TypedDescriptor('xscroll', Scrollbar)  # type: Scrollbar
    yscroll = TypedDescriptor('yscroll', Scrollbar)  # type: Scrollbar

    def __init__(self, master, **kwargs):
        self.frame = Frame(master)

        # instantiate the scroll bar and bind scrolling commands
        self.yscroll = Scrollbar(self.frame, orient=tkinter.VERTICAL)
        self.yscroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.xscroll = Scrollbar(self.frame, orient=tkinter.HORIZONTAL)
        self.xscroll.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        kwargs.update({'yscrollcommand': self.yscroll.set, 'xscrollcommand': self.xscroll.set})

        if 'wrap' not in kwargs:
            kwargs['wrap'] = tkinter.NONE
        Text.__init__(self, self.frame, **kwargs)
        self.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
        self.yscroll['command'] = self.yview
        self.xscroll['command'] = self.xview

    def set_value(self, value):
        """
        Set the value.

        Parameters
        ----------
        value : None|str
        """

        if not isinstance(value, str):
            raise TypeError('The value must be a str instance')

        self.delete('1.0', 'end')
        self.insert(tkinter.END, value)

    def get_value(self):
        """
        Fetches the populated value.

        Returns
        -------
        str
        """

        return self.get("1.0", 'end')

    def __str__(self):
        return str(self.frame)
