import tkinter
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class Entry(tkinter.Entry, WidgetEvents):
    def __init__(self, master=None, cnf=None, **kw):
        cnf = {} if cnf is None else cnf
        tkinter.Entry.__init__(self, master=master, cnf=cnf, **kw)

    def set_text(self, text):
        # handle case if the widget is disabled
        entry_state = self['state']
        if entry_state == 'disabled':
            self.config(state='normal')
        self.delete(0, tkinter.END)
        self.insert(0, text)
        if entry_state == 'disabled':
            self.config(state='disabled')
