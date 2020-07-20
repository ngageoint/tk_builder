import tkinter

import numpy

from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import basic_widgets
from tk_builder.widgets.image_frame import ImageFrame
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets.axes_image_canvas import AppVariables as CanvasAppVariables
from tk_builder.widgets.image_canvas import ToolConstants
from tk_builder.base_elements import BooleanDescriptor


class AppVariables(CanvasAppVariables):
    """
    The canvas image application variables.
    """
    resizeable = BooleanDescriptor('resizeable', default_value=True)  # type: bool


class Toolbar(WidgetPanel):
    _widget_list = ("zoom_in", "zoom_out", "pan", "margins_checkbox",
                    "left_margin_label", "left_margin", "right_margin_label", "right_margin",
                    "top_margin_label", "top_margin",
                    "bottom_margin_label", "bottom_margin")
    zoom_in = widget_descriptors.ButtonDescriptor("zoom_in")
    zoom_out = widget_descriptors.ButtonDescriptor("zoom_out")
    pan = widget_descriptors.ButtonDescriptor("pan")

    margins_checkbox = widget_descriptors.CheckButtonDescriptor("margins_checkbox", default_text="margins")  # type: basic_widgets.CheckButton

    left_margin_label = widget_descriptors.LabelDescriptor("left_margin_label", default_text="left margin")  # type: basic_widgets.Label
    right_margin_label = widget_descriptors.LabelDescriptor("right_margin_label", default_text="right margin")  # type: basic_widgets.Label
    top_margin_label = widget_descriptors.LabelDescriptor("top_margin_label", default_text="top margin")  # type: basic_widgets.Label
    bottom_margin_label = widget_descriptors.LabelDescriptor("bottom_margin_label", default_text="bottom margin")  # type: basic_widgets.Label

    left_margin = widget_descriptors.EntryDescriptor("left_margin", default_text="0")  # type: basic_widgets.Entry
    right_margin = widget_descriptors.EntryDescriptor("right_margin", default_text="0")  # type: basic_widgets.Entry
    top_margin = widget_descriptors.EntryDescriptor("top_margin", default_text="0")  # type: basic_widgets.Entry
    bottom_margin = widget_descriptors.EntryDescriptor("bottom_margin", default_text="0")  # type: basic_widgets.Entry

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)
        self.init_w_basic_widget_list(2, [4, 8])


class ImageCanvasPanel(WidgetPanel):
    _widget_list = ("toolbar", "image_frame",)
    image_frame = widget_descriptors.PanelDescriptor("image_frame", ImageFrame)  # type: ImageFrame
    toolbar = widget_descriptors.PanelDescriptor("toolbar", Toolbar)  # type: Toolbar

    def __init__(self, parent, canvas_width=600, canvas_height=400):
        WidgetPanel.__init__(self, parent)
        self.variables = AppVariables()
        self.init_w_vertical_layout()
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        self.toolbar.left_margin.config(width=5)
        self.toolbar.right_margin.config(width=5)
        self.toolbar.top_margin.config(width=5)
        self.toolbar.bottom_margin.config(width=5)

        self.toolbar.left_margin_label.master.forget()

        # set up callbacks
        self.toolbar.left_margin.on_enter_or_return_key(self.callback_update_margins)
        self.toolbar.right_margin.on_enter_or_return_key(self.callback_update_margins)
        self.toolbar.top_margin.on_enter_or_return_key(self.callback_update_margins)
        self.toolbar.bottom_margin.on_enter_or_return_key(self.callback_update_margins)

        self.toolbar.margins_checkbox.config(command=self.callback_hide_show_margins)

    def callback_hide_show_margins(self):
        show_margins = self.toolbar.margins_checkbox.is_selected()
        if show_margins is False:
            self.toolbar.left_margin_label.master.forget()
        else:
            self.toolbar.left_margin_label.master.pack()

        print(show_margins)

    def callback_update_margins(self, event):
        self.image_frame.outer_canvas.left_margin_pixels = int(self.toolbar.left_margin.get())
        self.image_frame.outer_canvas.right_margin_pixels = int(self.toolbar.right_margin.get())
        self.image_frame.outer_canvas.top_margin_pixels = int(self.toolbar.top_margin.get())
        self.image_frame.outer_canvas.bottom_margin_pixels = int(self.toolbar.bottom_margin.get())
        self.update_everything()

    def set_image_reader(self, image_reader):
        self.image_frame.outer_canvas.set_image_reader(image_reader)

    @property
    def resizeable(self):
        return self.variables.resizeable

    @resizeable.setter
    def resizeable(self, value):
        self.variables.resizeable = value
        if value is False:
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
        self.update_everything()

    def update_everything(self):
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
            self.image_frame.outer_canvas.canvas.update_current_image()
        self.image_frame.outer_canvas.delete("all")

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
