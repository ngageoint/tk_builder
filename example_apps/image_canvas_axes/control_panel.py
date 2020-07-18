from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import basic_widgets
from tk_builder.widgets import widget_descriptors


class ControlPanel(WidgetPanel):
    _widget_list = ("top_margin_label", "top_margin",
                    "bottom_margin_label", "bottom_margin",
                    "left_margin_label", "left_margin",
                    "right_margin_label", "right_margin")

    top_margin_label = widget_descriptors.LabelDescriptor("top_margin_label", default_text="top margin")
    bottom_margin_label = widget_descriptors.LabelDescriptor("bottom_margin_label", default_text="bottom margin")
    left_margin_label = widget_descriptors.LabelDescriptor("left_margin_label", default_text="left margin")
    right_margin_label = widget_descriptors.LabelDescriptor("right_margin_label", default_text="right margin")

    top_margin = widget_descriptors.ScaleDescriptor("top_margin")        # type: basic_widgets.Scale
    bottom_margin = widget_descriptors.ScaleDescriptor("bottom_margin")     # type: basic_widgets.Scale
    left_margin = widget_descriptors.ScaleDescriptor("left_margin")     # type: basic_widgets.Scale
    right_margin = widget_descriptors.ScaleDescriptor("right_margin")     # type: basic_widgets.Scale

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)

        self.init_w_basic_widget_list(4, [2, 2, 2, 2])

        self.top_margin.config(from_=0, to=300)
        self.bottom_margin.config(from_=0, to=300)
        self.left_margin.config(from_=0, to=300)
        self.right_margin.config(from_=0, to=300)

        self.parent.protocol("WM_DELETE_WINDOW", self.close_window)
