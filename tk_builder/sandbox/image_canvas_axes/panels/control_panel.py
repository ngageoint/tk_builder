from tk_builder.panels.widget_panel.widget_panel import AbstractWidgetPanel
from tk_builder.widgets import basic_widgets


class ControlPanel(AbstractWidgetPanel):
    x_slider = basic_widgets.Scale            # type: basic_widgets.Scale
    y_slider = basic_widgets.Scale          # type: basic_widgets.Scale

    def __init__(self, parent):
        # set the master frame
        AbstractWidgetPanel.__init__(self, parent)
        widgets_list = ["x_slider", "y_slider"]

        self.init_w_basic_widget_list(widgets_list, n_rows=2, n_widgets_per_row_list=[1, 2])

        self.pack()
        self.parent.protocol("WM_DELETE_WINDOW", self.close_window)

