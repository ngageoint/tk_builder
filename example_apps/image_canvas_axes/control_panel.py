from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import basic_widgets
from tk_builder.widgets import widget_descriptors


class ControlPanel(WidgetPanel):
    _widget_list = ('x_slider', 'y_slider')
    x_slider = widget_descriptors.ScaleDescriptor("x_slider")            # type: basic_widgets.Scale
    y_slider = widget_descriptors.ScaleDescriptor("y_slider")          # type: basic_widgets.Scale

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)

        self.init_w_vertical_layout()

        self.pack()
#        self.parent.protocol("WM_DELETE_WINDOW", self.close_window)
