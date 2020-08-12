from tkinter import ttk
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents


class RadioButton(ttk.Radiobutton, WidgetEvents):
    def __init__(self, master=None, **kw):
        ttk.Radiobutton.__init__(self, master, **kw)
        # TODO: ERROR - is it ttk.Radiobutton or tkinter.Radiobutton? The inheritance and super call clash.

    def set_text(self, text):
        self.config(text=text)
