import tkinter

import numpy

from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets.axes_image_canvas import AxesImageCanvas
from tk_builder.widgets.widget_descriptors import AxesImageCanvasDescriptor
from tk_builder.widgets.axes_image_canvas import AppVariables as CanvasAppVariables
from tk_builder.widgets.image_canvas import ToolConstants
from tk_builder.base_elements import BooleanDescriptor


class AppVariables(CanvasAppVariables):
    """
    The canvas image application variables.
    """
    resizeable = BooleanDescriptor('resizeable', default_value=False)  # type: bool


class ImageCanvasPanel(WidgetPanel):
    _widget_list = ("image_canvas",)
    image_canvas = AxesImageCanvasDescriptor("image_canvas")  # type: AxesImageCanvas

    def __init__(self, parent, canvas_width=600, canvas_height=400):
        WidgetPanel.__init__(self, parent)
        self.variables = AppVariables()
        self.init_w_vertical_layout()
        self.pack(fill=tkinter.BOTH, expand=tkinter.NO)

    def set_image_reader(self, image_reader):
        self.image_canvas.set_image_reader(image_reader)

    @property
    def resizeable(self):
        return self.variables.resizeable

    @resizeable.setter
    def resizeable(self, value):
        self.variables.resizeable = value
        self.image_canvas.resizeable = False

        if self.resizeable:
            self.on_resize(self.callback_resize)

    @property
    def current_tool(self):
        return self.image_canvas.canvas.variables.current_tool

    @current_tool.setter
    def current_tool(self, value):
        if value is None:
            self.image_canvas.canvas.set_current_tool_to_none()
        elif value == ToolConstants.EDIT_SHAPE_TOOL:
            self.image_canvas.canvas.set_current_tool_to_edit_shape()
        elif value == ToolConstants.PAN_TOOL:
            self.image_canvas.canvas.set_current_tool_to_pan()
        elif value == ToolConstants.SELECT_TOOL:
            self.image_canvas.canvas.set_current_tool_to_selection_tool()
        elif value == ToolConstants.ZOOM_IN_TOOL:
            self.image_canvas.canvas.set_current_tool_to_zoom_in()
        elif value == ToolConstants.ZOOM_OUT_TOOL:
            self.image_canvas.canvas.set_current_tool_to_zoom_out()
        elif value == ToolConstants.DRAW_ARROW_BY_DRAGGING:
            self.image_canvas.canvas.set_current_tool_to_draw_arrow_by_dragging()

    def callback_resize(self, event):
        print(event)
        self.update_everything(event)

    def update_everything(self, event):
        self.image_canvas.delete("all")

        print("winfo_width: " + str(self.winfo_width()))
        print("winfo_height: " + str(self.winfo_height()))
        print("canvas_winfo_width: " + str(self.image_canvas.winfo_width()))
        print("canvas_winfo_height: " + str(self.image_canvas.winfo_height()))
        print("canvas_width: " + str(self.image_canvas.variables.canvas_width))
        print("canvas_height: " + str(self.image_canvas.variables.canvas_height))

        width = self.winfo_width()-18
        height = self.winfo_width()

        self.image_canvas.set_canvas_size(width, height)

        self.image_canvas.canvas.set_canvas_size(self.image_canvas.variables.canvas_width -
                                                 self.image_canvas.left_margin_pixels -
                                                 self.image_canvas.right_margin_pixels,
                                                 self.image_canvas.variables.canvas_height -
                                                 self.image_canvas.top_margin_pixels -
                                                 self.image_canvas.bottom_margin_pixels)

        self.image_canvas.canvas.update_current_image()

        self.image_canvas.create_window(self.image_canvas.left_margin_pixels,
                                        self.image_canvas.top_margin_pixels,
                                        anchor=tkinter.NW,
                                        window=self.image_canvas.canvas)

        self.image_canvas._update_y_axis()
        self.image_canvas._update_y_label()
        self.image_canvas._update_title()
        self.image_canvas._update_x_axis()
        self.image_canvas._update_x_label()

