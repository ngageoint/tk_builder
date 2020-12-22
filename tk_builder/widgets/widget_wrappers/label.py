import tkinter
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class Label(tkinter.Label, WidgetEvents):
    def __init__(self, master=None, cnf=None, **kw):
        cnf = {} if cnf is None else cnf
        tkinter.Label.__init__(self, master=master, cnf=cnf, **kw)

    def set_text(self, txt):
        self.config(text=txt)

    def get_text(self):
        return self.cget("text")
