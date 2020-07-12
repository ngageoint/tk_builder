from tk_builder.panels.widget_panel.widget_panel import AbstractWidgetPanel
from tk_builder.widgets import basic_widgets


class ButtonPanel(AbstractWidgetPanel):
    """
    Basic button panel.
    """

    single_plot = basic_widgets.Button
    multi_plot = basic_widgets.Button
    animated_plot = basic_widgets.Button

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent
            The parent widget.
        """

        AbstractWidgetPanel.__init__(self, parent)
        widget_list = ["single_plot", "multi_plot", "animated_plot"]
        self.init_w_horizontal_layout(widget_list)
        self.set_label_text("plot demo buttons")
