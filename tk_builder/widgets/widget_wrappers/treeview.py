from tkinter import ttk
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class Treeview(ttk.Treeview, WidgetEvents):
    def __init__(self, master=None, **kw):
        ttk.Treeview.__init__(self, master, **kw)

    def on_selection(self, callback, *args, **kwargs):
        self.event_binding('<<TreeviewSelect>>', callback, *args, **kwargs)
