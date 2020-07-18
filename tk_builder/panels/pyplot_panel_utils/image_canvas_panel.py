import tkinter

from tk_builder.widgets.basic_widgets import LabelFrame
from tk_builder.widgets.axes_image_canvas import AxesImageCanvas
from tk_builder.widgets import widget_descriptors
from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import basic_widgets
from tk_builder.widgets import widget_descriptors


class ImageCanvasPanel(WidgetPanel):
    _widget_list = ("image_canvas",)

    image_canvas = widget_descriptors.PanelDescriptor("image_canvas", AxesImageCanvas)

    def __init__(self,
                 parent,
                 ):
        WidgetPanel.__init__(self, parent)
        self.init_w_vertical_layout()
        self.pack(fill=tkinter.BOTH, expand=1)
