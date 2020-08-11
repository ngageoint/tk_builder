import numpy as np
from typing import Union, List
import tkinter
from tk_builder.widgets import basic_widgets


class WidgetPanel(basic_widgets.LabelFrame):
    _widget_list = ()  # the list of names of the widget element variables
    padx = 5
    pady = 5

    def __init__(self, parent):
        self.parent = parent
        basic_widgets.LabelFrame.__init__(self, parent)
        self.config(borderwidth=2)

        self._rows = None  # type: List[basic_widgets.Frame]

    def close_window(self):
        self.parent.withdraw()

    def init_w_horizontal_layout(self):
        self.init_w_basic_widget_list(n_rows=1, n_widgets_per_row_list=[len(self._widget_list), ])

    def init_w_vertical_layout(self):
        self.init_w_basic_widget_list(n_rows=len(self._widget_list),
                                      n_widgets_per_row_list=[1, ] * len(self._widget_list))

    def init_w_rows(self):
        flattened_list = []
        widgets_per_row = []
        for widget_list in self._widget_list:
            widgets_per_row.append(len(widget_list))
            for widget in widget_list:
                flattened_list.append(widget)
        self._widget_list = tuple(flattened_list)
        self.init_w_basic_widget_list(len(self._widget_list), widgets_per_row)

    def init_w_box_layout(self,
                          n_columns,  # type: int
                          column_widths=None,  # type: Union[int, list]
                          row_heights=None,  # type: Union[int, list]
                          ):
        n_total_widgets = len(self._widget_list)
        n_rows = int(np.ceil(n_total_widgets / n_columns))
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
            column_num = np.mod(i, n_columns)
            row_num = int(i / n_columns)
            if column_widths is not None and isinstance(column_widths, type(1)):
                getattr(self, widget).config(width=column_widths)
            elif column_widths is not None and isinstance(column_widths, type([])):
                col_width = column_widths[column_num]
                getattr(self, widget).config(width=col_width)
            if row_heights is not None and isinstance(row_heights, type(1)):
                getattr(self, widget).config(height=row_heights)
            elif row_heights is not None and isinstance(row_heights, type([])):
                row_height = row_heights[row_num]
                getattr(self, widget).config(height=row_height)

    def init_w_basic_widget_list(self, n_rows, n_widgets_per_row_list):
        """
        This is a convenience method to initialize a basic widget panel.  To use this first make a subclass
        This should also be the primary method to initialize a panel.  Other convenience methods can be made
        to perform the button/widget location initialization, but all of those methods should perform their
        ordering then reference this method to actually perform the initialization.

        Parameters
        ----------
        n_rows : int
        n_widgets_per_row_list : List[int]

        Returns
        -------
        None
        """

        self._rows = [basic_widgets.Frame(self) for i in range(n_rows)]
        for row in self._rows:
            row.config(borderwidth=2)
            row.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        # find transition points
        transitions = np.cumsum(n_widgets_per_row_list)
        row_num = 0
        for i, widget_name in enumerate(self._widget_list):
            widget_descriptor = getattr(self.__class__, widget_name, None)
            if widget_descriptor is None:
                raise ValueError('widget class {} has no widget named {}'.format(self.__class__.__name__, widget_name))

            if widget_name != widget_descriptor.name:
                raise ValueError(
                    'widget {} of class {} has inconsistent name {}'.format(widget_name, self.__class__.__name__,
                                                                            widget_descriptor.name))

            widget_type = widget_descriptor.the_type

            # check whether things have been instantiated
            current_value = getattr(self, widget_name)
            if current_value is not None:
                current_value.destroy()

            if i in transitions:
                row_num += 1

            widget_text = widget_descriptor.default_text
            widget = widget_type(self._rows[row_num])
            widget.pack(side="left", padx=self.padx, pady=self.pady, fill=tkinter.BOTH, expand=tkinter.YES)
            if hasattr(widget_type, 'set_text') and widget_text is not None:
                widget.set_text(widget_text.replace("_", " "))
            setattr(self, widget_name, widget)
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def set_text_formatting(self, formatting_list):
        pass

    def set_spacing_between_buttons(self, spacing_npix_x=0, spacing_npix_y=None):
        if spacing_npix_y is None:
            spacing_npix_y = spacing_npix_x
        for widget in self._widget_list:
            getattr(self, widget).pack(side="left",
                                       padx=spacing_npix_x,
                                       pady=spacing_npix_y,
                                       fill=tkinter.BOTH,
                                       expand=tkinter.YES)

    def unpress_all_buttons(self):
        for widget in self._widget_list:
            if isinstance(getattr(self, widget), basic_widgets.Button):
                getattr(self, widget).config(relief="raised")

    def press_all_buttons(self):
        for widget in self._widget_list:
            if isinstance(getattr(self, widget), basic_widgets.Button):
                getattr(self, widget).config(relief="sunken")

    def enable_all_buttons(self):
        for widget in self._widget_list:
            if isinstance(getattr(self, widget), basic_widgets.Button):
                getattr(self, widget).config(state="normal")

    def disable_all_widgets(self):
        for widget in self._widget_list:
            getattr(self, widget).configure(state="disabled")

    def enable_all_widgets(self):
        for widget in self._widget_list:
            getattr(self, widget).config(state="normal")

    def set_active_button(self,
                          button,
                          ):
        self.unpress_all_buttons()
        self.enable_all_buttons()
        button.config(state="disabled")
        button.config(relief="sunken")


class RadioButtonPanel(WidgetPanel):
    _selection_dict = {}

    def __init__(self, parent):
        self.parent = parent
        WidgetPanel.__init__(self, parent)
        self._selected_value = tkinter.IntVar()

    def init_w_vertical_layout(self):
        super().init_w_vertical_layout()
        self._setup_radiobuttons()

    def init_w_horizontal_layout(self):
        super().init_w_horizontal_layout()
        self._setup_radiobuttons()

    def init_w_basic_widget_list(self, n_rows, n_widgets_per_row_list):
        super().init_w_basic_widget_list(n_rows, n_widgets_per_row_list)
        self._setup_radiobuttons()

    def init_w_box_layout(self,
                          n_columns,  # type: int
                          column_widths=None,  # type: Union[int, list]
                          row_heights=None,  # type: Union[int, list]
                          ):
        super().init_w_box_layout(n_columns,  # type: int
                                  column_widths=None,  # type: Union[int, list]
                                  row_heights=None,  # type: Union[int, list]
                                  )
        self._setup_radiobuttons()

    def _setup_radiobuttons(self):
        for i, w in enumerate(self._widget_list):
            button = getattr(self, self._widget_list[i])
            self._selection_dict[str(i)] = button
            button.config(variable=self._selected_value, value=i)
        self._selected_value.set(0)

    def selection(self):
        val = self._selected_value.get()
        return self._selection_dict[str(val)]
