import os
import tkinter
from tkinter.filedialog import asksaveasfilename

import numpy

from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import basic_widgets
from tk_builder.widgets.image_canvas import ImageCanvas
from tk_builder.widgets.axes_image_canvas import AxesImageCanvas
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
    top_level_controls = ("zoom_in",
                          "zoom_out",
                          "pan",
                          "margins_checkbox",
                          "axes_labels_checkbox",
                          "save_canvas",
                          "save_image")
    axes_labels_controls = ("title_label", "title",
                            "x_label", "x",
                            "y_label", "y")
    margin_controls = ("left_margin_label", "left_margin",
                       "right_margin_label", "right_margin",
                       "top_margin_label", "top_margin",
                       "bottom_margin_label", "bottom_margin")
    _widget_list = (top_level_controls, axes_labels_controls, margin_controls)
    zoom_in = widget_descriptors.ButtonDescriptor("zoom_in")  # type: basic_widgets.Button
    zoom_out = widget_descriptors.ButtonDescriptor("zoom_out")  # type: basic_widgets.Button
    pan = widget_descriptors.ButtonDescriptor("pan")  # type: basic_widgets.Button
    margins_checkbox = widget_descriptors.CheckButtonDescriptor("margins_checkbox", default_text="margins")  # type: basic_widgets.CheckButton
    axes_labels_checkbox = widget_descriptors.CheckButtonDescriptor("axes_labels_checkbox", default_text="axes labels")  # type: basic_widgets.CheckButton
    save_canvas = widget_descriptors.ButtonDescriptor("save_canvas", default_text="save canvas")  # type: basic_widgets.Button
    save_image = widget_descriptors.ButtonDescriptor("save_image", default_text="save image")  # type: basic_widgets.Button

    left_margin_label = widget_descriptors.LabelDescriptor("left_margin_label", default_text="left margin")  # type: basic_widgets.Label
    right_margin_label = widget_descriptors.LabelDescriptor("right_margin_label", default_text="right margin")  # type: basic_widgets.Label
    top_margin_label = widget_descriptors.LabelDescriptor("top_margin_label", default_text="top margin")  # type: basic_widgets.Label
    bottom_margin_label = widget_descriptors.LabelDescriptor("bottom_margin_label", default_text="bottom margin")  # type: basic_widgets.Label

    title_label = widget_descriptors.LabelDescriptor("title_label", default_text="title")  # type: basic_widgets.Label
    x_label = widget_descriptors.LabelDescriptor("x_label", default_text="x label")  # type: basic_widgets.Label
    y_label = widget_descriptors.LabelDescriptor("y_label", default_text="y label")  # type: basic_widgets.Label

    title = widget_descriptors.EntryDescriptor("title", default_text="")  # type: basic_widgets.Entry
    x = widget_descriptors.EntryDescriptor("x", default_text="")  # type: basic_widgets.Entry
    y = widget_descriptors.EntryDescriptor("y", default_text="")  # type: basic_widgets.Entry

    left_margin = widget_descriptors.EntryDescriptor("left_margin", default_text="0")  # type: basic_widgets.Entry
    right_margin = widget_descriptors.EntryDescriptor("right_margin", default_text="0")  # type: basic_widgets.Entry
    top_margin = widget_descriptors.EntryDescriptor("top_margin", default_text="0")  # type: basic_widgets.Entry
    bottom_margin = widget_descriptors.EntryDescriptor("bottom_margin", default_text="0")  # type: basic_widgets.Entry

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)
        self.init_w_rows()


class ImagePanel(WidgetPanel):
    _widget_list = ("toolbar", "image_frame",)
    image_frame = widget_descriptors.PanelDescriptor("image_frame", ImageFrame)  # type: ImageFrame
    toolbar = widget_descriptors.PanelDescriptor("toolbar", Toolbar)  # type: Toolbar
    canvas = widget_descriptors.ImageCanvasDescriptor("canvas")  # type: ImageCanvas
    axes_canvas = widget_descriptors.AxesImageCanvasDescriptor("axes_canvas")  # type: AxesImageCanvas

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)
        self.variables = AppVariables()
        self.init_w_vertical_layout()
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        self.toolbar.left_margin.config(width=5)
        self.toolbar.right_margin.config(width=5)
        self.toolbar.top_margin.config(width=5)
        self.toolbar.bottom_margin.config(width=5)

        self.toolbar.left_margin_label.master.forget()
        self.toolbar.title_label.master.forget()

        # set up callbacks
        self.toolbar.save_canvas.on_left_mouse_click(self.callback_save_canvas)
        self.toolbar.save_image.on_left_mouse_click(self.callback_save_image)

        self.toolbar.left_margin.on_enter_or_return_key(self.callback_update_axes)
        self.toolbar.right_margin.on_enter_or_return_key(self.callback_update_axes)
        self.toolbar.top_margin.on_enter_or_return_key(self.callback_update_axes)
        self.toolbar.bottom_margin.on_enter_or_return_key(self.callback_update_axes)

        self.toolbar.title.on_enter_or_return_key(self.callback_update_axes)
        self.toolbar.x.on_enter_or_return_key(self.callback_update_axes)
        self.toolbar.y.on_enter_or_return_key(self.callback_update_axes)

        self.toolbar.zoom_in.on_left_mouse_click(self.callback_set_to_zoom_in)
        self.toolbar.zoom_out.on_left_mouse_click(self.callback_set_to_zoom_out)
        self.toolbar.pan.on_left_mouse_click(self.callback_set_to_pan)

        self.toolbar.margins_checkbox.config(command=self.callback_hide_show_margins)
        self.toolbar.axes_labels_checkbox.config(command=self.callback_hide_show_axes_controls)

        self.toolbar.pack(expand=tkinter.YES, fill=tkinter.X)

        self.canvas = self.image_frame.outer_canvas.canvas
        self.axes_canvas = self.image_frame.outer_canvas

    def callback_set_to_zoom_in(self, event):
        self.current_tool = ToolConstants.ZOOM_IN_TOOL

    def callback_set_to_zoom_out(self, event):
        self.current_tool = ToolConstants.ZOOM_OUT_TOOL

    def callback_set_to_pan(self, event):
        self.current_tool = ToolConstants.PAN_TOOL

    def callback_save_canvas(self, event):
        save_fname = asksaveasfilename()
        if "." not in os.path.basename(save_fname):
            save_fname = save_fname + ".png"
        self.axes_canvas.save_full_canvas_as_png(save_fname)

    def callback_save_image(self, event):
        save_fname = asksaveasfilename()
        if "." not in os.path.basename(save_fname):
            save_fname = save_fname + ".png"
        self.canvas.save_full_canvas_as_png(save_fname)

    def callback_hide_show_margins(self):
        show_margins = self.toolbar.margins_checkbox.is_selected()
        if show_margins is False:
            self.toolbar.left_margin_label.master.forget()
        else:
            self.toolbar.left_margin_label.master.pack()

    def callback_hide_show_axes_controls(self):
        show_axes_controls = self.toolbar.axes_labels_checkbox.is_selected()
        if show_axes_controls is False:
            self.toolbar.title_label.master.forget()
        else:
            self.toolbar.title_label.master.pack()

    def callback_update_axes(self, event):
        self.image_frame.outer_canvas.title = self.toolbar.title.get()
        self.image_frame.outer_canvas.x_label = self.toolbar.x.get()
        self.image_frame.outer_canvas.y_label = self.toolbar.y.get()

        if self.toolbar.top_margin.get() == "0":
            self.toolbar.top_margin.set_text(str(self.image_frame.outer_canvas.top_margin_pixels))
        if self.toolbar.bottom_margin.get() == "0":
            self.toolbar.bottom_margin.set_text(str(self.image_frame.outer_canvas.bottom_margin_pixels))
        if self.toolbar.left_margin.get() == "0":
            self.toolbar.left_margin.set_text(str(self.image_frame.outer_canvas.left_margin_pixels))
        if self.toolbar.right_margin.get() == "0":
            self.toolbar.right_margin.set_text(str(self.image_frame.outer_canvas.right_margin_pixels))

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
            self.canvas.set_current_tool_to_none()
        elif value == ToolConstants.EDIT_SHAPE_TOOL:
            self.canvas.set_current_tool_to_edit_shape()
        elif value == ToolConstants.PAN_TOOL:
            self.canvas.set_current_tool_to_pan()
        elif value == ToolConstants.SELECT_TOOL:
            self.canvas.set_current_tool_to_selection_tool()
        elif value == ToolConstants.ZOOM_IN_TOOL:
            self.canvas.set_current_tool_to_zoom_in()
        elif value == ToolConstants.ZOOM_OUT_TOOL:
            self.canvas.set_current_tool_to_zoom_out()
        elif value == ToolConstants.DRAW_ARROW_BY_DRAGGING:
            self.canvas.set_current_tool_to_draw_arrow_by_dragging()
        elif value == ToolConstants.DRAW_RECT_BY_DRAGGING:
            self.canvas.set_current_tool_to_draw_rect()

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

            self.axes_canvas.set_canvas_size(adjusted_canvas_width, adjusted_canvas_height)
            self.canvas.set_canvas_size(self.axes_canvas.variables.canvas_width -
                                                                 self.axes_canvas.left_margin_pixels -
                                                                 self.axes_canvas.right_margin_pixels,
                                                                 self.axes_canvas.variables.canvas_height -
                                                                 self.axes_canvas.top_margin_pixels -
                                                                 self.axes_canvas.bottom_margin_pixels)

            self.canvas.update_current_image()

            display_image_dims = numpy.shape(
                self.canvas.variables.canvas_image_object.display_image)

            self.axes_canvas.set_canvas_size(display_image_dims[1] + self.axes_canvas.right_margin_pixels + self.axes_canvas.left_margin_pixels,
                                                          display_image_dims[0] + self.axes_canvas.top_margin_pixels + self.axes_canvas.bottom_margin_pixels + 5)
            self.canvas.set_canvas_size(self.axes_canvas.variables.canvas_width -
                                                                 self.image_frame.outer_canvas.left_margin_pixels -
                                                                 self.image_frame.outer_canvas.right_margin_pixels,
                                                                 self.image_frame.outer_canvas.variables.canvas_height -
                                                                 self.image_frame.outer_canvas.top_margin_pixels -
                                                                 self.image_frame.outer_canvas.bottom_margin_pixels)
            self.canvas.update_current_image()
        self.axes_canvas.delete("all")

        self.image_frame.create_window(0, 0, anchor=tkinter.NW, window=self.image_frame.outer_canvas)
        self.image_frame.outer_canvas.create_window(self.image_frame.outer_canvas.left_margin_pixels,
                                                    self.image_frame.outer_canvas.top_margin_pixels,
                                                    anchor=tkinter.NW,
                                                    window=self.image_frame.outer_canvas.canvas)
        self.canvas.redraw_all_shapes()

        self.image_frame.outer_canvas._update_y_axis()
        self.image_frame.outer_canvas._update_y_label()
        self.image_frame.outer_canvas._update_title()
        self.image_frame.outer_canvas._update_x_axis()
        self.image_frame.outer_canvas._update_x_label()
