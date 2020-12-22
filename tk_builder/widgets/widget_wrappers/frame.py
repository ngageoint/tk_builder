import tkinter
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class Frame(tkinter.Frame, WidgetEvents):
    def __init__(self, master=None, cnf=None, **kw):
        cnf = {} if cnf is None else cnf
        tkinter.Frame.__init__(self, master=master, cnf=cnf, **kw)
