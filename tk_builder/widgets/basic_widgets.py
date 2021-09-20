"""
Wrapping tkinter widgets to ensure simply and consistent event definitions and behavior.
"""


__classification__ = "UNCLASSIFIED"
__author__ = ("Jason Casey", "Thomas McCullough")

from typing import Callable

import tkinter
from tkinter import ttk

from tk_builder.widgets.widget_events import WidgetEvents


########
# The basic tkinter widgets with no ttk version

class Text(tkinter.Text, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        tkinter.Text.__init__(self, master=master, **kwargs)


class Canvas(tkinter.Canvas, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        tkinter.Canvas.__init__(self, master=master, **kwargs)


#########
# The basic tkinter widget, where we can use the ttk version

class Button(ttk.Button, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.Button.__init__(self, master=master, **kwargs)

    # event_handling
    def set_text(self, text):
        self.config(text=text)


class CheckButton(ttk.Checkbutton, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        self.value = tkinter.BooleanVar()
        ttk.Checkbutton.__init__(self, master=master, var=self.value, **kwargs)
        self.value.set(False)

    def set_text(self, text):
        self.config(text=text)

    def is_selected(self):
        return self.value.get()


class Entry(tkinter.Entry, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        self._text_variable = kwargs.get('textvariable', tkinter.StringVar())
        kwargs['textvariable'] = self._text_variable
        tkinter.Entry.__init__(self, master=master, **kwargs)
        if 'text' in kwargs:
            self.set_text(kwargs['text'])

    def set_text(self, text):
        self._text_variable.set(text)


class Frame(ttk.Frame, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.Frame.__init__(self, master=master, **kwargs)


class Label(ttk.Label, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.Label.__init__(self, master=master, **kwargs)

    def set_text(self, txt):
        self.config(text=txt)

    def get_text(self):
        return self.cget("text")


class LabelFrame(ttk.LabelFrame, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.LabelFrame.__init__(self, master=master, **kwargs)

    def set_text(self, text):
        self.config(text=text)


class Menubutton(ttk.Menubutton, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.Menubutton.__init__(self, master=master, **kwargs)


class PanedWindow(ttk.PanedWindow, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.PanedWindow.__init__(self, master=master, **kwargs)


class RadioButton(ttk.Radiobutton, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.Radiobutton.__init__(self, master=master, **kwargs)

    def set_text(self, text):
        self.config(text=text)


class Scale(ttk.Scale, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.Scale.__init__(self, master=master, **kwargs)


class Scrollbar(ttk.Scrollbar, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.Scrollbar.__init__(self, master=master, **kwargs)


class Spinbox(tkinter.Spinbox, WidgetEvents):
    # NB: ttk.Spinbox is broken in Python 3.6, so use "non themed" tkinter version
    def __init__(self, master=None, **kwargs):
        self._text_variable = kwargs.get('textvariable', tkinter.StringVar())
        kwargs['textvariable'] = self._text_variable
        tkinter.Spinbox.__init__(self, master=master, **kwargs)

    def set_text(self, text):
        self._text_variable.set(text)


###########
# ttk only widgets

class Combobox(ttk.Combobox, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        self._text_variable = kwargs.get('textvariable', tkinter.StringVar())
        kwargs['textvariable'] = self._text_variable
        ttk.Combobox.__init__(self, master=master, **kwargs)

    def set_text(self, text):
        self._text_variable.set(text)

    def on_selection(self, callback, *args, **kwargs):
        """
        Binds the <<ComboboxSelected>> event.

        Parameters
        ----------
        callback : Callable
        """

        self.event_binding('<<ComboboxSelected>>', callback, *args, **kwargs)

    def update_combobox_values(self, val_list):
        self['values'] = val_list
        self.current(0)


class Notebook(ttk.Notebook, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.Notebook.__init__(self, master=master, **kwargs)

    def on_tab_changed(self, callback, *args, **kwargs):
        """
        Binds the <<NotebookTabChanged>> event.

        Parameters
        ----------
        callback : Callable
        """

        self.event_binding("<<NotebookTabChanged>>", callback, *args, **kwargs)


class Progressbar(ttk.Progressbar, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.Progressbar.__init__(self, master=master, **kwargs)


class Separator(ttk.Separator, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.Separator.__init__(self, master=master, **kwargs)


class Sizegrip(ttk.Sizegrip, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.Sizegrip.__init__(self, master=master, **kwargs)


class Treeview(ttk.Treeview, WidgetEvents):
    def __init__(self, master=None, **kwargs):
        ttk.Treeview.__init__(self, master=master, **kwargs)

    def on_open(self, callback, *args, **kwargs):
        """
        Binds the <<TreeviewOpen>> event.

        Parameters
        ----------
        callback : Callable
        """

        self.event_binding('<<TreeviewOpen>>', callback, *args, **kwargs)

    def on_close(self, callback, *args, **kwargs):
        """
        Binds the <<TreeviewClose>> event.

        Parameters
        ----------
        callback : Callable
        """

        self.event_binding('<<TreeviewClose>>', callback, *args, **kwargs)

    def on_selection(self, callback, *args, **kwargs):
        """
        Binds the <<TreeviewSelect>> event.

        Parameters
        ----------
        callback : Callable
        """

        self.event_binding('<<TreeviewSelect>>', callback, *args, **kwargs)
