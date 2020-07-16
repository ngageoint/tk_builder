from tkinter import ttk
from tk_builder.widgets.widget_utils.widget_events import WidgetEvents


class Combobox(ttk.Combobox, WidgetEvents):
    def __init__(self, master=None, **kw):
        ttk.Combobox.__init__(self, master, **kw)

    def set_text(self, text):
        self.config(text=text)

    def on_selection(self, event):
        self.bind("<<ComboboxSelected>>", event)

    def update_combobox_values(self, val_list):
        self['values'] = val_list
        self.current(0)
