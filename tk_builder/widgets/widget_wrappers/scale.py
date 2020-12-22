from tkinter import ttk
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class Scale(ttk.Scale, WidgetEvents):
    def __init__(self, master=None, **kw):
        ttk.Scale.__init__(self, master, **kw)

