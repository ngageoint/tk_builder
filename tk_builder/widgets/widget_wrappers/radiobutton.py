from tkinter import ttk
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class RadioButton(ttk.Radiobutton, WidgetEvents):
    def __init__(self, master=None, **kw):
        ttk.Radiobutton.__init__(self, master, **kw)

    def set_text(self, text):
        self.config(text=text)
