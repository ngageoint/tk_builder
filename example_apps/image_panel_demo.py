import os
import tkinter
from tkinter import Menu

import numpy

from tk_builder.panel_builder import WidgetPanel
from tk_builder.panels.image_panel import ImagePanel
from tk_builder.image_readers.numpy_image_reader import NumpyImageReader
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets.image_canvas import ToolConstants


class CanvasResize(WidgetPanel):
    _widget_list = ("image_panel", )

    image_panel = widget_descriptors.ImagePanelDescriptor("image_panel")         # type: ImagePanel

    def __init__(self, primary):

        self.primary = primary

        primary_frame = tkinter.Frame(primary)
        WidgetPanel.__init__(self, primary_frame)

        self.init_w_horizontal_layout()

        self.image_panel.image_frame.set_canvas_size(800, 600)
        self.image_panel.resizeable = True

        image_data = numpy.random.random((500, 1200))
        image_data = image_data * 255
        image_reader = NumpyImageReader(image_data)
        self.image_panel.set_image_reader(image_reader)
        self.image_panel.current_tool = ToolConstants.PAN_TOOL

        self.image_panel.axes_canvas.image_x_min_val = 500
        self.image_panel.axes_canvas.image_x_max_val = 1200

        self.image_panel.axes_canvas.image_y_min_val = 5000
        self.image_panel.axes_canvas.image_y_max_val = 2000

        menubar = Menu()

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.exit)

        # create more pulldown menus
        popups_menu = Menu(menubar, tearoff=0)

        primary.config(menu=menubar)

        primary_frame.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    def exit(self):
        self.quit()


if __name__ == '__main__':
    root = tkinter.Tk()
    app = CanvasResize(root)
    root.mainloop()
