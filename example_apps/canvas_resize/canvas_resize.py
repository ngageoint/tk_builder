import os

import numpy
import tkinter
from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets.image_canvas import ImageCanvas
from tk_builder.image_readers.numpy_image_reader import NumpyImageReader
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets import basic_widgets


class CanvasResize(WidgetPanel):
    _widget_list = ("image_panel",)

    image_panel = widget_descriptors.PanelDescriptor("image_panel", ImageCanvas)         # type: ImageCanvas

    def __init__(self, primary):
        self.primary = primary

        primary_frame = basic_widgets.Frame(primary)
        WidgetPanel.__init__(self, primary_frame)

        self.init_w_horizontal_layout()

        # self.image_panel.set_canvas_size(800, 600)
        self.image_panel.resizeable = True

        image_data = numpy.random.random((500, 1200))
        image_data = image_data * 255
        image_reader = NumpyImageReader(image_data)
        self.image_panel._set_image_reader(image_reader)

        self.image_panel.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        primary_frame.pack(fill=tkinter.BOTH, expand=tkinter.YES)


if __name__ == '__main__':
    root = tkinter.Tk()
    app = CanvasResize(root)
    root.mainloop()
