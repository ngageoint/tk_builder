import os
import tkinter
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import basic_widgets
from tk_builder.widgets import widget_descriptors


class FileSelector(WidgetPanel):
    """
    File selector interface.
    """
    _widget_list = ("select_file", "fname_label")
    select_file = widget_descriptors.ButtonDescriptor(
        "select_file", default_text="file selector")  # type: basic_widgets.Button
    fname_label = widget_descriptors.LabelDescriptor("fname_label", default_text="")   # type: basic_widgets.Label

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent
            The parent widget.
        """

        WidgetPanel.__init__(self, parent)
        tkinter.LabelFrame.__init__(self, parent)
        self.config(borderwidth=0)
        self.fname = None

        self.init_w_horizontal_layout()
        self.fname_filters = [('All files', '*')]
        # in practice this would be overridden if the user wants more things to happen after selecting a file.
        self.select_file.on_left_mouse_click(self.event_select_file)
        self.initialdir = os.path.expanduser("~")
        self.fname_label.config(state='disabled')

    def set_fname_filters(self, filter_list):
        """

        Parameters
        ----------
        filter_list : List[str]

        Returns
        -------
        None
        """

        self.fname_filters = filter_list

    def set_initial_dir(self, directory):
        """
        Set the initial directory, the default opening location.

        Parameters
        ----------
        directory : str

        Returns
        -------
        None
        """

        self.initialdir = directory

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

        self.fname = askopenfilename(initialdir=self.initialdir, filetypes=self.fname_filters)
        self.fname_label.set_text(self.fname)
        return self.fname

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

        self.fname = asksaveasfilename(initialdir=self.initialdir, filetypes=self.fname_filters)
        self.fname_label.config(text=self.fname)
