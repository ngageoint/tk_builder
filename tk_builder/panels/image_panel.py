import os
import tkinter
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo
import PIL.Image
from typing import List

from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import basic_widgets, widget_descriptors
from tk_builder.widgets.image_canvas import ImageCanvas, ToolConstants, ShapeTypeConstants
from tk_builder.image_readers.image_reader import ImageReader
from tk_builder import file_filters

from sarpy.compliance import string_types


__classification__ = "UNCLASSIFIED"
__author__ = ("Jason Casey", "Thomas McCullough")


class CanvasSize(WidgetPanel):
    _widget_list = (
        "canvas_size_checkbox", "canvas_width_label", "canvas_width", "canvas_height_label", "canvas_height", "set_size")
    canvas_size_checkbox = widget_descriptors.CheckButtonDescriptor(
        'canvas_size_checkbox', default_text='canvas\nsize:',
        docstring='Should the canvas size elements be shown?')  # type: basic_widgets.CheckButton
    canvas_width_label = widget_descriptors.LabelDescriptor(
        'canvas_width_label', default_text='width:',
        docstring='The canvas width label.')  # type: basic_widgets.Label
    canvas_width = widget_descriptors.EntryDescriptor(
        'canvas_width', default_text='600',
        docstring='The canvas width value.')  # type: basic_widgets.Entry
    canvas_height_label = widget_descriptors.LabelDescriptor(
        'canvas_height_label', default_text='height:',
        docstring='The canvas height label.')  # type: basic_widgets.Label
    canvas_height = widget_descriptors.EntryDescriptor(
        'canvas_height', default_text='400',
        docstring='The canvas height value.')  # type: basic_widgets.Entry
    set_size = widget_descriptors.ButtonDescriptor(
        'set_size', default_text='set size',
        docstring='Button to perform the actual size set.')  # type: basic_widgets.Button

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent : ImagePanel
        """

        WidgetPanel.__init__(self, parent)
        self.init_w_horizontal_layout()


class Toolbar(WidgetPanel):
    tool_controls = (
        'tool_label', 'zoom_in', 'zoom_out', 'pan', 'select', 'view',
        'select_closest_shape', 'edit_shape', 'shift_shape', 'new_shape')
    shape_controls = ('shape_label', 'point', 'line', 'rect', 'ellipse', 'arrow', 'polygon', 'text')
    other_controls = ("save_canvas", "save_image", "size_controls")
    _widget_list = (tool_controls, shape_controls, other_controls)

    # create the tool descriptors
    tool_label = widget_descriptors.LabelDescriptor(
        'tool_label', default_text='tool:',  docstring='The label for the tool series of radiobuttons.')  # type: basic_widgets.Label
    zoom_in = widget_descriptors.RadioButtonDescriptor(
        'zoom_in', default_text='Zoom In', docstring='Zoom in selector.')  # type: basic_widgets.RadioButton
    zoom_out = widget_descriptors.RadioButtonDescriptor(
        'zoom_out', default_text='Zoom Out', docstring='Zoom out selector.')  # type: basic_widgets.RadioButton
    pan = widget_descriptors.RadioButtonDescriptor(
        'pan', default_text='Pan', docstring='Pan selector.')  # type: basic_widgets.RadioButton
    select = widget_descriptors.RadioButtonDescriptor(
        'select', default_text='Select', docstring='Select selector.')  # type: basic_widgets.RadioButton
    view = widget_descriptors.RadioButtonDescriptor(
        'view', default_text='View', docstring='View selector.')  # type: basic_widgets.RadioButton
    select_closest_shape = widget_descriptors.RadioButtonDescriptor(
        'select_closest_shape', default_text='Choose\nShape', docstring='Select closest shape selector.')  # type: basic_widgets.RadioButton
    edit_shape = widget_descriptors.RadioButtonDescriptor(
        'edit_shape', default_text='Edit\nShape', docstring='Edit shape selector.')  # type: basic_widgets.RadioButton
    shift_shape = widget_descriptors.RadioButtonDescriptor(
        'shift_shape', default_text='Shift\nShape', docstring='Shift shape selector.')  # type: basic_widgets.RadioButton
    new_shape = widget_descriptors.RadioButtonDescriptor(
        'new_shape', default_text='New\nShape', docstring='New shape selector.')  # type: basic_widgets.RadioButton
    # create the shape descriptors
    shape_label = widget_descriptors.LabelDescriptor(
        'shape_label', default_text='shape type:',  docstring='The label for the shape series of radiobuttons.')  # type: basic_widgets.Label
    point = widget_descriptors.RadioButtonDescriptor(
        'point', default_text='point', docstring='point selector.')  # type: basic_widgets.RadioButton
    line = widget_descriptors.RadioButtonDescriptor(
        'line', default_text='line', docstring='line selector.')  # type: basic_widgets.RadioButton
    rect = widget_descriptors.RadioButtonDescriptor(
        'rect', default_text='rect', docstring='rect selector.')  # type: basic_widgets.RadioButton
    ellipse = widget_descriptors.RadioButtonDescriptor(
        'ellipse', default_text='ellipse', docstring='ellipse selector.')  # type: basic_widgets.RadioButton
    arrow = widget_descriptors.RadioButtonDescriptor(
        'arrow', default_text='arrow', docstring='arrow selector.')  # type: basic_widgets.RadioButton
    polygon = widget_descriptors.RadioButtonDescriptor(
        'polygon', default_text='polygon', docstring='polygon selector.')  # type: basic_widgets.RadioButton
    text = widget_descriptors.RadioButtonDescriptor(
        'text', default_text='text', docstring='text selector.')  # type: basic_widgets.RadioButton
    # the remaining element descriptors
    save_canvas = widget_descriptors.ButtonDescriptor(
        'save_canvas', default_text='save canvas', docstring='Save the present canvas and contents to image file.')  # type: basic_widgets.Button
    save_image = widget_descriptors.ButtonDescriptor(
        'save_image', default_text='save image', docstring='Save the present canvas to image file.')  # type: basic_widgets.Button
    size_controls = widget_descriptors.TypedDescriptor(
        'size_controls', CanvasSize, docstring='The canvas size controls.')  # type: CanvasSize

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent : ImagePanel
        """

        WidgetPanel.__init__(self, parent)
        self.init_w_rows()


class ImagePanel(WidgetPanel):
    """
    This utilizes the ImageCanvas to display raster and vector data.  A toolbar
    providing a set of common tools such as pan and zoom functionality is included.

    Mouse zoom operations using the mouse wheel are enabled by default. Other
    functionality includes axes and margins in the case the user wishes to display
    X/Y axes, titles, etc for 2 dimensional data displays or plots.
    """

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)
        self._the_tool = tkinter.IntVar(self, value=ToolConstants.VIEW)
        self._the_shape = tkinter.IntVar(self, value=ShapeTypeConstants.POLYGON)
        self._image_save_directory = os.path.expanduser('~')
        self.canvas = ImageCanvas(self)
        self.toolbar = Toolbar(self)
        self._set_toolbar_callbacks()

        # set up callbacks - sync changes from image canvas
        self.canvas.bind('<<CurrentToolChanged>>', self.callback_update_tool)
        self.canvas.bind('<<ShapeTypeChanged>>', self.callback_update_shape)

        self.pack()
        self.toolbar.pack(side='top', expand=tkinter.NO, fill=tkinter.BOTH)
        self.canvas.pack(side='bottom', fill=tkinter.BOTH, expand=1)

        self.set_max_canvas_size(1920, 1080)
        self.resizeable = False

    def _set_toolbar_callbacks(self):
        # set the toolbar tool callbacks
        self.toolbar.zoom_in.config(variable=self._the_tool, value=ToolConstants.ZOOM_IN, command=self.callback_set_tool)
        self.toolbar.zoom_out.config(variable=self._the_tool, value=ToolConstants.ZOOM_OUT, command=self.callback_set_tool)
        self.toolbar.pan.config(variable=self._the_tool, value=ToolConstants.PAN, command=self.callback_set_tool)
        self.toolbar.select.config(variable=self._the_tool, value=ToolConstants.SELECT, command=self.callback_set_tool)
        self.toolbar.view.config(variable=self._the_tool, value=ToolConstants.VIEW, command=self.callback_set_tool)
        self.toolbar.select_closest_shape.config(variable=self._the_tool, value=ToolConstants.SELECT_CLOSEST_SHAPE, command=self.callback_set_tool)
        self.toolbar.edit_shape.config(variable=self._the_tool, value=ToolConstants.EDIT_SHAPE, command=self.callback_set_tool)
        self.toolbar.shift_shape.config(variable=self._the_tool, value=ToolConstants.SHIFT_SHAPE, command=self.callback_set_tool)
        self.toolbar.new_shape.config(variable=self._the_tool, value=ToolConstants.NEW_SHAPE, command=self.callback_set_tool)
        # set the toolbar shape callbacks
        self.toolbar.point.config(variable=self._the_shape, value=ShapeTypeConstants.POINT, command=self.callback_set_shape)
        self.toolbar.line.config(variable=self._the_shape, value=ShapeTypeConstants.LINE, command=self.callback_set_shape)
        self.toolbar.rect.config(variable=self._the_shape, value=ShapeTypeConstants.RECT, command=self.callback_set_shape)
        self.toolbar.ellipse.config(variable=self._the_shape, value=ShapeTypeConstants.ELLIPSE, command=self.callback_set_shape)
        self.toolbar.arrow.config(variable=self._the_shape, value=ShapeTypeConstants.ARROW, command=self.callback_set_shape)
        self.toolbar.polygon.config(variable=self._the_shape, value=ShapeTypeConstants.POLYGON, command=self.callback_set_shape)
        self.toolbar.text.config(variable=self._the_shape, value=ShapeTypeConstants.TEXT, command=self.callback_set_shape)
        # set the save callbacks
        self.toolbar.save_canvas.config(command=self.callback_save_canvas)
        self.toolbar.save_image.config(command=self.callback_save_image)
        # set the canvas size callbacks
        self.toolbar.size_controls.canvas_size_checkbox.config(command=self.callback_hide_show_canvas_size_controls)
        width_validator = (self.register(self.validate_width), '%P')
        self.toolbar.size_controls.canvas_width.config(validate='focusout', validatecommand=width_validator)
        height_validator = (self.register(self.validate_height), '%P')
        self.toolbar.size_controls.canvas_height.config(validate='focusout', validatecommand=height_validator)
        self.toolbar.size_controls.set_size.config(command=self.perform_resize)

    @property
    def the_tool(self):
        return self._the_tool.get()

    @the_tool.setter
    def the_tool(self, value):
        the_value = ToolConstants.validate(value)
        if the_value is None:
            raise ValueError('Unhandled tool value {}'.format(value))
        self._the_tool.set(the_value)

    @property
    def the_shape(self):
        return self._the_shape

    @the_shape.setter
    def the_shape(self, value):
        the_value = ShapeTypeConstants.validate(value)
        if the_value is None:
            raise ValueError('Unhandled shape value {}'.format(value))
        self._the_shape.set(the_value)

    @property
    def resizeable(self):
        return self.canvas.resizeable

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

        self.canvas.resizeable = value
        if value is False:
            self.show_canvas_size_controls()
        else:
            self.hide_canvas_size_controls()

    @property
    def current_tool(self):
        """
        int: The current tool
        """

        return self.canvas.current_tool

    @current_tool.setter
    def current_tool(self, value):
        """
        Sets the image canvas current tool. This should be in keeping with the ToolConstants
        class in "image_canvas.py".

        Parameters
        ----------
        value : int|str

        Returns
        -------
        None
        """

        self.canvas.set_tool(value)

    def set_min_canvas_size(self, x, y):
        """
        Sets minimum canvas size.  When dynamic resizing is enabled, the canvas will
        stop resizing after the minimum dimensions are reached.

        Parameters
        ----------
        x : int
            The width, in pixels.
        y: int
            The height, in pixels.
        """

        self.canvas.variables.state.min_width = x
        self.canvas.variables.state.min_height = y

    def set_max_canvas_size(self, x, y):
        """
        Sets maximum canvas size.  When dynamic resizing is enabled, the canvas will
        stop resizing after the maximum dimensions are reached.

        Parameters
        ----------
        x : int
            The width, in pixels.
        y: int
            The height, in pixels.
        """

        self.canvas.variables.state.max_width = x
        self.canvas.variables.state.max_height = y

    def update_image_save_directory(self, pathname):
        """
        Updates the initial browsing directory for saving image files, to the parent directory
        of the provided path.

        Parameters
        ----------
        pathname : None|str

        Returns
        -------
        None
        """

        if pathname is None or pathname == '':
            self._image_save_directory = os.path.expanduser('~')
        else:
            self._image_save_directory = os.path.split(pathname)[0]

    def validate_width(self, the_value):
        """
        Helper method validating the canvas width value.

        Parameters
        ----------
        the_value : str
        """

        try:
            the_int = int(the_value)
        except:
            return False
        if the_int < self.canvas.variables.state.min_width or the_int > self.canvas.variables.state.max_width:
            showinfo('Width requirement',
                     message='Width must be in the range {} - {}'.format(self.canvas.variables.state.min_width,
                                                                         self.canvas.variables.state.max_width))
            return False
        return True

    def validate_height(self, the_value):
        """
        Helper method validating the canvas height value.

        Parameters
        ----------
        the_value : str
        """

        try:
            the_int = int(the_value)
        except:
            return False
        if the_int < self.canvas.variables.state.min_height or the_int > self.canvas.variables.state.max_height:
            showinfo('Height requirement',
                     message='Height must be in the range {} - {}'.format(self.canvas.variables.state.min_height,
                                                                         self.canvas.variables.state.max_height))
            return False
        return True

    # methods for showing or hiding elements
    def hide_controls(self):
        """
        Hides all the controls.
        """

        self.toolbar.forget_row(0)
        self.toolbar.forget_row(1)
        self.toolbar.forget_row(2)

    def hide_tools(self, tool_list=None):
        """
        Hide some elements of the tools collection.

        Parameters
        ----------
        tool_list : None|str|List[str]
            None hides all tools. Otherwise, this should be the tool or tools to hide
            from view. Note that `shape_drawing` provides an alias to the collection of tools
            associated with shape drawing (i.e. 'select_closest_shape', 'edit_shape',
            'shift_shape', 'new_shape')
        """

        SHAPE_DRAWING = ['select_closest_shape', 'edit_shape', 'shift_shape', 'new_shape']

        def check_entry(temp_list, the_entry):
            if isinstance(the_entry, string_types):
                temp = the_entry.lower()
                if temp == 'shape_drawing':
                    for temp_tool in SHAPE_DRAWING:
                        check_entry(temp_list, temp_tool)
                else:
                    if temp not in self.toolbar.tool_controls:
                        raise ValueError("Can't hide unknown tool element {}".format(the_entry))
                    if temp not in temp_list:
                        temp_list.append(temp)
            else:
                for temp in the_entry:
                    check_entry(temp_list, temp)

        # validate input
        if tool_list is None:
            temp_tool_list = self.toolbar.tool_controls
        else:
            temp_tool_list = []
            check_entry(temp_tool_list, tool_list)

        # forget the packing for the given elements
        if set(temp_tool_list) == set(self.toolbar.tool_controls):
            self.toolbar.tool_label.master.forget()
        else:
            # only forget some elements
            for the_item in temp_tool_list:
                getattr(self.toolbar, the_item).pack_forget()

    def hide_shapes(self, shape_list=None):
        """
        Hide some elements of the shapes collection.

        Parameters
        ----------
        shape_list : None|str|List[str]
            None hides all shapes. Otherwise, this should be the shape or shapes to
            hide from view.
        """

        def check_entry(temp_list, the_entry):
            if isinstance(the_entry, string_types):
                temp = the_entry.lower()
                if temp not in self.toolbar.shape_controls:
                    raise ValueError("Can't hide unknown shape element {}".format(the_entry))
                if temp not in temp_list:
                    temp_list.append(temp)
            else:
                for temp in the_entry:
                    check_entry(temp_list, temp)

        # validate elements
        if shape_list is None:
            temp_shape_list = self.toolbar.shape_controls
        else:
            temp_shape_list = []
            check_entry(temp_shape_list, shape_list)

        if set(temp_shape_list) == set(self.toolbar.shape_controls):
            self.toolbar.shape_label.master.forget()
        else:
            for the_item in temp_shape_list:
                getattr(self.toolbar, the_item).pack_forget()

    def hide_canvas_size_controls(self):
        """
        Hides the canvas size controls checkbox in the toolbar
        """

        self.toolbar.size_controls.canvas_size_checkbox.master.pack_forget()

    def show_canvas_size_controls(self):
        """
        Shows / unhides the canvas size controls checkbox in the toolbar
        """

        self.toolbar.size_controls.canvas_size_checkbox.master.pack()

    def callback_hide_show_canvas_size_controls(self):
        """
        Allows the user to toggle the canvas size controls.  This option is available
        by default if the image panel is set up to not allow dynamic resizing.  In
        this case, the user can set the canvas size using the canvas size controls.
        """

        # NB: this is bound by the toolbar itself.
        show_canvas_size_controls = self.toolbar.size_controls.canvas_size_checkbox.is_selected()
        if show_canvas_size_controls:
            self.toolbar.size_controls.master.pack()
        else:
            self.toolbar.size_controls.master.forget()

    # callbacks
    def callback_canvas_mouse_zoom(self, event):
        """
        Handles the canvas zoom event then updates axes
        """

        self.canvas.callback_mouse_zoom(event)
        self.update_everything()

    def callback_set_tool(self):
        """
        Handle that our selected tool on the toolbar has changed.
        """

        # NB: this is bound by the toolbar itself.
        if self.current_tool != self.the_tool:
            self.current_tool = self.the_tool

    # noinspection PyUnusedLocal
    def callback_update_tool(self, event):
        """
        Handle the message from the image canvas that the tool has changed.

        Parameters
        ----------
        event
        """

        if self.current_tool != self.the_tool:
            self.the_tool = self.current_tool

    def callback_set_shape(self):
        """
        Handle that the selected shape on the toolbar has changed.
        """

        # NB: this is bound by the toolbar itself
        if self.canvas.new_shape_type != self.the_shape:
            self.canvas.new_shape_type = self.the_shape

    # noinspection PyUnusedLocal
    def callback_update_shape(self, event):
        """
        Handle the message from the image canvas that the new shape type has changed.

        Parameters
        ----------
        event
        """

        if self.canvas.new_shape_type != self.the_shape:
            self.the_shape = self.canvas.new_shape_type

    def callback_save_canvas(self):
        """
        Saves the image canvas as a png image.  This will save the entire canvas,
        including axes labels and titles.
        """

        save_fname = asksaveasfilename(
            initialdir=self._image_save_directory,
            title="Select output image file",
            filetypes=file_filters.basic_image_collection)

        if save_fname in ['', ()]:
            return
        if os.path.splitext(save_fname)[1] == '':
            save_fname += '.png'
        self.update_image_save_directory(save_fname)

        self.canvas.save_full_canvas_as_image_file(save_fname)

    def callback_save_image(self):
        """
        Saves the currently displayed image in the image canvas.  This will save
        the image only, and will not save any axes, axes labels, or titles.
        """

        save_fname = asksaveasfilename(
            initialdir=self._image_save_directory,
            title="Select output image file",
            filetypes=file_filters.basic_image_collection)

        if save_fname in ['', ()]:
            return
        if os.path.splitext(save_fname)[1] == '':
            save_fname += '.png'
        self.update_image_save_directory(save_fname)

        image_data = self.canvas.variables.canvas_image_object.display_image
        pil_image = PIL.Image.fromarray(image_data)
        pil_image.save(save_fname)

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

        self.canvas.set_image_reader(image_reader)
        self.update_image_save_directory(image_reader.file_name)

    def do_nothing(self, event):
        """
        Null callback pattern, intended to allow callback disabling.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        pass

    def perform_resize(self):
        """
        Perform the resize.
        """

        the_height = int(self.toolbar.size_controls.canvas_height.get())
        the_width = int(self.toolbar.size_controls.canvas_width.get())
        self.canvas.set_canvas_size(the_width, the_height)

    def update_everything(self):
        """
        Redraw the image canvas contents.
        """
