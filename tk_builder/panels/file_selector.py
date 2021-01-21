"""
A common use file selector.
"""

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


import os
from tkinter.filedialog import askopenfilename, asksaveasfilename

from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import basic_widgets
from tk_builder.widgets import widget_descriptors


class FileSelector(WidgetPanel):
    """
    File selector interface.  Provides a button for the user to press to select
    a filename.

    The selected filename is accessible in the property "file_name". A label displays
    the selected file name for easy reference.
    """

    _widget_list = ("select_file", "fname_label")
    select_file = widget_descriptors.ButtonDescriptor(
        "select_file", default_text="file selector")  # type: basic_widgets.Button
    fname_label = widget_descriptors.LabelDescriptor(
        "fname_label", default_text="")   # type: basic_widgets.Label

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent
            The parent widget.
        """
        self._file_name = None
        WidgetPanel.__init__(self, parent)
        self.config(borderwidth=0)

        self.init_w_horizontal_layout()
        self.fname_filters = [('All Files', '*')]
        # in practice this would be overridden if the user wants more things to happen after selecting a file.
        self.select_file.config(command=self.select_file_command)
        self.browse_directory = os.path.expanduser("~")
        self.fname_label.config(state='disabled')

    @property
    def file_name(self):
        """
        str: The selected file name.
        """

        return self._file_name

    def set_fname_filters(self, filter_list):
        """

        Parameters
        ----------
        filter_list
            This is a list of tuples of the form `[(<name for filter>, <filter expression>)]`,
            where `<filter expression>` is a regular expression or list of regular expressions.

        Returns
        -------
        None
        """

        self.fname_filters = filter_list

    def event_select_file(self, event):
        """
        The file selection event.

        Parameters
        ----------
        event

        Returns
        -------
        str
        """

        self.select_file_command()

    def select_file_command(self):
        """
        Select file command callback.

        Returns
        -------
        str
        """

        fname = askopenfilename(initialdir=self.browse_directory, filetypes=self.fname_filters)
        if fname:
            self.browse_directory = os.path.split(fname)[0]
            self.fname_label.set_text(fname)
            self._file_name = fname
        return fname

    def event_new_file(self, event):
        """
        The new file selection event.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        fname = asksaveasfilename(initialdir=self.browse_directory, filetypes=self.fname_filters)
        if fname:
            self.fname_label.config(text=fname)
            self.browse_directory = os.path.split(fname)[0]
            self._file_name = fname
