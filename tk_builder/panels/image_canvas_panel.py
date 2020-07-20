import tkinter

import numpy

from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets.axes_image_canvas import AxesImageCanvas
from tk_builder.widgets.image_frame import ImageFrame
from tk_builder.widgets.widget_descriptors import AxesImageCanvasDescriptor
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets.axes_image_canvas import AppVariables as CanvasAppVariables
from tk_builder.widgets.image_canvas import ToolConstants
from tk_builder.base_elements import BooleanDescriptor


class AppVariables(CanvasAppVariables):
    """
    The canvas image application variables.
    """
    resizeable = BooleanDescriptor('resizeable', default_value=False)  # type: bool


class Toolbar(WidgetPanel):
    _widget_list = ("zoom_in", "zoom_out")
    zoom_in = widget_descriptors.ButtonDescriptor("zoom_in")
    zoom_out = widget_descriptors.ButtonDescriptor("zoom_out")

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)
        self.init_w_horizontal_layout()


class ImageCanvasPanel(WidgetPanel):
    _widget_list = ("toolbar", "image_frame",)
    image_frame = widget_descriptors.PanelDescriptor("image_frame", ImageFrame)  # type: ImageFrame
    toolbar = widget_descriptors.PanelDescriptor("toolbar", Toolbar)

    def __init__(self, parent, canvas_width=600, canvas_height=400):
        WidgetPanel.__init__(self, parent)
        self.variables = AppVariables()
        self.init_w_vertical_layout()
        self.pack(fill=tkinter.BOTH, expand=tkinter.NO)
        self.image_frame.pack(fill=tkinter.BOTH, expand=tkinter.NO)
        self.set_text("stuff")

    def set_image_reader(self, image_reader):
        self.image_frame.outer_canvas.set_image_reader(image_reader)

    @property
    def resizeable(self):
        return self.variables.resizeable

    @resizeable.setter
    def resizeable(self, value):
        self.variables.resizeable = value
        if value == False:
            self.pack(expand=tkinter.NO)
        self.image_frame.resizeable = False

        if self.resizeable:
            self.on_resize(self.callback_resize)

    @property
    def current_tool(self):
        return self.image_frame.outer_canvas.canvas.variables.current_tool

    @current_tool.setter
    def current_tool(self, value):
        if value is None:
            self.image_frame.outer_canvas.canvas.set_current_tool_to_none()
        elif value == ToolConstants.EDIT_SHAPE_TOOL:
            self.image_frame.outer_canvas.canvas.set_current_tool_to_edit_shape()
        elif value == ToolConstants.PAN_TOOL:
            self.image_frame.outer_canvas.canvas.set_current_tool_to_pan()
        elif value == ToolConstants.SELECT_TOOL:
            self.image_frame.outer_canvas.canvas.set_current_tool_to_selection_tool()
        elif value == ToolConstants.ZOOM_IN_TOOL:
            self.image_frame.outer_canvas.canvas.set_current_tool_to_zoom_in()
        elif value == ToolConstants.ZOOM_OUT_TOOL:
            self.image_frame.outer_canvas.canvas.set_current_tool_to_zoom_out()
        elif value == ToolConstants.DRAW_ARROW_BY_DRAGGING:
            self.image_frame.outer_canvas.canvas.set_current_tool_to_draw_arrow_by_dragging()

    def callback_resize(self, event):
        self.update_everything(event)

    def update_everything(self, event):
        self.image_frame.outer_canvas.delete("all")

        width = self.winfo_width()
        height = self.winfo_height()

        parent_geometry = self.image_frame.master.winfo_geometry()
        outer_canvas_geometry = self.image_frame.winfo_geometry()

        parent_geom_width = int(parent_geometry.split("x")[0])
        parent_geom_height = int(parent_geometry.split("x")[1].split("+")[0])
        parent_geom_pad_x = int(parent_geometry.split("+")[1])
        parent_geom_pad_y = int(parent_geometry.split("+")[2])

        outer_canvas_width = int(outer_canvas_geometry.split("x")[0])
        outer_canvas_height = int(outer_canvas_geometry.split("x")[1].split("+")[0])
        outer_canvas_pad_x = int(outer_canvas_geometry.split("+")[1])
        outer_canvas_pad_y = int(outer_canvas_geometry.split("+")[2])

        constant_offset_x = WidgetPanel.padx
        constant_offset_y = WidgetPanel.pady

        width_offset = parent_geom_width - outer_canvas_width + outer_canvas_pad_x + parent_geom_pad_x - constant_offset_x
        height_offset = parent_geom_height - outer_canvas_height + outer_canvas_pad_y + parent_geom_pad_y - constant_offset_y

        adjusted_canvas_width = width - width_offset
        adjusted_canvas_height = height - height_offset

        if parent_geom_width > 1 and outer_canvas_width > 1:
            self.image_frame.set_canvas_size(adjusted_canvas_width, adjusted_canvas_height)

            self.image_frame.outer_canvas.set_canvas_size(adjusted_canvas_width, adjusted_canvas_height)
            self.image_frame.outer_canvas.canvas.set_canvas_size(self.image_frame.outer_canvas.variables.canvas_width -
                                                                 self.image_frame.outer_canvas.left_margin_pixels -
                                                                 self.image_frame.outer_canvas.right_margin_pixels,
                                                                 self.image_frame.outer_canvas.variables.canvas_height -
                                                                 self.image_frame.outer_canvas.top_margin_pixels -
                                                                 self.image_frame.outer_canvas.bottom_margin_pixels)

            self.image_frame.outer_canvas.canvas.update_current_image()

            display_image_dims = numpy.shape(
                self.image_frame.outer_canvas.canvas.variables.canvas_image_object.display_image)

            print(display_image_dims)

            self.image_frame.outer_canvas.set_canvas_size(display_image_dims[1] + self.image_frame.outer_canvas.right_margin_pixels + self.image_frame.outer_canvas.left_margin_pixels,
                                                          display_image_dims[0] + self.image_frame.outer_canvas.top_margin_pixels + self.image_frame.outer_canvas.bottom_margin_pixels + 5)
            self.image_frame.outer_canvas.canvas.set_canvas_size(self.image_frame.outer_canvas.variables.canvas_width -
                                                                 self.image_frame.outer_canvas.left_margin_pixels -
                                                                 self.image_frame.outer_canvas.right_margin_pixels,
                                                                 self.image_frame.outer_canvas.variables.canvas_height -
                                                                 self.image_frame.outer_canvas.top_margin_pixels -
                                                                 self.image_frame.outer_canvas.bottom_margin_pixels)
            self.image_frame.outer_canvas.update_current_image()
            self.image_frame.outer_canvas.canvas.update_current_image()

        self.image_frame.create_window(0, 0, anchor=tkinter.NW, window=self.image_frame.outer_canvas)
        self.image_frame.outer_canvas.create_window(self.image_frame.outer_canvas.left_margin_pixels,
                                                    self.image_frame.outer_canvas.top_margin_pixels,
                                                    anchor=tkinter.NW,
                                                    window=self.image_frame.outer_canvas.canvas)

        self.image_frame.outer_canvas._update_y_axis()
        self.image_frame.outer_canvas._update_y_label()
        self.image_frame.outer_canvas._update_title()
        self.image_frame.outer_canvas._update_x_axis()
        self.image_frame.outer_canvas._update_x_label()
