import tkinter
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class CheckButton(tkinter.Checkbutton, WidgetEvents):
    def __init__(self, master=None, cnf=None, **kw):
        cnf = {} if cnf is None else cnf
        self.value = tkinter.BooleanVar()
        tkinter.Checkbutton.__init__(self, master=master, cnf=cnf, var=self.value, **kw)
        self.value.set(False)

    def set_text(self, text):
        self.config(text=text)

    def is_selected(self):
        return self.value.get()
