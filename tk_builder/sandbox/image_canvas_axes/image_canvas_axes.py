import os
import time
import numpy

import tkinter
from tkinter import Menu
from tk_builder.panel_templates.widget_panel.widget_panel import AbstractWidgetPanel
from tk_builder.panel_templates.image_canvas_panel.image_canvas_panel import ImageCanvasPanel
from tk_builder.sandbox.image_canvas_axes.panels.control_panel import ControlPanel

from sarpy_apps.apps.aperture_tool.app_variables import AppVariables


class ApertureTool(AbstractWidgetPanel):
    image_panel = ImageCanvasPanel         # type: ImageCanvasPanel
    control_panel = ControlPanel

    def __init__(self, master):
        self.app_variables = AppVariables()

        self.master = master

        master_frame = tkinter.Frame(master)
        AbstractWidgetPanel.__init__(self, master_frame)

        widgets_list = ["image_panel"]
        self.init_w_horizontal_layout(widgets_list)

        self.image_panel.canvas.set_canvas_size(900, 700)
        self.image_panel.set_canvas_size(800, 600)

        self.control_popup_panel = tkinter.Toplevel(self.master)
        self.control_panel = ControlPanel(self.control_popup_panel)
        self.control_panel.pack()
        self.control_popup_panel.withdraw()

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
    app = ApertureTool(root)
    root.mainloop()
