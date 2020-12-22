import tkinter
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class Button(tkinter.Button, WidgetEvents):
    def __init__(self, master=None, cnf=None, **kw):
        cnf = {} if cnf is None else cnf
        tkinter.Button.__init__(self, master=master, cnf=cnf, **kw)

    # event_handling
    def set_text(self, text):
        self.config(text=text)
