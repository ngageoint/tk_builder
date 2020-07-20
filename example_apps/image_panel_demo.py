import os
import tkinter
from tkinter import Menu

import numpy

from tk_builder.panel_builder import WidgetPanel
from tk_builder.panels.image_canvas_panel import ImageCanvasPanel
from tk_builder.image_readers.numpy_image_reader import NumpyImageReader
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets.image_canvas import ToolConstants

from example_apps.image_canvas_axes.control_panel import ControlPanel


class CanvasResize(WidgetPanel):
    _widget_list = ("image_panel", )

    image_panel = widget_descriptors.ImageCanvasPanelDescriptor("image_panel")         # type: ImageCanvasPanel
    control_panel = widget_descriptors.PanelDescriptor("control_panel", ControlPanel)   # type: ControlPanel

    def __init__(self, primary):

        self.primary = primary

        primary_frame = tkinter.Frame(primary)
        WidgetPanel.__init__(self, primary_frame)

        self.init_w_horizontal_layout()

        # self.image_panel.set_canvas_size(800, 600)
        self.image_panel.resizeable = True

        image_data = numpy.random.random((500, 1200))
        image_data = image_data * 255
        image_reader = NumpyImageReader(image_data)
        self.image_panel.set_image_reader(image_reader)
        self.image_panel.current_tool = ToolConstants.PAN_TOOL

        self.image_panel.image_canvas.left_margin_pixels = 0
        self.image_panel.image_canvas.top_margin_pixels = 0
        self.image_panel.image_canvas.bottom_margin_pixels = 0
        self.image_panel.image_canvas.right_margin_pixels = 0
        self.image_panel.image_canvas.x_label = "x axis"
        self.image_panel.image_canvas.y_label = "Y axis"

        self.image_panel.image_canvas.title = "This is a title"

        self.image_panel.image_canvas.image_x_min_val = 500
        self.image_panel.image_canvas.image_x_max_val = 1200

        self.image_panel.image_canvas.image_y_min_val = 5000
        self.image_panel.image_canvas.image_y_max_val = 2000

        self.control_popup_panel = tkinter.Toplevel(self.primary)
        self.control_panel = ControlPanel(self.control_popup_panel)

        menubar = Menu()

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.exit)

        # create more pulldown menus
        popups_menu = Menu(menubar, tearoff=0)
        popups_menu.add_command(label="Main Controls", command=self.controls_popup)

        primary.config(menu=menubar)

        primary_frame.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.control_panel.top_margin.set(self.image_panel.image_canvas.top_margin_pixels)
        self.control_panel.bottom_margin.set(self.image_panel.image_canvas.bottom_margin_pixels)
        self.control_panel.left_margin.set(self.image_panel.image_canvas.left_margin_pixels)
        self.control_panel.right_margin.set(self.image_panel.image_canvas.right_margin_pixels)

        # callbacks
        self.control_panel.top_margin.on_left_mouse_release(self.callback_top_margin_update)
        self.control_panel.bottom_margin.on_left_mouse_release(self.callback_bottom_margin_update)
        self.control_panel.left_margin.on_left_mouse_release(self.callback_left_margin_update)
        self.control_panel.right_margin.on_left_mouse_release(self.callback_right_margin_update)

    def callback_top_margin_update(self, event):
        margin = int(self.control_panel.top_margin.get())
        self.image_panel.image_canvas.top_margin_pixels = margin
        self.image_panel.update_everything(event)

    def callback_bottom_margin_update(self, event):
        margin = int(self.control_panel.bottom_margin.get())
        self.image_panel.image_canvas.bottom_margin_pixels = margin
        self.image_panel.update_everything(event)

    def callback_left_margin_update(self, event):
        margin = int(self.control_panel.left_margin.get())
        self.image_panel.image_canvas.left_margin_pixels = margin
        self.image_panel.update_everything(event)

    def callback_right_margin_update(self, event):
        margin = int(self.control_panel.right_margin.get())
        self.image_panel.image_canvas.right_margin_pixels = margin
        self.image_panel.update_everything(event)

    def exit(self):
        self.quit()

    def controls_popup(self):
        self.control_panel.deiconify()

    def callback_save_as_png(self, event):
        self.image_panel.canvas.save_full_canvas_as_png(os.path.expanduser("~/Downloads/canvas_image.png"))
        self.image_panel.save_full_canvas_as_png(os.path.expanduser("~/Downloads/image_panel.png"))


if __name__ == '__main__':
    root = tkinter.Tk()
    app = CanvasResize(root)
    root.mainloop()
