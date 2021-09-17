__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


from typing import List, Generator
import numpy
import tkinter
from tkinter import ttk

from tk_builder.widgets import basic_widgets


class _BaseWidgetPanel(object):
    """
    This lays out the basic convenience building block for tool to allow simple
    construction and packing of the tkinter elements. This is just a packing
    convenience, and can be safely approached in other ways.

    When creating the subclass definition the following CLASS variable should be
    set `_widget_list` which should be a tuple of strings that define the widgets
    that will be incorporated into the panel.

    Next, descriptors should created that correspond to the elements within `_widget_list`.
    The descriptor definitions are located in `tk_builder.widgets.widget_descriptors`.
    Each descriptor should have a variable name that matches a string within `_widget_list`.

    The panel will be packed by calling one of the following methods:
      * `init_w_horizontal_layout`
      * `init_w_vertical_layout`
      * `init_w_rows`
      * `init_w_box_layout`
      * `init_w_basic_widget_list`
    """

    _widget_list = ()  # the list of names of the widget element variables
    padx = 5
    pady = 5

    def __init__(self, master):
        self.master = master
        self._rows = []  # type: List[basic_widgets.Frame]

    def _widget_objects(self, subtype_filter=None):
        """
        Create an iterator over the widget objects.

        Parameters
        ----------
        subtype_filter : None|type|Tuple[type]

        Returns
        -------
        Generator[tkinter.Widget]
        """

        for widget_name in self._widget_list:
            widget = getattr(self, widget_name)
            if subtype_filter is None or isinstance(widget, subtype_filter):
                yield widget

    def init_w_horizontal_layout(self):
        """
        Creates the layout of the panel with all widgets laid out horizontally
        """

        self.init_w_basic_widget_list(n_rows=1, n_widgets_per_row_list=[len(self._widget_list), ])

    def init_w_vertical_layout(self):
        """
        Creates the layout of the panel with all widgets laid out vertically
        """

        self.init_w_basic_widget_list(n_rows=len(self._widget_list),
                                      n_widgets_per_row_list=[1, ] * len(self._widget_list))

    def init_w_rows(self):
        """
        Creates the layout of the panel with all widgets laid out corresponding
        to the structure of _widget_list. In this case _widget_list consists of
        nested tuples.  The outer elements represent each row, and the nested
        elements represent the number of columns within each row.

        For example, suppose `_widget_list = (("one", "two", ), ("three", "four", "five"))`
        When initialized with `init_w_rows`, the layout will have two rows. The
        top row will consist of widgets `one` and two`, laid out horizontally.
        The bottom row will consist of widgets `three`, `four`, and `five`, laid
        out horizontally.
        """

        flattened_list = []
        widgets_per_row = []
        for widget_list in self._widget_list:
            widgets_per_row.append(len(widget_list))
            for widget in widget_list:
                flattened_list.append(widget)
        self._widget_list = tuple(flattened_list)
        self.init_w_basic_widget_list(len(widgets_per_row), widgets_per_row)

    def init_w_box_layout(self, n_columns, column_widths=None, row_heights=None):
        """
        Create the layout of the panel with a box layout defined by a certain number
        of columns. It is assumed that elements of `_widget_list` are defined
        sequentially, and the layout is defined across columns first.

        NOTE! This will fail if `_widget_list` is not a flat list.

        For example, suppose `_widget_list = ("one", "two", "three", "four", "five" "six")`.
        Initializing with `init_w_box_layout`, the layout will be 3 rows of 2 columns each.
        The first row containing `one`, `two`, the second row containing `three`, `four`,
        and the third row containing `five`, `six` with each laid out horizontally.

        Parameters
        ----------
        n_columns : int
        column_widths : None|int|List[int]
        row_heights : None|int|List[int]

        Returns
        -------
        None
        """

        n_total_widgets = len(self._widget_list)
        n_rows = int(numpy.ceil(n_total_widgets / n_columns))
        n_widgets_per_row = []
        n_widgets_left = n_total_widgets
        for i in range(n_rows):
            n_widgets = n_widgets_left / n_columns
            if n_widgets >= 1:
                n_widgets_per_row.append(n_columns)
            else:
                n_widgets_per_row.append(n_widgets_left)
            n_widgets_left -= n_columns

        self.init_w_basic_widget_list(n_rows, n_widgets_per_row)

        for i, widget in enumerate(self._widget_list):
            column_num = (i % n_columns)
            row_num = int(i/n_columns)
            if column_widths is not None:
                if isinstance(column_widths, int):
                    getattr(self, widget).config(width=column_widths)
                else:
                    col_width = column_widths[column_num]
                    getattr(self, widget).config(width=col_width)

            if row_heights is not None:
                if isinstance(row_heights, int):
                    # noinspection PyBroadException
                    try:
                        getattr(self, widget).config(height=row_heights)
                    except Exception:
                        pass  # some widgets don't have a height
                else:
                    row_height = row_heights[row_num]
                    # noinspection PyBroadException
                    try:
                        getattr(self, widget).config(height=row_height)
                    except Exception:
                        pass

    def init_w_basic_widget_list(self, n_rows, n_widgets_per_row_list):
        """
        This is a convenience method to initialize a basic widget panel, and
        should also be the primary method to initialize a panel.

        Other convenience methods can be made to perform the button/widget location
        initialization, but all of those methods should perform their ordering,
        then reference this method to actually perform the initialization.

        Parameters
        ----------
        n_rows : int
        n_widgets_per_row_list : List[int]

        Returns
        -------
        None
        """

        if n_rows != len(n_widgets_per_row_list):
            raise ValueError(
                'Argument mismatch for class {}. The number of rows must match the '
                'length of the provided list.'.format(self.__class__))

        self._rows = [basic_widgets.Frame(self) for _ in range(n_rows)]
        for row in self._rows:
            row.config(borderwidth=2)
            row.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        # find transition points
        transitions = numpy.cumsum(n_widgets_per_row_list)
        row_num = 0

        for i, widget_name in enumerate(self._widget_list):
            widget_descriptor = getattr(self.__class__, widget_name, None)

            if widget_descriptor is None:
                raise ValueError(
                    'widget class {} has no widget descriptor named {}. The tk_builder init...() '
                    'methods cannot be used for initialization without the descriptor pattern.'.format(
                        self.__class__.__name__, widget_name))

            if widget_name != widget_descriptor.name:
                raise ValueError(
                    'widget {} of class {} has inconsistent name {}'.format(
                        widget_name, self.__class__.__name__, widget_descriptor.name))

            widget_type = widget_descriptor.the_type

            # check whether things have been instantiated
            current_value = getattr(self, widget_name)
            if current_value is not None:
                current_value.destroy()

            if i in transitions:
                row_num += 1

            try:
                widget_text = widget_descriptor.default_text
            except AttributeError:
                widget_text = None
            widget = widget_type(self._rows[row_num])
            widget.pack(side="left", padx=self.padx, pady=self.pady, fill=tkinter.BOTH, expand=tkinter.YES)
            if hasattr(widget_type, 'set_text') and widget_text is not None:
                widget.set_text(widget_text.replace("_", " "))
            setattr(self, widget_name, widget)
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def disable_all_widgets(self):
        """
        Disables all widgets. This may be an appropriate first step in an
        application where a user may be required to take initialization steps.
        """

        for widget in self._widget_objects():
            widget.config(state="disabled")
            # noinspection PyBroadException
            try:
                widget.config(state="disabled")
            except Exception:
                if isinstance(widget, ttk.Widget):
                    widget.state(['disabled'])

    def enable_all_widgets(self):
        """
        Enables all widgets within a panel.
        """

        for widget in self._widget_objects():
            # noinspection PyBroadException
            try:
                widget.config(state="normal")
            except Exception:
                if isinstance(widget, ttk.Widget):
                    widget.state(['!disabled'])

    def forget_row(self, row_value):
        if row_value < 0 or row_value >= len(self._rows):
            return
        self._rows[row_value].pack_forget()

    def pack_row(self, row_value):
        if row_value < 0 or row_value >= len(self._rows):
            return
        self._rows[row_value].pack()


class WidgetPanel(basic_widgets.LabelFrame, _BaseWidgetPanel):
    def __init__(self, master):
        _BaseWidgetPanel.__init__(self, master)
        basic_widgets.LabelFrame.__init__(self, master)
        self.config(borderwidth=2)

    def close_window(self):
        self.master.withdraw()


class WidgetPanelNoLabel(basic_widgets.Frame, _BaseWidgetPanel):
    def __init__(self, master):
        _BaseWidgetPanel.__init__(self, master)
        basic_widgets.Frame.__init__(self, master)
        self.config(borderwidth=2)

    def close_window(self):
        self.master.withdraw()


class RadioButtonPanel(WidgetPanel):
    """
    This is a WidgetPanel specifically for building panels that contain radio
    buttons.  A subclass of RadioButtonPanel should be created to create a
    custom panel of radiobuttons.
    """

    def __init__(self, master):
        self._selection_dict = {}
        WidgetPanel.__init__(self, master)
        self._selected_value = tkinter.IntVar()

    def init_w_vertical_layout(self):
        WidgetPanel.init_w_vertical_layout(self)
        self._setup_radiobuttons()

    def init_w_horizontal_layout(self):
        WidgetPanel.init_w_horizontal_layout(self)
        self._setup_radiobuttons()

    def init_w_basic_widget_list(self, n_rows, n_widgets_per_row_list):
        WidgetPanel.init_w_basic_widget_list(self, n_rows, n_widgets_per_row_list)
        self._setup_radiobuttons()

    def init_w_box_layout(self, n_columns, column_widths=None,  row_heights=None):
        WidgetPanel.init_w_box_layout(self,
                                      n_columns,
                                      column_widths=column_widths,
                                      row_heights=row_heights)
        self._setup_radiobuttons()

    def _setup_radiobuttons(self):
        for i, button in enumerate(self._widget_objects()):
            self._selection_dict[str(i)] = button
            button.config(variable=self._selected_value, value=i)
        self._selected_value.set(0)

    def selection(self):
        val = self._selected_value.get()
        return self._selection_dict[str(val)]

    def set_selection(self, value):
        self._selected_value.set(value)
