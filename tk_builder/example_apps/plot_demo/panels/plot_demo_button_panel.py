from tk_builder.panel_builder.widget_panel import WidgetPanel
from tk_builder.widgets import basic_widgets
from tk_builder.widgets import widget_descriptors


class ButtonPanel(WidgetPanel):
    """
    Basic button panel.
    """
    _widget_list = ("single_plot", "multi_plot", "animated_plot")
    single_plot = widget_descriptors.ButtonDescriptor("single_plot")
    multi_plot = widget_descriptors.ButtonDescriptor("multi_plot")
    animated_plot = widget_descriptors.ButtonDescriptor("animated_plot")

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent
            The parent widget.
        """

        WidgetPanel.__init__(self, parent)
        self.init_w_horizontal_layout()
