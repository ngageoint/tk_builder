from tkinter import ttk
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents


class Treeview(ttk.Treeview, WidgetEvents):
    def __init__(self, master=None, **kw):
        ttk.Treeview.__init__(self, master, **kw)

    # def set_text(self, text):
    #     self.config(text=text)
