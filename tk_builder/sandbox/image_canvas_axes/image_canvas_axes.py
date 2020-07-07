import numpy

import tkinter
from tkinter import Menu
from tk_builder.panel_templates.widget_panel.widget_panel import AbstractWidgetPanel
from tk_builder.panel_templates.image_canvas_panel.image_canvas_panel import ImageCanvasPanel
from tk_builder.image_readers.numpy_image_reader import NumpyImageReader
from tk_builder.sandbox.image_canvas_axes.panels.control_panel import ControlPanel

from sarpy_apps.apps.aperture_tool.app_variables import AppVariables


class CanvasResize(AbstractWidgetPanel):
    image_panel = ImageCanvasPanel         # type: ImageCanvasPanel
    control_panel = ControlPanel

    def __init__(self, master):
        self.app_variables = AppVariables()

        self.master = master

        master_frame = tkinter.Frame(master)
        AbstractWidgetPanel.__init__(self, master_frame)

        widgets_list = ["image_panel"]
        self.init_w_horizontal_layout(widgets_list)

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

        self.control_popup_panel = tkinter.Toplevel(self.master)
        self.control_panel = ControlPanel(self.control_popup_panel)

        menubar = Menu()

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.exit)

        # create more pulldown menus
        popups_menu = Menu(menubar, tearoff=0)
        popups_menu.add_command(label="Main Controls", command=self.controls_popup)

        master.config(menu=menubar)

        master_frame.pack()
        self.pack()

    def exit(self):
        self.quit()

    def controls_popup(self):
        self.control_panel.deiconify()


if __name__ == '__main__':
    root = tkinter.Tk()
    app = CanvasResize(root)
    root.mainloop()
