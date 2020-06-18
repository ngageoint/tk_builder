from tkinter import ttk
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents


class Scale(ttk.Scale, WidgetEvents):
    def __init__(self, master=None, **kw):
        ttk.Scale.__init__(self, master, **kw)
