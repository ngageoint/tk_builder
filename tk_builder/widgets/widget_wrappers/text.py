import tkinter
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents


class Text(tkinter.Text, WidgetEvents):
    def __init__(self, master=None, cnf=None, **kw):
        cnf = {} if cnf is None else cnf
        tkinter.Text.__init__(self, master=master, cnf=cnf, **kw)
