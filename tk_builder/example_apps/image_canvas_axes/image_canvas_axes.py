import numpy

import tkinter
from tkinter import Menu
from tk_builder.panel_builder.widget_panel import WidgetPanel
from tk_builder.panels.image_canvas_panel.image_canvas_panel import ImageCanvasPanel
from tk_builder.image_readers.numpy_image_reader import NumpyImageReader
from tk_builder.example_apps.image_canvas_axes.panels.control_panel import ControlPanel
from tk_builder.widgets import widget_descriptors

from sarpy_apps.apps.aperture_tool.app_variables import AppVariables


class CanvasResize(WidgetPanel):
    _widget_list = ("image_panel", )

    image_panel = widget_descriptors.ImageCanvasPanelDescriptor("image_panel")         # type: ImageCanvasPanel
    control_panel = widget_descriptors.PanelDescriptor("control_panel", ControlPanel)   # type: ControlPanel

    def __init__(self, primary):
        self.app_variables = AppVariables()

        self.primary = primary

        primary_frame = tkinter.Frame(primary)
        WidgetPanel.__init__(self, primary_frame)

        self.init_w_horizontal_layout()

        self.image_panel.set_canvas_size(800, 600)

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

        self.control_popup_panel = tkinter.Toplevel(self.primary)
        self.control_panel = ControlPanel(self.control_popup_panel)

        menubar = Menu()

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.exit)

        # create more pulldown menus
        popups_menu = Menu(menubar, tearoff=0)
        popups_menu.add_command(label="Main Controls", command=self.controls_popup)

        primary.config(menu=menubar)

        primary_frame.pack()
        self.pack()

        # callbacks
        self.control_panel.x_slider.on_left_mouse_motion(self.callback_x_slider_update)

    def callback_x_slider_update(self, event):
        print(self.control_panel.x_slider.get())

    def exit(self):
        self.quit()

    def controls_popup(self):
        self.control_panel.deiconify()


if __name__ == '__main__':
    root = tkinter.Tk()
    app = CanvasResize(root)
    root.mainloop()
