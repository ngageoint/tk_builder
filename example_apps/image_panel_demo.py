import os
import tkinter
from tkinter import Menu

import numpy

from tk_builder.panel_builder import WidgetPanel
from tk_builder.panels.image_panel import ImagePanel
from tk_builder.image_readers.numpy_image_reader import NumpyImageReader
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets.image_canvas import ToolConstants


class Buttons(WidgetPanel):
    _widget_list = ("draw_rect", "draw_line", "edit_shape")
    draw_rect = widget_descriptors.ButtonDescriptor("draw_rect", default_text="rect")
    draw_line = widget_descriptors.ButtonDescriptor("draw_line", default_text="line")
    edit_shape = widget_descriptors.ButtonDescriptor("edit_shape", default_text="edit")

    def __init__(self, primary):
        self.primary = primary
        WidgetPanel.__init__(self, primary)
        self.init_w_vertical_layout()


class CanvasResize(WidgetPanel):
    _widget_list = ("image_panel", "button_panel")

    image_panel = widget_descriptors.ImagePanelDescriptor("image_panel")         # type: ImagePanel
    button_panel = widget_descriptors.PanelDescriptor("button_panel", Buttons)  # type: Buttons

    def __init__(self, primary):
        self.rect_id = None
        self.line_id = None
        self.n_shapes = 0

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
        self.image_panel.canvas.set_canvas_size(800, 800)

        self.button_panel.draw_rect.on_left_mouse_click(self.callback_draw_rect)
        self.button_panel.draw_line.on_left_mouse_click(self.callback_draw_line)
        self.button_panel.edit_shape.on_left_mouse_click(self.callback_edit_shape)
        self.image_panel.canvas.on_left_mouse_release(self.callback_on_left_mouse_release)

    def callback_draw_rect(self, event):
        self.image_panel.canvas.set_current_tool_to_draw_rect(self.rect_id)

    def callback_draw_line(self, event):
        self.image_panel.canvas.set_current_tool_to_draw_line_by_dragging(self.line_id)

    def callback_edit_shape(self, event):
        self.image_panel.canvas.set_current_tool_to_edit_shape()

    def callback_on_left_mouse_release(self, event):
        self.image_panel.canvas.callback_handle_left_mouse_release(event)
        n_shapes = len(self.image_panel.canvas.get_non_tool_shape_ids())
        if n_shapes > self.n_shapes:
            self.n_shapes = n_shapes
            if self.image_panel.current_tool == ToolConstants.DRAW_RECT_BY_DRAGGING:
                self.rect_id = self.image_panel.canvas.variables.current_shape_id
            elif self.image_panel.current_tool == ToolConstants.DRAW_LINE_BY_DRAGGING:
                self.line_id = self.image_panel.canvas.variables.current_shape_id

    def exit(self):
        self.quit()


if __name__ == '__main__':
    root = tkinter.Tk()
    app = CanvasResize(root)
    root.after(100, app.image_panel.update_everything)
    root.mainloop()
