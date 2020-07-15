from tk_builder.panel_builder.widget_panel import WidgetPanel
from tk_builder.widgets import basic_widgets
from tk_builder.widgets import widget_descriptors


class BandSelection(WidgetPanel):
    """
    Band selection tool for RGB display.
    """
    _widget_list = ("red_label", "red_selection",
                    "green_label", "green_selection",
                    "blue_label", "blue_selection",
                    "alpha_label", "alpha_selection")

    red_label = widget_descriptors.LabelDescriptor("red_label", default_text="red")
    green_label = widget_descriptors.LabelDescriptor("green_label", default_text="green")
    blue_label = widget_descriptors.LabelDescriptor("blue_label", default_text="blue")
    alpha_label = widget_descriptors.LabelDescriptor("alpha_label", default_text="alpha")

    red_selection = widget_descriptors.ComboboxDescriptor("red_selection")      # type: basic_widgets.Combobox
    green_selection = widget_descriptors.ComboboxDescriptor("green_selection")    # type: basic_widgets.Combobox
    blue_selection = widget_descriptors.ComboboxDescriptor("blue_selection")     # type: basic_widgets.Combobox
    alpha_selection = widget_descriptors.ComboboxDescriptor("alpha_selection")    # type: basic_widgets.Combobox

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent
            The parent widget.
        """
        WidgetPanel.__init__(self, parent)

        self.init_w_box_layout(n_columns=2, column_widths=10)
