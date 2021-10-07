"""
Some commonly used derived widgets ready for extension.
"""

__classification__ = 'UNCLASSIFIED'
__author__ = "Thomas McCullough"

import tkinter
from tk_builder.widgets.basic_widgets import Frame, Scrollbar, Treeview
from tk_builder.widgets.widget_descriptors import TypedDescriptor

class TreeviewWithScrolling(Treeview):
    """
    A treeview widget with integrated scrollbar embedded in a frame.
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

    def __str__(self):
        return str(self.frame)




