import os
import tkinter
from tkinter.filedialog import asksaveasfilename

from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import basic_widgets
from tk_builder.widgets.axes_image_canvas import AxesImageCanvas
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets.image_canvas import ToolConstants

import PIL.Image


class Toolbar(WidgetPanel):
    top_level_controls = ("zoom_in",
                          "zoom_out",
                          "pan",
                          "margins_checkbox",
                          "axes_labels_checkbox",
                          "canvas_size_checkbox",
                          "save_canvas",
                          "save_image")
    axes_labels_controls = ("title_label", "title",
                            "x_label", "x",
                            "y_label", "y")

    margin_controls = ("left_margin_label", "left_margin",
                       "right_margin_label", "right_margin",
                       "top_margin_label", "top_margin",
                       "bottom_margin_label", "bottom_margin")

    canvas_size_controls = ("canvas_width_label", "canvas_width", "canvas_height_label", "canvas_height")

    _widget_list = (top_level_controls, axes_labels_controls, margin_controls, canvas_size_controls)
    zoom_in = widget_descriptors.ButtonDescriptor("zoom_in")  # type: basic_widgets.Button
    zoom_out = widget_descriptors.ButtonDescriptor("zoom_out")  # type: basic_widgets.Button
    pan = widget_descriptors.ButtonDescriptor("pan")  # type: basic_widgets.Button
    margins_checkbox = widget_descriptors.CheckButtonDescriptor("margins_checkbox", default_text="margins")  # type: basic_widgets.CheckButton
    axes_labels_checkbox = widget_descriptors.CheckButtonDescriptor("axes_labels_checkbox", default_text="axes labels")  # type: basic_widgets.CheckButton
    canvas_size_checkbox = widget_descriptors.CheckButtonDescriptor("canvas_size_checkbox", default_text="canvas size")  # type: basic_widgets.CheckButton
    save_canvas = widget_descriptors.ButtonDescriptor("save_canvas", default_text="save canvas")  # type: basic_widgets.Button
    save_image = widget_descriptors.ButtonDescriptor("save_image", default_text="save image")  # type: basic_widgets.Button

    left_margin_label = widget_descriptors.LabelDescriptor("left_margin_label", default_text="left margin")  # type: basic_widgets.Label
    right_margin_label = widget_descriptors.LabelDescriptor("right_margin_label", default_text="right margin")  # type: basic_widgets.Label
    top_margin_label = widget_descriptors.LabelDescriptor("top_margin_label", default_text="top margin")  # type: basic_widgets.Label
    bottom_margin_label = widget_descriptors.LabelDescriptor("bottom_margin_label", default_text="bottom margin")  # type: basic_widgets.Label

    left_margin = widget_descriptors.EntryDescriptor("left_margin", default_text="0")  # type: basic_widgets.Entry
    right_margin = widget_descriptors.EntryDescriptor("right_margin", default_text="0")  # type: basic_widgets.Entry
    top_margin = widget_descriptors.EntryDescriptor("top_margin", default_text="0")  # type: basic_widgets.Entry
    bottom_margin = widget_descriptors.EntryDescriptor("bottom_margin", default_text="0")  # type: basic_widgets.Entry

    title_label = widget_descriptors.LabelDescriptor("title_label", default_text="title")  # type: basic_widgets.Label
    x_label = widget_descriptors.LabelDescriptor("x_label", default_text="x label")  # type: basic_widgets.Label
    y_label = widget_descriptors.LabelDescriptor("y_label", default_text="y label")  # type: basic_widgets.Label

    title = widget_descriptors.EntryDescriptor("title", default_text="")  # type: basic_widgets.Entry
    x = widget_descriptors.EntryDescriptor("x", default_text="")  # type: basic_widgets.Entry
    y = widget_descriptors.EntryDescriptor("y", default_text="")  # type: basic_widgets.Entry

    canvas_width_label = widget_descriptors.LabelDescriptor("canvas_width_label", default_text="width")  # type: basic_widgets.Label
    canvas_width = widget_descriptors.EntryDescriptor("canvas_width", default_text="600")  # type: basic_widgets.Entry
    canvas_height_label = widget_descriptors.LabelDescriptor("canvas_height_label", default_text="height")  # type: basic_widgets.Label
    canvas_height = widget_descriptors.EntryDescriptor("canvas_height", default_text="400")  # type: basic_widgets.Entry

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)
        self.init_w_rows()


class ImagePanel(WidgetPanel):
    """
    ImagePanel class.  This class utilizes the ImageCanvas to display raster and vector data.  A toolbar is
    provided with common tools such as pan and zoom functionality.  Mouse zoom operations using the
    mouse wheel are enabled by default.
    Other functionality includes axes and margins in the case the user wishes to display X/Y axes, titles, etc
    for 2 dimensional data displays or plots.
    """

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)
        self.toolbar = Toolbar(self)
        self.axes_canvas = AxesImageCanvas(self)
        self.canvas = self.axes_canvas.inner_canvas

        self.toolbar.left_margin_label.master.forget()
        self.toolbar.title_label.master.forget()
        self.toolbar.canvas_width_label.master.forget()

        # set up callbacks
        self.toolbar.save_canvas.config(command=self.callback_save_canvas)
        self.toolbar.save_image.config(command=self.callback_save_image)

        self.toolbar.left_margin.on_enter_or_return_key(self.callback_update_axes)
        self.toolbar.right_margin.on_enter_or_return_key(self.callback_update_axes)
        self.toolbar.top_margin.on_enter_or_return_key(self.callback_update_axes)
        self.toolbar.bottom_margin.on_enter_or_return_key(self.callback_update_axes)

        self.toolbar.title.on_enter_or_return_key(self.callback_update_axes)
        self.toolbar.x.on_enter_or_return_key(self.callback_update_axes)
        self.toolbar.y.on_enter_or_return_key(self.callback_update_axes)

        self.toolbar.canvas_width.on_enter_or_return_key(self.callback_update_canvas_size)
        self.toolbar.canvas_height.on_enter_or_return_key(self.callback_update_canvas_size)

        self.toolbar.zoom_in.config(command=self.callback_set_to_zoom_in)
        self.toolbar.zoom_out.config(command=self.callback_set_to_zoom_out)
        self.toolbar.pan.config(command=self.callback_set_to_pan)

        self.toolbar.margins_checkbox.config(command=self.callback_hide_show_margins)
        self.toolbar.axes_labels_checkbox.config(command=self.callback_hide_show_axes_controls)
        self.toolbar.canvas_size_checkbox.config(command=self.callback_hide_show_canvas_size_controls)

        self.pack()
        self.toolbar.pack(side='top', expand=tkinter.NO, fill=tkinter.BOTH)
        self.axes_canvas.pack(side='bottom')

        self.set_max_canvas_size(1920, 1080)
        self.resizeable = False

    def hide_zoom_in(self):
        """
        Hides the zoom in button in the toolbar
        """
        self.toolbar.zoom_in.pack_forget()

    def hide_zoom_out(self):
        """
        Hides the zoom out button in the toolbar
        """
        self.toolbar.zoom_out.pack_forget()

    def hide_pan(self):
        """
        Hides the pan button in the toolbar
        """
        self.toolbar.pan.pack_forget()

    def hide_margin_controls(self):
        """
        Hides the margin controls checkbox in the toolbar
        """
        self.toolbar.margins_checkbox.pack_forget()

    def hide_axes_controls(self):
        """
        Hides the axes labels checkbox in the toolbar
        """
        self.toolbar.axes_labels_checkbox.pack_forget()

    def hide_save_canvas(self):
        """
        Hides the save canvas button in the toolbar
        """
        self.toolbar.save_canvas.pack_forget()

    def hide_save_image(self):
        """
        Hides the save image button in the toolbar
        """
        self.toolbar.save_image.pack_forget()

    def hide_canvas_size_controls(self):
        """
        Hides the canvas size controls checkbox in the toolbar
        """
        self.toolbar.canvas_size_checkbox.pack_forget()

    def show_canvas_size_controls(self):
        """
        Shows / unhides the canvas size controls checkbox in the toolbar
        """
        self.toolbar.canvas_size_checkbox.pack()

    def callback_canvas_mouse_zoom(self, event):
        """
        Handles the canvas zoom event then updates axes
        """
        self.canvas.callback_mouse_zoom(event)
        self.update_everything()

    def callback_set_to_zoom_in(self):
        """
        Sets current tool to zoom in
        """
        self.current_tool = ToolConstants.ZOOM_IN_TOOL

    def callback_set_to_zoom_out(self):
        """
        Sets current tool to zoom out
        """
        self.current_tool = ToolConstants.ZOOM_OUT_TOOL

    def callback_set_to_pan(self):
        """
        Sets current tool to pan
        """
        self.current_tool = ToolConstants.PAN_TOOL

    def callback_save_canvas(self):
        """
        Saves the image canvas as a png image.  This will save the entire canvas, including axes labels and titles.
        """
        save_fname = asksaveasfilename()
        if "." not in os.path.basename(save_fname):
            save_fname = save_fname + ".png"
        self.axes_canvas.save_full_canvas_as_png(save_fname)

    def callback_save_image(self):
        """
        Saves the currently displayed image in the image canvas.  This will save the image only, and will not save
        any axes, axes labels, or titles.
        """
        save_fname = asksaveasfilename()
        if "." not in os.path.basename(save_fname):
            save_fname = save_fname + ".png"
        image_data = self.canvas.variables.canvas_image_object.display_image
        pil_image = PIL.Image.fromarray(image_data)
        pil_image.save(save_fname)

    def callback_hide_show_margins(self):
        """
        Allows the user to toggle the margins settings in the toolbar.  The margins will be shown if the
        margins checkbox is selected in the toolbar.  If the margins checkbox is unselected the margins settings
        will become hidden.
        """
        show_margins = self.toolbar.margins_checkbox.is_selected()
        if show_margins is False:
            self.toolbar.left_margin_label.master.forget()
        else:
            self.toolbar.left_margin_label.master.pack()

    def callback_hide_show_axes_controls(self):
        """
        Allows the user to toggle the axes controls settings in the toolbar.  The axes controls will be shown if
        the axes labels checkbox is selected in the toolbar.  If the axes labels checkbox is unselected the axes
        controls will be hidden.
        """
        show_axes_controls = self.toolbar.axes_labels_checkbox.is_selected()
        if show_axes_controls is False:
            self.toolbar.title_label.master.forget()
        else:
            self.toolbar.title_label.master.pack()

    def callback_hide_show_canvas_size_controls(self):
        """
        Allows the user to toggle the canvas size controls.  This option is available by default if the image panel
        is set up to not allow dynamic resizing.  In this case, the user can set the canvas size using the
        canvas size controls.
        """
        show_canvas_size_controls = self.toolbar.canvas_size_checkbox.is_selected()
        if show_canvas_size_controls:
            self.toolbar.canvas_width_label.master.pack()
        else:
            self.toolbar.canvas_width_label.master.forget()

    def callback_update_axes(self, event):
        """
        Updates all canvas titles, x axis labels, y axis labels, and margin settings
        """
        self.axes_canvas.title = self.toolbar.title.get()
        self.axes_canvas.x_label = self.toolbar.x.get()
        self.axes_canvas.y_label = self.toolbar.y.get()

        self.axes_canvas.left_margin_pixels = int(self.toolbar.left_margin.get())
        self.axes_canvas.right_margin_pixels = int(self.toolbar.right_margin.get())
        self.axes_canvas.top_margin_pixels = int(self.toolbar.top_margin.get())
        self.axes_canvas.bottom_margin_pixels = int(self.toolbar.bottom_margin.get())

        self.update_everything()

    def callback_update_canvas_size(self, event):
        """
        Updates the canvas size.  This is generally done explicitly by the user using the toolbar settings when
        dynamic resizing has been disabled.
        """
        width = int(self.toolbar.canvas_width.get())
        height = int(self.toolbar.canvas_height.get())
        self.config(width=width+20)
        self.toolbar.config(width=width)
        self.toolbar.pack(expand=True)
        self.pack(expand=True)
        self.image_frame.config(width=width, height=height)
        self.axes_canvas.set_canvas_size(width, height)
        self.canvas.set_canvas_size(width - self.axes_canvas.left_margin_pixels - self.axes_canvas.right_margin_pixels,
                                    height - self.axes_canvas.top_margin_pixels - self.axes_canvas.bottom_margin_pixels)
        self.update_everything()

    def set_image_reader(self, image_reader):
        """
        Sets the image reader.  The image reader should be a subclass of the "ImageReader" class.

        Parameters
        ----------
        image_reader : ImageReader

        Returns
        -------
        None
        """
        self.axes_canvas.set_image_reader(image_reader)

    def do_nothing(self, event):
        """
        Does nothing.  This is used when we need to explicitly disable a callback.  For instance, when dynamic resizing
        is enabled a callback is assigned to "on_resize".  When we want to disable dynamic resizing that callback must
        be disabled.  Assigning the "do_nothing" callback to "on_resize" disables the resize callback, eliminating
        a resize response when the window size changes, and allows the user to resize the image canvas manually.
        """
        pass

    @property
    def resizeable(self):
        return self._resizeable

    @resizeable.setter
    def resizeable(self, value):
        """
        Enables or disables dynamic resizing of the image canvas.

        Parameters
        ----------
        value : bool

        Returns
        -------
        None
        """
        self._resizeable = value
        if value is False:
            self.show_canvas_size_controls()
            self.on_resize(self.do_nothing)
        else:
            self.hide_canvas_size_controls()
            self.on_resize(self.callback_resize)

    @property
    def current_tool(self):
        return self.image_frame.outer_canvas.canvas.variables.current_tool

    @current_tool.setter
    def current_tool(self, value):
        """
        Sets the image canvases current tool.  The value should be one of the strings defined in the ToolConstants
        class in "image_canvas.py"

        Parameters
        ----------
        value : str

        Returns
        -------
        None
        """
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

    def set_min_canvas_size(self, x, y):
        """
        minimum canvas size.  When dynamic resizing is enabled the canvas will stop resizing after the minimum
        dimensions are reached.

        Parameters
        ----------
        x : int
        y: int

        Returns
        -------
        None
        """

        self.axes_canvas.variables.min_width = x
        self.axes_canvas.variables.min_height = y

    def set_max_canvas_size(self, x, y):
        """
        maximum canvas size.  When dynamic resizing is enabled the canvas will stop resizing after the maximum
        dimensions are reached.

        Parameters
        ----------
        x : int
        y: int

        Returns
        -------
        None
        """

        self.axes_canvas.variables.max_width = x
        self.axes_canvas.variables.max_height = y

    def callback_resize(self, event):
        pass
