import os

import numpy
import tkinter
from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets.axes_image_canvas import AxesImageCanvas
from tk_builder.image_readers.numpy_image_reader import NumpyImageReader
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets import basic_widgets


class SaveImageCanvas(WidgetPanel):
    _widget_list = ("image_panel", "save_button")

    image_panel = widget_descriptors.ImageCanvasPanelDescriptor("image_panel")         # type: AxesImageCanvas
    save_button = widget_descriptors.ButtonDescriptor("save_button", default_text="save")  # type: basic_widgets.Button

    def __init__(self, primary):
        self.primary = primary

        primary_frame = tkinter.Frame(primary)
        WidgetPanel.__init__(self, primary_frame)

        self.init_w_horizontal_layout()
        self.image_panel.set_canvas_size(800, 600)
        self.image_panel.resizeable = True

        image_data = numpy.random.random((500, 1200))
        image_data = image_data * 255
        image_reader = NumpyImageReader(image_data)
        self.image_panel.set_image_reader(image_reader)
        self.image_panel.canvas.set_current_tool_to_pan()

        self.image_panel.left_margin_pixels = 200
        self.image_panel.top_margin_pixels = 100
        self.image_panel.bottom_margin_pixels = 100
        self.image_panel.right_margin_pixels = 100
        self.image_panel.x_label = "x axis"
        self.image_panel.y_label = "Y axis"

        self.image_panel.title = "This is a title"

        self.image_panel.image_x_min_val = 500
        self.image_panel.image_x_max_val = 1200

        self.image_panel.image_y_min_val = 5000
        self.image_panel.image_y_max_val = 2000

        self.save_button.on_left_mouse_click(self.callback_save_as_png)
        self.image_panel.pack(fill="both", expand=True)
        self.pack(fill="both", expand=True)
        primary_frame.pack(fill="both", expand=True)

    def callback_save_as_png(self, event):
        self.image_panel.canvas.save_full_canvas_as_png(os.path.expanduser("~/Downloads/canvas_image.png"))
        self.image_panel.save_full_canvas_as_png(os.path.expanduser("~/Downloads/image_panel.png"))


if __name__ == '__main__':
    root = tkinter.Tk()
    app = SaveImageCanvas(root)
    root.mainloop()
