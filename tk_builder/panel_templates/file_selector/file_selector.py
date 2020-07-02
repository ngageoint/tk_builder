import os
import tkinter
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tk_builder.panel_templates.widget_panel.widget_panel import AbstractWidgetPanel
from tk_builder.widgets import basic_widgets


class FileSelector(AbstractWidgetPanel):
    """
    File selector interface.
    """

    select_file = basic_widgets.Button  # type: basic_widgets.Button
    fname_label = basic_widgets.Entry   # type: basic_widgets.Label

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent
            The parent widget.
        """

        AbstractWidgetPanel.__init__(self, parent)
        tkinter.LabelFrame.__init__(self, parent)
        self.config(borderwidth=2)
        self.fname = None

        widget_list = ["select_file", "fname_label"]
        self.init_w_horizontal_layout(widget_list)
        self.set_label_text("file selector")
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
