import tkinter
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents


class LabelFrame(tkinter.LabelFrame, WidgetEvents):
    def __init__(self, master=None, cnf=None, **kw):
        cnf = {} if cnf is None else cnf
        tkinter.LabelFrame.__init__(self, master=master, cnf=cnf, **kw)

    def set_text(self, text):
        self.config(text=text)
