
__classification__ = "UNCLASSIFIED"
__author__ = ("Jason Casey", "Thomas McCullough")


import os
import tkinter
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import askokcancel
import PIL.Image
from typing import List

from tk_builder.panel_builder import WidgetPanel, WidgetPanelNoLabel
from tk_builder.widgets import basic_widgets, widget_descriptors
from tk_builder.widgets.image_canvas import ImageCanvas
from tk_builder.widgets.image_canvas_tool import ImageCanvasTool, \
    ShapeTypeConstants, get_tool_enum
from tk_builder.image_reader import CanvasImageReader
from tk_builder import file_filters

from sarpy.compliance import string_types, integer_types
from sarpy.visualization.remap import get_remap_list


class Toolbar(WidgetPanelNoLabel):
    tool_controls = (
        'tool_label', 'zoom_in', 'zoom_out', 'pan', 'select', 'view',
        'select_closest_shape', 'edit_shape', 'shift_shape', 'new_shape')
    shape_controls = (
        'shape_label', 'point', 'line', 'arrow', 'rect', 'ellipse',
        'polygon', 'text')
    other_controls = (
        "save_canvas", "save_image", "remap_label", "remap_combo",
        "select_index_label", "select_index_combo")
    _widget_list = (tool_controls, shape_controls, other_controls)

    # create the tool descriptors
    tool_label = widget_descriptors.LabelDescriptor(
        'tool_label', default_text='tool:',
        docstring='The label for the tool series of radiobuttons.')  # type: basic_widgets.Label
    zoom_in = widget_descriptors.RadioButtonDescriptor(
        'zoom_in', default_text='Zoom In',
        docstring='Zoom in selector.')  # type: basic_widgets.RadioButton
    zoom_out = widget_descriptors.RadioButtonDescriptor(
        'zoom_out', default_text='Zoom Out',
        docstring='Zoom out selector.')  # type: basic_widgets.RadioButton
    pan = widget_descriptors.RadioButtonDescriptor(
        'pan', default_text='Pan',
        docstring='Pan selector.')  # type: basic_widgets.RadioButton
    select = widget_descriptors.RadioButtonDescriptor(
        'select', default_text='Select',
        docstring='Select selector.')  # type: basic_widgets.RadioButton
    view = widget_descriptors.RadioButtonDescriptor(
        'view', default_text='View',
        docstring='View selector.')  # type: basic_widgets.RadioButton
    select_closest_shape = widget_descriptors.RadioButtonDescriptor(
        'select_closest_shape', default_text='Choose\nShape',
        docstring='Select closest shape selector.')  # type: basic_widgets.RadioButton
    edit_shape = widget_descriptors.RadioButtonDescriptor(
        'edit_shape', default_text='Edit\nShape',
        docstring='Edit shape selector.')  # type: basic_widgets.RadioButton
    shift_shape = widget_descriptors.RadioButtonDescriptor(
        'shift_shape', default_text='Shift\nShape',
        docstring='Shift shape selector.')  # type: basic_widgets.RadioButton
    new_shape = widget_descriptors.RadioButtonDescriptor(
        'new_shape', default_text='New\nShape',
        docstring='New shape selector.')  # type: basic_widgets.RadioButton
    # create the shape descriptors
    shape_label = widget_descriptors.LabelDescriptor(
        'shape_label', default_text='shape type:',
        docstring='The label for the shape series of radiobuttons.')  # type: basic_widgets.Label
    point = widget_descriptors.RadioButtonDescriptor(
        'point', default_text='point',
        docstring='point selector.')  # type: basic_widgets.RadioButton
    line = widget_descriptors.RadioButtonDescriptor(
        'line', default_text='line',
        docstring='line selector.')  # type: basic_widgets.RadioButton
    arrow = widget_descriptors.RadioButtonDescriptor(
        'arrow', default_text='arrow',
        docstring='arrow selector.')  # type: basic_widgets.RadioButton
    rect = widget_descriptors.RadioButtonDescriptor(
        'rect', default_text='rect',
        docstring='rect selector.')  # type: basic_widgets.RadioButton
    ellipse = widget_descriptors.RadioButtonDescriptor(
        'ellipse', default_text='ellipse',
        docstring='ellipse selector.')  # type: basic_widgets.RadioButton
    polygon = widget_descriptors.RadioButtonDescriptor(
        'polygon', default_text='polygon',
        docstring='polygon selector.')  # type: basic_widgets.RadioButton
    text = widget_descriptors.RadioButtonDescriptor(
        'text', default_text='text',
        docstring='text selector.')  # type: basic_widgets.RadioButton
    # the remaining element descriptors
    save_canvas = widget_descriptors.ButtonDescriptor(
        'save_canvas', default_text='save canvas',
        docstring='Save the present canvas and contents to image file.')  # type: basic_widgets.Button
    save_image = widget_descriptors.ButtonDescriptor(
        'save_image', default_text='save image',
        docstring='Save the present canvas to image file.')  # type: basic_widgets.Button
    remap_label = widget_descriptors.LabelDescriptor(
        'remap_label', default_text='remap:',
        docstring='The remap label.')  # type: basic_widgets.Label
    remap_combo = widget_descriptors.ComboboxDescriptor(
        'remap_combo', default_text='',
        docstring='The remap value')  # type: basic_widgets.Combobox
    select_index_label = widget_descriptors.LabelDescriptor(
        'select_index_label', default_text='image\nindex:',
        docstring='The image index selection label.')  # type: basic_widgets.Label
    select_index_combo = widget_descriptors.ComboboxDescriptor(
        'select_index_combo', default_text='',
        docstring='The image index selection')  # type: basic_widgets.Combobox

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent : ImagePanel
        """

        WidgetPanelNoLabel.__init__(self, parent)
        self.init_w_rows()


class ImagePanel(WidgetPanel):
    """
    The main base widget on which to base most apps where image viewing is central
    to operation.

    Image data display functionality is provided by an embedded ImageCanvas widget.
    Also embedded is toolbar allowing easy selection of functionality like zooming,
    panning, region selection, creation of a variety of vector shapes, and saving
    of the presently displayed image to an image file.
    """

    def __init__(self, parent):
        self.parent = parent
        WidgetPanel.__init__(self, parent)
        self._the_tool = tkinter.IntVar(self, value=get_tool_enum('VIEW'))
        self._the_shape = tkinter.IntVar(self, value=ShapeTypeConstants.POLYGON)
        self._image_save_directory = os.path.expanduser('~')
        self.canvas = ImageCanvas(self)
        self.toolbar = Toolbar(self)
        self.toolbar.config(relief=tkinter.RIDGE)
        self._set_toolbar_callbacks()

        # set up callbacks - sync changes from image canvas
        self.canvas.bind('<<CurrentToolChanged>>', self.callback_update_tool)
        self.canvas.bind('<<ShapeTypeChanged>>', self.callback_update_shape)

        self.pack()
        # handle the appearance of several toolbar labels
        self.toolbar.tool_label.configure(anchor=tkinter.CENTER, relief=tkinter.RIDGE, justify=tkinter.RIGHT)
        self.toolbar.shape_label.config(anchor=tkinter.CENTER, relief=tkinter.RIDGE, justify=tkinter.RIGHT)
        self.toolbar.remap_label.config(anchor=tkinter.CENTER, relief=tkinter.RIDGE, justify=tkinter.RIGHT)
        self.toolbar.select_index_label.config(anchor=tkinter.CENTER, relief=tkinter.RIDGE, justify=tkinter.RIGHT)
        self.toolbar.pack(side='top', expand=tkinter.NO, fill=tkinter.BOTH)
        self.canvas.pack(side='bottom', fill=tkinter.BOTH, expand=1)

        self.set_max_canvas_size(1920, 1080)

    def _set_toolbar_callbacks(self):
        # set the toolbar tool callbacks
        self.toolbar.zoom_in.config(
            variable=self._the_tool, value=get_tool_enum('ZOOM_IN'), command=self.callback_set_tool)
        self.toolbar.zoom_out.config(
            variable=self._the_tool, value=get_tool_enum('ZOOM_OUT'), command=self.callback_set_tool)
        self.toolbar.pan.config(
            variable=self._the_tool, value=get_tool_enum('PAN'), command=self.callback_set_tool)
        self.toolbar.select.config(
            variable=self._the_tool, value=get_tool_enum('SELECT'), command=self.callback_set_tool)
        self.toolbar.view.config(
            variable=self._the_tool, value=get_tool_enum('VIEW'), command=self.callback_set_tool)
        self.toolbar.select_closest_shape.config(
            variable=self._the_tool, value=get_tool_enum('SHAPE_SELECT'), command=self.callback_set_tool)
        self.toolbar.edit_shape.config(
            variable=self._the_tool, value=get_tool_enum('EDIT_SHAPE'), command=self.callback_set_tool)
        self.toolbar.shift_shape.config(
            variable=self._the_tool, value=get_tool_enum('SHIFT_SHAPE'), command=self.callback_set_tool)
        self.toolbar.new_shape.config(
            variable=self._the_tool, value=get_tool_enum('NEW_SHAPE'), command=self.callback_set_tool)

        # set the toolbar shape callbacks
        self.toolbar.point.config(
            variable=self._the_shape, value=ShapeTypeConstants.POINT, command=self.callback_set_shape)
        self.toolbar.line.config(
            variable=self._the_shape, value=ShapeTypeConstants.LINE, command=self.callback_set_shape)
        self.toolbar.arrow.config(
            variable=self._the_shape, value=ShapeTypeConstants.ARROW, command=self.callback_set_shape)
        self.toolbar.rect.config(
            variable=self._the_shape, value=ShapeTypeConstants.RECT, command=self.callback_set_shape)
        self.toolbar.ellipse.config(
            variable=self._the_shape, value=ShapeTypeConstants.ELLIPSE, command=self.callback_set_shape)
        self.toolbar.polygon.config(
            variable=self._the_shape, value=ShapeTypeConstants.POLYGON, command=self.callback_set_shape)
        self.toolbar.text.config(
            variable=self._the_shape, value=ShapeTypeConstants.TEXT, command=self.callback_set_shape)
        # set the save callbacks
        self.toolbar.save_canvas.config(command=self.callback_save_canvas)
        self.toolbar.save_image.config(command=self.callback_save_image)
        # set the other callbacks
        self.toolbar.remap_combo.on_selection(self.callback_remap)
        self.toolbar.select_index_combo.on_selection(self.callback_select_index)

    @property
    def the_tool(self):
        return self._the_tool.get()

    @the_tool.setter
    def the_tool(self, value):
        if isinstance(value, integer_types):
            self._the_tool.set(value)
        elif isinstance(value, string_types):
            self._the_tool.set(get_tool_enum(value))
        else:
            raise ValueError('Unhandled tool value {}'.format(value))

    @property
    def the_shape(self):
        return self._the_shape.get()

    @the_shape.setter
    def the_shape(self, value):
        the_value = ShapeTypeConstants.validate(value)
        if the_value is None:
            raise ValueError('Unhandled shape value {}'.format(value))
        self._the_shape.set(the_value)

    @property
    def current_tool(self):
        # type: () -> ImageCanvasTool
        """
        ImageCanvasTool: The current tool
        """

        return self.canvas.current_tool

    @current_tool.setter
    def current_tool(self, value):
        """
        Sets the image canvas current tool.

        Parameters
        ----------
        value : int|str

        Returns
        -------
        None
        """

        if isinstance(value, integer_types) or isinstance(value, string_types):
            self.canvas.current_tool = value
        else:
            raise TypeError('Expected an integer or string value')

    @property
    def current_tool_enum(self):
        """
        int: The enum value for the current tool.
        """

        return self.canvas.variables.get_tool_enum(self.canvas.current_tool)

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

    def _update_image_save_directory(self, pathname):
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

    def _populate_select_index_combo(self):
        """
        Populate the index selection combobox. This should be called when a new
        reader is selected.
        """

        if self.canvas.variables.canvas_image_object is None or \
                self.canvas.variables.canvas_image_object.image_reader is None:
            index_values = []
        else:
            index_values = [
                str(entry) for entry in
                range(self.canvas.variables.canvas_image_object.image_reader.image_count)]

        self.toolbar.select_index_combo.update_combobox_values(index_values)
        if len(index_values) == 0:
            self.toolbar.select_index_combo.set('')
            self.toolbar.select_index_combo.config(state='disabled')
        else:
            current_value = self.canvas.variables.canvas_image_object.image_reader.index
            self.toolbar.select_index_combo.current(current_value)
            self.toolbar.select_index_combo.config(state='readonly')

    def _populate_remap_combo(self):
        """
        Populate the remap combobox state. This should be called when a new reader is
        selected.
        """

        if self.canvas.variables.canvas_image_object is None or \
                self.canvas.variables.canvas_image_object.image_reader is None:
            remapable = False
        else:
            remapable = self.canvas.variables.canvas_image_object.image_reader.remapable

        if remapable:
            # get the old value
            old_value = self.toolbar.remap_combo.get()
            # populate the list of values
            remap_values = [entry[0] for entry in get_remap_list()]
            self.toolbar.remap_combo.update_combobox_values(remap_values)
            if old_value in remap_values:
                self.toolbar.remap_combo.set(old_value)
            else:
                self.toolbar.remap_combo.current(0)
            self.toolbar.remap_combo.config(state='readonly')
        else:
            self.toolbar.remap_combo.config(state='disabled')

    # methods for showing/hiding/enabling/disabling elements
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

    def hide_remap_combo(self):
        """
        Hides the remap combobox.
        """

        self.toolbar.remap_label.pack_forget()
        self.toolbar.remap_combo.pack_forget()

    def hide_select_index(self):
        """
        Hides the index selection label and combobox.
        """

        self.toolbar.select_index_label.pack_forget()
        self.toolbar.select_index_combo.pack_forget()

    def disable_shapes(self):
        """
        Disable the shapes selection.
        """

        for name in self.toolbar.shape_controls[1:]:
            getattr(self.toolbar, name).state(['disabled'])

    def enable_shapes(self):
        """
        Enable the shapes selection.
        """

        for name in self.toolbar.shape_controls[1:]:
            getattr(self.toolbar, name).state(['!disabled'])

    def disable_tools(self):
        """
        Disable the tools selection.
        """

        for name in self.toolbar.tool_controls[1:]:
            getattr(self.toolbar, name).state(['disabled'])

    def enable_tools(self):
        """
        Enable the tools selection.
        """

        for name in self.toolbar.tool_controls[1:]:
            getattr(self.toolbar, name).state(['!disabled'])

    ###########
    # callbacks

    # noinspection PyUnusedLocal
    def callback_select_index(self, event):
        """
        Handles setting the image index.
        """

        the_index = self.toolbar.select_index_combo.get()
        if the_index == '':
            return

        the_index = int(the_index)
        if self.canvas.variables.canvas_image_object.image_reader.index == the_index:
            return  # nothing has changed, so nothing to be done

        self.canvas.set_image_index(the_index)

    # noinspection PyUnusedLocal
    def callback_remap(self, event):
        """
        Handles the remap setting.

        Parameters
        ----------
        event
        """

        remap_dict = {entry[0]: entry[1] for entry in get_remap_list()}
        selection = self.toolbar.remap_combo.get()
        remap_type = remap_dict[selection]
        self.canvas.set_remap(remap_type)

    def callback_set_tool(self):
        """
        Handle that our selected tool on the toolbar has changed.
        """

        # NB: this is bound by the toolbar itself.
        if self.current_tool_enum != self.the_tool:
            self.current_tool = self.the_tool

    # noinspection PyUnusedLocal
    def callback_update_tool(self, event):
        """
        Handle the message from the image canvas that the tool has changed.

        Parameters
        ----------
        event
        """

        if self.the_tool != self.current_tool_enum:
            self.the_tool = self.current_tool_enum

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
        Saves the image canvas as a postscript (.ps) file.  This will save the entire
        canvas, including axes labels and titles.

        Note that postscript is an older vector format which can be processed in a
        variety of ways using the ghostscript application.
        """

        ps_filter = file_filters.create_filter_entry('Postscript Files', '.ps')
        save_fname = asksaveasfilename(
            initialdir=self._image_save_directory,
            title="Select output postscript file",
            filetypes=[ps_filter, file_filters.all_files])

        if save_fname in ['', ()]:
            return
        save_fstem, save_fext = os.path.splitext(save_fname)
        if save_fext not in ['.ps', '.PS']:
            answer = askokcancel(
                'This permits saving only a postscript file, which should have extension `.ps`.\n'
                'Should we change the file extension from `{}` to `.ps`?')
            if answer is True:
                save_fname = save_fstem + '.ps'
            elif answer is None:  # Cancel
                return
        self._update_image_save_directory(save_fname)

        self.canvas.save_full_canvas_as_postscript_file(save_fname)

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
        self._update_image_save_directory(save_fname)

        image_data = self.canvas.variables.canvas_image_object.display_image
        pil_image = PIL.Image.fromarray(image_data)
        pil_image.save(save_fname)

    def set_image_reader(self, image_reader):
        """
        Sets the image reader.  The image reader should be a subclass of the "ImageReader" class.

        Parameters
        ----------
        image_reader : CanvasImageReader

        Returns
        -------
        None
        """

        self.canvas.set_image_reader(image_reader)
        self._update_image_save_directory(image_reader.file_name)
        self._populate_select_index_combo()
        self._populate_remap_combo()

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

    def update_everything(self):
        """
        Redraw the image canvas contents.
        """
