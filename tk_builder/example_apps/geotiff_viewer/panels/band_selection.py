from tk_builder.panel_builder.widget_panel import WidgetPanel
from tk_builder.widgets import basic_widgets


class BandSelection(WidgetPanel):
    """
    Band selection tool for RGB display.
    """

    red_selection = basic_widgets.Combobox      # type: basic_widgets.Combobox
    green_selection = basic_widgets.Combobox    # type: basic_widgets.Combobox
    blue_selection = basic_widgets.Combobox     # type: basic_widgets.Combobox
    alpha_selection = basic_widgets.Combobox    # type: basic_widgets.Combobox

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent
            The parent widget.
        """
        WidgetPanel.__init__(self, parent)

        widget_list = ["red", "red_selection",
                       "green", "green_selection",
                       "blue", "blue_selection",
                       "alpha", "alpha_selection"]
        self.init_w_box_layout(widget_list, n_columns=2, column_widths=10)
