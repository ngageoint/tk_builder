# -*- coding: utf-8 -*-
"""
This module provides functionality for
"""

import PIL.Image
from PIL import ImageTk
import platform
import time
import tkinter
import tkinter.colorchooser as colorchooser
from typing import Union, Tuple, List, Dict

import numpy
from scipy.linalg import norm

from tk_builder.base_elements import BooleanDescriptor, IntegerDescriptor, \
    IntegerTupleDescriptor, StringDescriptor, TypedDescriptor, FloatDescriptor
from tk_builder.widgets import basic_widgets
from tk_builder.utils.color_utils.hex_color_palettes import SeabornHexPalettes
from tk_builder.utils.color_utils import color_utils
from tk_builder.image_readers.image_reader import ImageReader
from tk_builder.utils.geometry_utils import polygon_utils

if platform.system() == "Linux":
    import pyscreenshot as ImageGrab
else:
    from PIL import ImageGrab


class CanvasImage(object):
    """
    The canvas image object.
    """

    image_reader = TypedDescriptor(
        'image_reader', ImageReader,
        docstring='The image reader object.')  # type: ImageReader
    canvas_decimated_image = TypedDescriptor(
        'canvas_decimated_image', numpy.ndarray,
        docstring='The canvas decimated image data.')  # type: numpy.ndarray
    display_image = TypedDescriptor(
        'display_image', numpy.ndarray,
        docstring='The display image data.')  # type: numpy.ndarray
    decimation_factor = IntegerDescriptor(
        'decimation_factor', default_value=1,
        docstring='The decimation factor.')  # type: int
    display_rescaling_factor = FloatDescriptor(
        'display_rescaling_factor', default_value=1.0,
        docstring='The display resclaing factor.')  # type: float
    canvas_full_image_upper_left_yx = IntegerTupleDescriptor(
        'canvas_full_image_upper_left_yx', length=2, default_value=(0, 0),
        docstring='The upper left corner of the full image canvas in '
                  'yx order.')  # type: tuple
    canvas_ny = IntegerDescriptor(
        'canvas_ny',
        docstring='')  # type: int
    canvas_nx = IntegerDescriptor(
        'canvas_nx',
        docstring='')  # type: int
    scale_to_fit_canvas = BooleanDescriptor(
        'scale_to_fit_canvas', default_value=True,
        docstring='Scale the image to fit the canvas?')  # type: bool

    def __init__(self, image_reader, canvas_nx, canvas_ny):
        """

        Parameters
        ----------
        image_reader : ImageReader
        canvas_nx : int
        canvas_ny : int
        """

        self.drop_bands = []  # type: List
        self.image_reader = image_reader
        self.canvas_nx = canvas_nx
        self.canvas_ny = canvas_ny
        self.update_canvas_display_image_from_full_image()

    def get_decimated_image_data_in_full_image_rect(self, full_image_rect, decimation):
        """
        Get decimated data.

        Parameters
        ----------
        full_image_rect : Tuple|List
        decimation : int

        Returns
        -------
        numpy.ndarray
        """

        y_start = full_image_rect[0]
        y_end = full_image_rect[2]
        x_start = full_image_rect[1]
        x_end = full_image_rect[3]
        decimated_data = self.image_reader[y_start:y_end:decimation, x_start:x_end:decimation]
        return decimated_data

    def get_scaled_display_data(self, decimated_image):
        """
        Gets scaled data for display.

        Parameters
        ----------
        decimated_image : numpy.ndarray

        Returns
        -------
        numpy.ndarray
        """

        scale_factor = self.compute_display_scale_factor(decimated_image)
        new_nx = int(decimated_image.shape[1] * scale_factor)
        new_ny = int(decimated_image.shape[0] * scale_factor)
        if new_nx > self.canvas_nx:
            new_nx = self.canvas_nx
        if new_ny > self.canvas_ny:
            new_ny = self.canvas_ny
        if len(self.drop_bands) != 0:
            zeros_image = numpy.zeros_like(decimated_image[:, :, 0])
            for drop_band in self.drop_bands:
                decimated_image[:, :, drop_band] = zeros_image
        pil_image = PIL.Image.fromarray(decimated_image)
        display_image = pil_image.resize((new_nx, new_ny))
        return numpy.array(display_image)

    def decimated_image_coords_to_display_image_coords(self, decimated_image_yx_cords):
        """
        Convert from decimated image coordinates to display coordinates.

        Parameters
        ----------
        decimated_image_yx_cords : List[Tuple[float, float]]

        Returns
        -------
        List[Tuple[float, float]]
        """

        scale_factor = self.compute_display_scale_factor(self.canvas_decimated_image)
        return [(coord[0]*scale_factor, coord[1]*scale_factor) for coord in decimated_image_yx_cords]

    def display_image_coords_to_decimated_image_coords(self, display_image_yx_coords):
        """
        Convert from display coordinates to decimated image coordinates.

        Parameters
        ----------
        display_image_yx_coords : List[Tuple[float, float]]

        Returns
        -------
        List[Tuple[float, float]]
        """

        scale_factor = self.compute_display_scale_factor(self.canvas_decimated_image)
        return [(coord[0]/scale_factor, coord[1]/scale_factor) for coord in display_image_yx_coords]

    @staticmethod
    def display_image_coords_to_canvas_coords(display_image_yx_coords):
        """
        Converts display image coordinates to canvas coordinates. This is just a
        axis switch operation.

        Parameters
        ----------
        display_image_yx_coords : List[Tuple[float, float]]

        Returns
        -------
        List[Tuple[float, float]]
        """

        return [(yx[1], yx[0]) for yx in display_image_yx_coords]

    def compute_display_scale_factor(self, decimated_image):
        """
        Computes the nominal scale factor.

        Parameters
        ----------
        decimated_image : numpy.ndarray

        Returns
        -------
        float
        """

        # TODO: division may not work as expected in Python 2 (int versus float)
        #   what is the intent here?
        decimated_image_nx = decimated_image.shape[1]
        decimated_image_ny = decimated_image.shape[0]
        scale_factor_1 = self.canvas_nx/decimated_image_nx
        scale_factor_2 = self.canvas_ny/decimated_image_ny
        scale_factor = min(scale_factor_1, scale_factor_2)
        return scale_factor

    def get_decimated_image_data_in_canvas_rect(self, canvas_rect, decimation=None):
        """
        Gets the decimated image from the image rectangle.

        Parameters
        ----------
        canvas_rect : Tuple|List
        decimation : None|int

        Returns
        -------
        numpy.ndarray
        """

        full_image_rect = self.canvas_rect_to_full_image_rect(canvas_rect)
        if decimation is None:
            decimation = self.get_decimation_from_canvas_rect(canvas_rect)
        return self.get_decimated_image_data_in_full_image_rect(full_image_rect, decimation)

    def update_canvas_display_image_from_full_image(self):
        """
        Update the image in the canvas.

        Returns
        -------
        None
        """

        full_image_rect = (0, 0, self.image_reader.full_image_ny, self.image_reader.full_image_nx)
        self.update_canvas_display_image_from_full_image_rect(full_image_rect)

    def update_canvas_display_image_from_full_image_rect(self, full_image_rect):
        """
        Update the canvas to the given image rectangle.

        Parameters
        ----------
        full_image_rect : Tuple|List

        Returns
        -------
        None
        """

        self.set_decimation_from_full_image_rect(full_image_rect)
        decimated_image_data = self.get_decimated_image_data_in_full_image_rect(full_image_rect, self.decimation_factor)
        self.update_canvas_display_from_numpy_array(decimated_image_data)
        self.canvas_full_image_upper_left_yx = (full_image_rect[0], full_image_rect[1])

    def update_canvas_display_image_from_canvas_rect(self, canvas_rect):
        """
        Update the canvas to the given camvas rectangle.

        Parameters
        ----------
        canvas_rect : Tuple|List

        Returns
        -------
        None
        """

        full_image_rect = self.canvas_rect_to_full_image_rect(canvas_rect)
        full_image_rect = (int(round(full_image_rect[0])),
                           int(round(full_image_rect[1])),
                           int(round(full_image_rect[2])),
                           int(round(full_image_rect[3])))
        self.update_canvas_display_image_from_full_image_rect(full_image_rect)

    def update_canvas_display_from_numpy_array(self, image_data):
        """
        Update the canvas from a numpy array.

        Parameters
        ----------
        image_data : numpy.ndarray

        Returns
        -------
        None
        """

        if len(self.drop_bands) > 0:
            zeros_image = numpy.zeros_like(image_data[:, :, 0])
            for drop_band in self.drop_bands:
                image_data[:, :, drop_band] = zeros_image
        self.canvas_decimated_image = image_data
        if self.scale_to_fit_canvas:
            scale_factor = self.compute_display_scale_factor(image_data)
            self.display_rescaling_factor = scale_factor
            self.display_image = self.get_scaled_display_data(image_data)
        else:
            self.display_image = image_data

    def get_decimation_factor_from_full_image_rect(self, full_image_rect):
        """
        Get the decimation factor from the rectangle size.

        Parameters
        ----------
        full_image_rect : Tuple|List

        Returns
        -------
        int
        """

        ny = full_image_rect[2] - full_image_rect[0]
        nx = full_image_rect[3] - full_image_rect[1]
        decimation_y = ny / self.canvas_ny
        decimation_x = nx / self.canvas_nx
        decimation_factor = max(decimation_y, decimation_x)
        decimation_factor = int(decimation_factor)
        if decimation_factor < 1:
            decimation_factor = 1
        return decimation_factor

    def get_decimation_from_canvas_rect(self, canvas_rect):
        """
        Get the decimation factor from the canvas rectangle size.

        Parameters
        ----------
        canvas_rect : Tuple|List

        Returns
        -------
        int
        """

        full_image_rect = self.canvas_rect_to_full_image_rect(canvas_rect)
        return self.get_decimation_factor_from_full_image_rect(full_image_rect)

    def set_decimation_from_full_image_rect(self, full_image_rect):
        """
        Sets the decimation from the image rectangle.

        Parameters
        ----------
        full_image_rect : Tuple|List

        Returns
        -------
        None
        """

        decimation_factor = self.get_decimation_factor_from_full_image_rect(full_image_rect)
        self.decimation_factor = decimation_factor

    def canvas_coords_to_full_image_yx(self, canvas_coords):
        """
        Gets full coordinates in yx order from canvas coordinates.

        Parameters
        ----------
        canvas_coords : Tuple|List

        Returns
        -------
        List
        """

        decimation_factor = self.decimation_factor
        if self.scale_to_fit_canvas:
            decimation_factor = decimation_factor/self.display_rescaling_factor
        siz = int(len(canvas_coords)/2)
        out = []
        for i in range(siz):
            out.extend(
                (canvas_coords[2*i+1]*decimation_factor + self.canvas_full_image_upper_left_yx[0],
                 canvas_coords[2 * i] * decimation_factor + self.canvas_full_image_upper_left_yx[1]))
        return out

    def canvas_rect_to_full_image_rect(self, canvas_rect):
        """
        Gets the full image coordinates from the canvas coordinates.

        Parameters
        ----------
        canvas_rect : Tuple|List

        Returns
        -------
        Tuple
        """

        image_y1, image_x1 = self.canvas_coords_to_full_image_yx([canvas_rect[0], canvas_rect[1]])
        image_y2, image_x2 = self.canvas_coords_to_full_image_yx([canvas_rect[2], canvas_rect[3]])

        if image_x1 < 0:
            image_x1 = 0
        if image_y1 < 0:
            image_y1 = 0
        if image_x2 > self.image_reader.full_image_nx:
            image_x2 = self.image_reader.full_image_nx
        if image_y2 > self.image_reader.full_image_ny:
            image_y2 = self.image_reader.full_image_ny

        return image_y1, image_x1, image_y2, image_x2

    def full_image_yx_to_canvas_coords(self, full_image_yx):
        """
        Gets the canvas coordinates from full image coordinates in yx order.

        Parameters
        ----------
        full_image_yx : Tuple|List

        Returns
        -------
        List
        """

        decimation_factor = self.decimation_factor
        if self.scale_to_fit_canvas:
            decimation_factor = decimation_factor / self.display_rescaling_factor

        siz = int(len(full_image_yx)/2)
        out = []
        for i in range(siz):
            out.extend(
                (float(full_image_yx[2*i+1] - self.canvas_full_image_upper_left_yx[1]) / decimation_factor,
                 float(full_image_yx[2 * i] - self.canvas_full_image_upper_left_yx[0]) / decimation_factor))
        return out


class VectorObject(object):
    def __init__(self, vector_type,
                 tkinter_options,
                 image_drag_limits=None):
        self.type = vector_type
        self.tkinter_options = tkinter_options
        self.image_coords = None
        self.point_size = None
        self.image_drag_limits = image_drag_limits
        if vector_type == SHAPE_TYPES.RECT or vector_type == SHAPE_TYPES.POLYGON:
            self.color = tkinter_options['outline']
        elif vector_type == SHAPE_TYPES.LINE or vector_type == SHAPE_TYPES.ARROW:
            self.color = tkinter_options['fill']


class AppVariables(object):
    """
    The canvas image application variables.
    """

    canvas_height = IntegerDescriptor(
        'canvas_height', default_value=200,
        docstring='The default canvas height, in pixels.')  # type: int
    canvas_width = IntegerDescriptor(
        'canvas_width', default_value=300,
        docstring='The default canvas width, in pixels.')  # type: int
    rect_border_width = IntegerDescriptor(
        'rect_border_width', default_value=2,
        docstring='The (margin) rectangular border width, in pixels.')  # type: int
    line_width = IntegerDescriptor(
        'line_width', default_value=2,
        docstring='The line width, in pixels.')  # type: int
    point_size = IntegerDescriptor(
        'point_size', default_value=3,
        docstring='The point size, in pixels.')  # type: int
    poly_border_width = IntegerDescriptor(
        'poly_border_width', default_value=2,
        docstring='The polygon border width, in pixels.')  # type: int
    poly_fill = StringDescriptor(
        'poly_fill',
        docstring='The polygon fill color(named or hexidecimal string).')  # type: Union[None, str]
    foreground_color = StringDescriptor(
        'foreground_color', default_value='red',
        docstring='The foreground color (named or hexidecimal string).')  # type: str
    image_id = IntegerDescriptor(
        'image_id',
        docstring='The image id.')  # type: int
    current_shape_id = IntegerDescriptor(
        'current_shape_id',
        docstring='The current shape id.')  # type: int
    current_shape_canvas_anchor_point_xy = IntegerTupleDescriptor(
        'current_shape_canvas_anchor_point_xy', length=2,
        docstring='The current shape canvas anchor point, in xy order.')  # type: Union[None, tuple]
    pan_anchor_point_xy = IntegerTupleDescriptor(
        'pan_anchor_point_xy', length=2, default_value=(0, 0),
        docstring='The pan anchor point, in xy order.')  # type: Union[None, tuple]
    canvas_image_object = TypedDescriptor(
        'canvas_image_object', CanvasImage,
        docstring='The canvas image object.')  # type: CanvasImage
    _tk_im = TypedDescriptor(
        '_tk_im', ImageTk.PhotoImage,
        docstring='The Tkinter Image.')  # type: ImageTk.PhotoImage
    # zoom rectangle properties
    zoom_rect_id = IntegerDescriptor(
        'zoom_rect_id',
        docstring='The zoom rectangle id.')  # type: int
    zoom_rect_color = StringDescriptor(
        'zoom_rect_color', default_value='cyan',
        docstring='The zoom rectangle color (named or hexidecimal).')  # type: str
    zoom_rect_border_width = IntegerDescriptor(
        'zoom_rect_border_width', default_value=2,
        docstring='The zoom rectangle border width, in pixels.')  # type: int
    # selection rectangle properties
    select_rect_id = IntegerDescriptor(
        'select_rect_id',
        docstring='The select rectangle id.')  # type: int
    select_rect_color = StringDescriptor(
        'select_rect_color', default_value='red',
        docstring='The select rectangle color (named or hexidecimal).')  # type: str
    select_rect_border_width = IntegerDescriptor(
        'select_rect_border_width', default_value=2,
        docstring='The select rectangle border width, in pixels.')  # type: int
    # animation properties
    animate_zoom = BooleanDescriptor(
        'animate_zoom', default_value=True,
        docstring='Specifies whether to animate zooming.')  # type: bool
    n_zoom_animations = IntegerDescriptor(
        'n_zoom_animations', default_value=5,
        docstring='The number of zoom frames.')  # type: int
    animate_pan = BooleanDescriptor(
        'animate_pan', default_value=False,
        docstring='Specifies whether to animate panning.')  # type: bool
    animation_time_in_seconds = FloatDescriptor(
        'animation_time_in_seconds', default_value=0.3,
        docstring='The animation time in seconds.')  # type: float
    # tool identifiers
    active_tool = StringDescriptor(
        'active_tool',
        docstring='The active tool name.')  # type: str
    current_tool = StringDescriptor(
        'current_tool',
        docstring='The current tool name.')  # type: str
    # some configuration properties
    vertex_selector_pixel_threshold = FloatDescriptor(
        'vertex_selector_pixel_threshold', default_value=10.0,
        docstring='The pixel threshold for vertex selection.')  # type: float
    mouse_wheel_zoom_percent_per_event = FloatDescriptor(
        'mouse_wheel_zoom_percent_per_event', default_value=1.5,
        docstring='The percent to zoom in/out on mouse wheel detection.')  # type: float
    highlight_n_colors_cycle = IntegerDescriptor(
        'highlight_n_colors_cycle', default_value=10,
        docstring='The length of highlight colors cycle.')  # type: int
    zoom_on_wheel = BooleanDescriptor(
        'zoom_on_wheel', default_value=True,
        docstring='Zoom on the mouse wheel operation?')  # type: bool
    rescale_image_to_fit_canvas = BooleanDescriptor(
        'rescale_image_to_fit_canvas', default_value=True,
        docstring='Rescale the image to fit the canvas?')  # type: bool
    scale_dynamic_range = BooleanDescriptor(
        'scale_dynamic_range', default_value=False,
        docstring='Scale the dynamic range of the image?')  # type: bool
    # some state properties
    the_canvas_is_currently_zooming = BooleanDescriptor(
        'the_canvas_is_currently_zooming', default_value=False,
        docstring='Is the canvas object currently zooming?')  # type: bool
    actively_drawing_shape = BooleanDescriptor(
        'actively_drawing_shape', default_value=False,
        docstring='Is the canvas object actively drawing a shape?')  # type: bool
    tmp_closest_coord_index = IntegerDescriptor(
        'tmp_closest_coord_index', default_value=0,
        docstring='')  # type: int

    def __init__(self):

        self.shape_ids = []  # type: [int]
        self.vector_objects = {}  # type: {VectorObject}
        self.shape_properties = {}
        self.shape_drag_image_coord_limits = {}  # type: dict
        self.highlight_color_palette = SeabornHexPalettes.blues  # type: List[str]
        self.tmp_points = None  # type: [int]


class ToolConstants:
    ZOOM_IN_TOOL = "zoom in"
    ZOOM_OUT_TOOL = "zoom out"
    DRAW_RECT_BY_DRAGGING = "draw rect by dragging"
    DRAW_RECT_BY_CLICKING = "draw rect by clicking"
    DRAW_ELLIPSE_BY_DRAGGING = "draw ellipse by dragging"
    DRAW_LINE_BY_DRAGGING = "draw line by dragging"
    DRAW_LINE_BY_CLICKING = "draw line by clicking"
    DRAW_ARROW_BY_DRAGGING = "draw arrow by dragging"
    DRAW_ARROW_BY_CLICKING = "draw arrow by clicking"
    DRAW_POLYGON_BY_CLICKING = "draw polygon by clicking"
    DRAW_POINT_BY_CLICKING = "draw point by clicking"
    SELECT_TOOL = "select tool"
    SELECT_CLOSEST_SHAPE_TOOL = "select closest shape"
    PAN_TOOL = "pan tool"
    TRANSLATE_SHAPE_TOOL = "translate shape tool"
    EDIT_SHAPE_COORDS_TOOL = "edit shape coords tool"
    EDIT_SHAPE_TOOL = "edit shape tool"


class ShapePropertyConstants:
    SHAPE_TYPE = "shape type"
    CANVAS_COORDS = "canvas coords"
    IMAGE_COORDS = "image coords"
    POINT_SIZE = "point size"
    COLOR = "color"


class ShapeTypeConstants:
    POINT = "point"
    LINE = "line"
    RECT = "rect"
    ELLIPSE = "ellipse"
    ARROW = "arrow"
    POLYGON = "polygon"
    TEXT = "text"


SHAPE_PROPERTIES = ShapePropertyConstants()
SHAPE_TYPES = ShapeTypeConstants()
TOOLS = ToolConstants()


class ImageCanvas(basic_widgets.Canvas):
    def __init__(self, primary):
        """

        Parameters
        ----------
        primary
            The primary widget.
        """
        osplat = platform.system()
        if osplat == "Windows":
            import ctypes
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()

        basic_widgets.Canvas.__init__(self, primary, highlightthickness=0)
        self.pack(fill=tkinter.BOTH, expand=tkinter.NO)

        self.variables = AppVariables()

        self.variables.zoom_rect_id = self.create_new_rect((0, 0, 1, 1), outline=self.variables.zoom_rect_color, width=self.variables.zoom_rect_border_width)
        self.variables.select_rect_id = self.create_new_rect((0, 0, 1, 1), outline=self.variables.select_rect_color, width=self.variables.select_rect_border_width)

        # hide the shapes we initialize
        self.hide_shape(self.variables.select_rect_id)
        self.hide_shape(self.variables.zoom_rect_id)

        self.on_left_mouse_click(self.callback_handle_left_mouse_click)
        self.on_left_mouse_motion(self.callback_handle_left_mouse_motion)
        self.on_left_mouse_release(self.callback_handle_left_mouse_release)
        self.on_right_mouse_click(self.callback_handle_right_mouse_click)
        self.on_mouse_motion(self.callback_handle_mouse_motion)

        self.on_mouse_wheel(self.callback_mouse_zoom)

        self.variables.active_tool = None
        self.variables.current_shape_id = None

    def _set_image_reader(self, image_reader):
        """
        Set the image reader.

        Parameters
        ----------
        image_reader : ImageReader

        Returns
        -------
        None
        """

        self.variables.canvas_image_object = CanvasImage(
            image_reader, self.variables.canvas_width, self.variables.canvas_height)
        if self.variables.rescale_image_to_fit_canvas:
            self.set_image_from_numpy_array(self.variables.canvas_image_object.display_image)
        else:
            self.set_image_from_numpy_array(self.variables.canvas_image_object.canvas_decimated_image)

    def get_vector_object(self, vector_id):
        """

        Parameters
        ----------
        vector_id : int

        Returns
        -------
        VectorObject
        """
        return self.variables.vector_objects[str(vector_id)]

    def get_canvas_line_length(self, line_id):
        """
        Gets the canvas line length.

        Parameters
        ----------
        line_id : int

        Returns
        -------
        int
        """

        line_coords = self.coords(line_id)
        x1 = line_coords[0]
        y1 = line_coords[1]
        x2 = line_coords[2]
        y2 = line_coords[3]
        length = numpy.sqrt(numpy.square(x2-x1) + numpy.square(y2-y1))
        return length

    def get_image_line_length(self, line_id):
        """
        Gest the image line length.

        Parameters
        ----------
        line_id : int

        Returns
        -------
        int
        """

        canvas_line_length = self.get_canvas_line_length(line_id)
        return canvas_line_length * self.variables.canvas_image_object.decimation_factor

    def hide_shape(self, shape_id):
        """
        Hide the shape specified by the provided id.

        Parameters
        ----------
        shape_id : int

        Returns
        -------
        None
        """

        if shape_id:
            self.itemconfigure(shape_id, state="hidden")

    def show_shape(self, shape_id):
        """
        Show or un-hide the shape specified by the provided id.

        Parameters
        ----------
        shape_id : int

        Returns
        -------
        None
        """

        if shape_id:
            self.itemconfigure(shape_id, state="normal")

    def callback_mouse_zoom(self, event):
        """
        The mouse zoom callback.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        if self.variables.zoom_on_wheel:
            delta = event.delta
            single_delta = 120

            # handle case where platform is linux:
            if platform.system() == "Linux":
                delta = single_delta
                if event.num == 5:
                    delta = delta*-1

            zoom_in_box_half_width = int(self.variables.canvas_width / self.variables.mouse_wheel_zoom_percent_per_event / 2)
            zoom_out_box_half_width = int(self.variables.canvas_width * self.variables.mouse_wheel_zoom_percent_per_event / 2)
            zoom_in_box_half_height = int(self.variables.canvas_height / self.variables.mouse_wheel_zoom_percent_per_event / 2)
            zoom_out_box_half_height = int(self.variables.canvas_height * self.variables.mouse_wheel_zoom_percent_per_event / 2)

            x = event.x
            y = event.y

            after_zoom_x_offset = (self.variables.canvas_width/2 - x)/self.variables.mouse_wheel_zoom_percent_per_event
            after_zoom_y_offset = (self.variables.canvas_height/2 - y)/self.variables.mouse_wheel_zoom_percent_per_event

            x_offset_point = x + after_zoom_x_offset
            y_offset_point = y + after_zoom_y_offset

            zoom_in_box = (x_offset_point - zoom_in_box_half_width,
                           y_offset_point - zoom_in_box_half_height,
                           x_offset_point + zoom_in_box_half_width,
                           y_offset_point + zoom_in_box_half_height)

            zoom_out_box = (x_offset_point - zoom_out_box_half_width,
                            y_offset_point - zoom_out_box_half_height,
                            x_offset_point + zoom_out_box_half_width,
                            y_offset_point + zoom_out_box_half_height)

            if self.variables.the_canvas_is_currently_zooming:
                pass
            else:
                if delta > 0:
                    self.zoom_to_selection(zoom_in_box, self.variables.animate_zoom)
                else:
                    self.zoom_to_selection(zoom_out_box, self.variables.animate_zoom)
        else:
            pass

    def animate_with_numpy_frame_sequence(self, numpy_frame_sequence, frames_per_second=15):
        """
        Animate with a sequence of numpy arrays.

        Parameters
        ----------
        numpy_frame_sequence : List[numpy.ndarray]
        frames_per_second : float

        Returns
        -------
        None
        """

        sleep_time = 1/frames_per_second
        for animation_frame in numpy_frame_sequence:
            tic = time.time()
            self.set_image_from_numpy_array(animation_frame)
            self.update()
            toc = time.time()
            frame_generation_time = toc-tic
            if frame_generation_time < sleep_time:
                new_sleep_time = sleep_time - frame_generation_time
                time.sleep(new_sleep_time)
            else:
                pass

    def animate_with_pil_frame_sequence(self, pil_frame_sequence, frames_per_second=15):
        """
        Animate with a sequence of PIL images.

        Parameters
        ----------
        pil_frame_sequence : List[PIL.Image]
        frames_per_second : float

        Returns
        -------
        None
        """

        sleep_time = 1/frames_per_second
        for animation_frame in pil_frame_sequence:
            tic = time.time()
            self._set_image_from_pil_image(animation_frame)
            self.update()
            toc = time.time()
            frame_generation_time = toc-tic
            if frame_generation_time < sleep_time:
                new_sleep_time = sleep_time - frame_generation_time
                time.sleep(new_sleep_time)
            else:
                pass

    def callback_handle_left_mouse_click(self, event):
        """
        Left mouse click callback.

        Parameters
        ----------
        event

        Returns
        -------

        """

        if self.variables.active_tool == TOOLS.PAN_TOOL:
            self.variables.pan_anchor_point_xy = event.x, event.y
            self.variables.tmp_anchor_point = event.x, event.y
        elif self.variables.active_tool == TOOLS.TRANSLATE_SHAPE_TOOL:
            self.variables.tmp_anchor_point = event.x, event.y
        elif self.variables.active_tool == TOOLS.EDIT_SHAPE_COORDS_TOOL:
            closest_coord_index = self.find_closest_shape_coord(self.variables.current_shape_id, event.x, event.y)
            self.variables.tmp_closest_coord_index = closest_coord_index
        elif self.variables.active_tool == TOOLS.SELECT_CLOSEST_SHAPE_TOOL:
            closest_shape_id = self.find_closest_shape(event.x, event.y)
            self.variables.current_shape_id = closest_shape_id
            self.highlight_existing_shape(self.variables.current_shape_id)
        else:
            start_x = self.canvasx(event.x)
            start_y = self.canvasy(event.y)

            self.variables.current_shape_canvas_anchor_point_xy = (start_x, start_y)
            if self.variables.current_shape_id not in self.variables.shape_ids:
                coords = (start_x, start_y, start_x + 1, start_y + 1)
                if self.variables.active_tool == TOOLS.DRAW_LINE_BY_DRAGGING:
                    self.create_new_line(coords)
                elif self.variables.active_tool == TOOLS.DRAW_LINE_BY_CLICKING:
                    self.create_new_line(coords)
                    self.variables.actively_drawing_shape = True
                elif self.variables.active_tool == TOOLS.DRAW_ARROW_BY_DRAGGING:
                    self.create_new_arrow(coords)
                elif self.variables.active_tool == TOOLS.DRAW_ARROW_BY_CLICKING:
                    self.create_new_arrow(coords)
                    self.variables.actively_drawing_shape = True
                elif self.variables.active_tool == TOOLS.DRAW_RECT_BY_DRAGGING:
                    self.create_new_rect(coords)
                elif self.variables.active_tool == TOOLS.DRAW_RECT_BY_CLICKING:
                    self.create_new_rect(coords)
                    self.variables.actively_drawing_shape = True
                elif self.variables.active_tool == TOOLS.DRAW_ELLIPSE_BY_DRAGGING:
                    self.create_new_ellipse(coords)
                elif self.variables.active_tool == TOOLS.DRAW_POINT_BY_CLICKING:
                    self.create_new_point((start_x, start_y))
                elif self.variables.active_tool == TOOLS.DRAW_POLYGON_BY_CLICKING:
                    self.create_new_polygon(coords)
                    self.variables.actively_drawing_shape = True
                else:
                    print("no tool selected")
            else:
                if self.variables.current_shape_id in self.variables.shape_ids:
                    vector_object = self.get_vector_object(self.variables.current_shape_id)
                    if vector_object.type == SHAPE_TYPES.POINT:
                        self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id,
                                                                       (start_x, start_y))
                    elif self.variables.active_tool == TOOLS.DRAW_LINE_BY_CLICKING:
                        self.event_click_line(event)
                    elif self.variables.active_tool == TOOLS.DRAW_ARROW_BY_CLICKING:
                        self.event_click_line(event)
                    elif self.variables.active_tool == TOOLS.DRAW_POLYGON_BY_CLICKING:
                        self.event_click_polygon(event)
                    elif self.variables.active_tool == TOOLS.DRAW_RECT_BY_CLICKING:
                        if self.variables.actively_drawing_shape:
                            self.variables.actively_drawing_shape = False
                        else:
                            self.variables.actively_drawing_shape = True

    def callback_handle_left_mouse_release(self, event):
        """
        Left mouse release callback.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        if self.variables.active_tool == TOOLS.PAN_TOOL:
            self._pan(event)
        if self.variables.active_tool == TOOLS.ZOOM_IN_TOOL:
            rect_coords = self.coords(self.variables.zoom_rect_id)
            self.zoom_to_selection(rect_coords, self.variables.animate_zoom)
            self.hide_shape(self.variables.zoom_rect_id)
        if self.variables.active_tool == TOOLS.ZOOM_OUT_TOOL:
            rect_coords = self.coords(self.variables.zoom_rect_id)
            x1 = -rect_coords[0]
            x2 = self.variables.canvas_width + rect_coords[2]
            y1 = -rect_coords[1]
            y2 = self.variables.canvas_height + rect_coords[3]
            zoom_rect = (x1, y1, x2, y2)
            self.zoom_to_selection(zoom_rect, self.variables.animate_zoom)
            self.hide_shape(self.variables.zoom_rect_id)

    def callback_handle_mouse_motion(self, event):
        """
        Mouse motion callback.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        if self.variables.actively_drawing_shape:
            if self.variables.active_tool == TOOLS.DRAW_LINE_BY_CLICKING:
                self.event_drag_multipoint_line(event)
            elif self.variables.active_tool == TOOLS.DRAW_ARROW_BY_CLICKING:
                self.event_drag_multipoint_line(event)
            elif self.variables.active_tool == TOOLS.DRAW_POLYGON_BY_CLICKING:
                self.event_drag_multipoint_polygon(event)
            elif self.variables.active_tool == TOOLS.DRAW_RECT_BY_CLICKING:
                self.event_drag_line(event)
        elif self.variables.current_tool == TOOLS.EDIT_SHAPE_TOOL:
            vector_object = self.get_vector_object(self.variables.current_shape_id)
            if vector_object.type == SHAPE_TYPES.RECT or vector_object.type == SHAPE_TYPES.ELLIPSE:
                select_x1, select_y1, select_x2, select_y2 = self.get_shape_canvas_coords(
                    self.variables.current_shape_id)
                select_xul = min(select_x1, select_x2)
                select_xlr = max(select_x1, select_x2)
                select_yul = min(select_y1, select_y2)
                select_ylr = max(select_y1, select_y2)

                distance_to_ul = numpy.sqrt(numpy.square(event.x - select_xul) + numpy.square(event.y - select_yul))
                distance_to_ur = numpy.sqrt(numpy.square(event.x - select_xlr) + numpy.square(event.y - select_yul))
                distance_to_lr = numpy.sqrt(numpy.square(event.x - select_xlr) + numpy.square(event.y - select_ylr))
                distance_to_ll = numpy.sqrt(numpy.square(event.x - select_xul) + numpy.square(event.y - select_ylr))

                if distance_to_ul < self.variables.vertex_selector_pixel_threshold:
                    self.config(cursor="top_left_corner")
                    self.variables.active_tool = TOOLS.EDIT_SHAPE_COORDS_TOOL
                elif distance_to_ur < self.variables.vertex_selector_pixel_threshold:
                    self.config(cursor="top_right_corner")
                    self.variables.active_tool = TOOLS.EDIT_SHAPE_COORDS_TOOL
                elif distance_to_lr < self.variables.vertex_selector_pixel_threshold:
                    self.config(cursor="bottom_right_corner")
                    self.variables.active_tool = TOOLS.EDIT_SHAPE_COORDS_TOOL
                elif distance_to_ll < self.variables.vertex_selector_pixel_threshold:
                    self.config(cursor="bottom_left_corner")
                    self.variables.active_tool = TOOLS.EDIT_SHAPE_COORDS_TOOL
                elif select_xul < event.x < select_xlr and select_yul < event.y < select_ylr:
                    self.config(cursor="fleur")
                    self.variables.active_tool = TOOLS.TRANSLATE_SHAPE_TOOL
                else:
                    self.config(cursor="arrow")
                    self.variables.active_tool = None
            elif vector_object.type == SHAPE_TYPES.LINE or vector_object.type == SHAPE_TYPES.ARROW:
                canvas_coords = self.get_shape_canvas_coords(self.variables.current_shape_id)
                x_coords = canvas_coords[0::2]
                y_coords = canvas_coords[1::2]
                distance_to_vertex = numpy.sqrt(numpy.square(event.x - x_coords[0]) +
                                                numpy.square(event.y - y_coords[0]))
                p2 = numpy.asarray((x_coords[1], y_coords[1]))
                p1 = numpy.asarray((x_coords[0], y_coords[0]))
                p3 = numpy.asarray((event.x, event.y))
                distance_to_line = norm(numpy.cross(p2 - p1, p1 - p3)) / norm(p2 - p1)
                for xy in zip(x_coords, y_coords):
                    vertex_distance = numpy.sqrt(numpy.square(event.x - xy[0]) + numpy.square(event.y - xy[1]))
                    if vertex_distance < distance_to_vertex:
                        distance_to_vertex = vertex_distance

                if distance_to_vertex < self.variables.vertex_selector_pixel_threshold:
                    self.config(cursor="target")
                    self.variables.active_tool = TOOLS.EDIT_SHAPE_COORDS_TOOL
                elif distance_to_line < self.variables.vertex_selector_pixel_threshold:
                    self.config(cursor="fleur")
                    self.variables.active_tool = TOOLS.TRANSLATE_SHAPE_TOOL
                else:
                    self.config(cursor="arrow")
                    self.variables.active_tool = None
            elif vector_object.type == SHAPE_TYPES.LINE or vector_object.type == SHAPE_TYPES.POLYGON:
                canvas_coords = self.get_shape_canvas_coords(self.variables.current_shape_id)
                x_coords = canvas_coords[0::2]
                y_coords = canvas_coords[1::2]
                xy_points = [xy for xy in zip(x_coords, y_coords)]
                distance_to_vertex = numpy.sqrt(numpy.square(event.x - x_coords[0]) +
                                                numpy.square(event.y - y_coords[0]))
                for xy in zip(x_coords, y_coords):
                    vertex_distance = numpy.sqrt(numpy.square(event.x - xy[0]) + numpy.square(event.y - xy[1]))
                    if vertex_distance < distance_to_vertex:
                        distance_to_vertex = vertex_distance

                if distance_to_vertex < self.variables.vertex_selector_pixel_threshold:
                    self.config(cursor="target")
                    self.variables.active_tool = TOOLS.EDIT_SHAPE_COORDS_TOOL
                elif polygon_utils.point_inside_polygon(event.x, event.y, xy_points):
                    self.config(cursor="fleur")
                    self.variables.active_tool = TOOLS.TRANSLATE_SHAPE_TOOL
                else:
                    self.config(cursor="arrow")
                    self.variables.active_tool = None
            elif vector_object.type == SHAPE_TYPES.POINT:
                canvas_coords = self.get_shape_canvas_coords(self.variables.current_shape_id)
                distance_to_point = numpy.sqrt(numpy.square(event.x - canvas_coords[0]) +
                                               numpy.square(event.y - canvas_coords[1]))
                if distance_to_point < self.variables.vertex_selector_pixel_threshold:
                    self.config(cursor="fleur")
                    self.variables.active_tool = TOOLS.TRANSLATE_SHAPE_TOOL

    def callback_handle_left_mouse_motion(self, event):
        """
        Left mouse motion callback.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        # TODO: update this for the case where there is no current shape id
        vector_object = self.get_vector_object(self.variables.current_shape_id)
        if self.variables.active_tool == TOOLS.PAN_TOOL:
            x_dist = event.x - self.variables.tmp_anchor_point[0]
            y_dist = event.y - self.variables.tmp_anchor_point[1]
            self.move(self.variables.image_id, x_dist, y_dist)
            self.variables.tmp_anchor_point = event.x, event.y
        elif self.variables.active_tool == TOOLS.TRANSLATE_SHAPE_TOOL:
            x_dist = event.x - self.variables.tmp_anchor_point[0]
            y_dist = event.y - self.variables.tmp_anchor_point[1]
            t_coords = self.get_shape_canvas_coords(self.variables.current_shape_id)
            new_coords = numpy.asarray(t_coords) + x_dist
            new_coords_y = numpy.asarray(t_coords) + y_dist
            new_coords[1::2] = new_coords_y[1::2]
            if vector_object.image_drag_limits:
                canvas_limits = self.image_coords_to_canvas_coords(vector_object.image_drag_limits)
                x_vertices = new_coords[0::2]
                y_vertices = new_coords[1::2]
                within_x_limits = True
                within_y_limits = True
                for x_vertex in x_vertices:
                    if canvas_limits[2] < x_vertex or x_vertex < canvas_limits[0]:
                        within_x_limits = False
                for y_vertex in y_vertices:
                    if y_vertex < canvas_limits[1] or y_vertex > canvas_limits[3]:
                        within_y_limits = False
                if not within_x_limits:
                    new_coords[0::2] = t_coords[0::2]
                if not within_y_limits:
                    new_coords[1::2] = t_coords[1::2]
            self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id,
                                                           new_coords,
                                                           update_pixel_coords=True)
            self.variables.tmp_anchor_point = event.x, event.y
        elif self.variables.active_tool == TOOLS.EDIT_SHAPE_COORDS_TOOL:
            previous_coords = self.get_shape_canvas_coords(self.variables.current_shape_id)
            coord_x_index = self.variables.tmp_closest_coord_index*2
            coord_y_index = coord_x_index + 1
            new_coords = list(previous_coords)
            new_coords[coord_x_index] = event.x
            new_coords[coord_y_index] = event.y
            if vector_object.image_drag_limits:
                drag_x_lim_1, drag_y_lim_1, drag_x_lim_2, drag_y_lim_2 = \
                    self.image_coords_to_canvas_coords(vector_object.image_drag_limits)
                if new_coords[coord_x_index] < drag_x_lim_1:
                    new_coords[coord_x_index] = drag_x_lim_1
                if new_coords[coord_x_index] > drag_x_lim_2:
                    new_coords[coord_x_index] = drag_x_lim_2
                if new_coords[coord_y_index] < drag_y_lim_1:
                    new_coords[coord_y_index] = drag_y_lim_1
                if new_coords[coord_y_index] > drag_y_lim_2:
                    new_coords[coord_y_index] = drag_y_lim_2

            self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id, tuple(new_coords))
        elif self.variables.active_tool == TOOLS.ZOOM_IN_TOOL:
            self.event_drag_line(event)
        elif self.variables.active_tool == TOOLS.ZOOM_OUT_TOOL:
            self.event_drag_line(event)
        elif self.variables.active_tool == TOOLS.SELECT_TOOL:
            self.event_drag_line(event)
        elif self.variables.active_tool == TOOLS.DRAW_RECT_BY_DRAGGING:
            self.event_drag_line(event)
        elif self.variables.active_tool == TOOLS.DRAW_ELLIPSE_BY_DRAGGING:
            self.event_drag_line(event)
        elif self.variables.active_tool == TOOLS.DRAW_LINE_BY_DRAGGING:
            self.event_drag_line(event)
        elif self.variables.active_tool == TOOLS.DRAW_ARROW_BY_DRAGGING:
            self.event_drag_line(event)
        elif self.variables.active_tool == TOOLS.DRAW_POINT_BY_CLICKING:
            self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id, (event.x, event.y))

    def highlight_existing_shape(self, shape_id):
        """
        Highlights an existing shape, according to provided id.

        Parameters
        ----------
        shape_id : int

        Returns
        -------
        None
        """

        original_color = self.get_vector_object(shape_id).color
        colors = color_utils.get_full_hex_palette(self.variables.highlight_color_palette, self.variables.highlight_n_colors_cycle)
        for color in colors:
            self.change_shape_color(shape_id, color)
            time.sleep(0.001)
            self.update()
        colors.reverse()
        for color in colors:
            self.change_shape_color(shape_id, color)
            time.sleep(0.001)
            self.update()
        self.change_shape_color(shape_id, original_color)

    # noinspection PyUnusedLocal
    def callback_handle_right_mouse_click(self, event):
        """
        Callback for right mouse click.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        if self.variables.active_tool == TOOLS.DRAW_LINE_BY_CLICKING:
            self.variables.actively_drawing_shape = False
        elif self.variables.active_tool == TOOLS.DRAW_ARROW_BY_CLICKING:
            self.variables.actively_drawing_shape = False
        elif self.variables.active_tool == TOOLS.DRAW_POLYGON_BY_CLICKING:
            self.variables.actively_drawing_shape = False

    def set_image_from_numpy_array(self, numpy_data):
        """
        This is the default way to set and display image data.  All other methods
        to update images should ultimately call this.

        Parameters
        ----------
        numpy_data : numpy.ndarray

        Returns
        -------
        None
        """

        if self.variables.scale_dynamic_range:
            min_data = numpy.min(numpy_data)
            dynamic_range = numpy.max(numpy_data) - min_data
            numpy_data = numpy.asanyarray(
                255*(numpy_data - min_data)/dynamic_range, dtype=numpy.uint8)
        pil_image = PIL.Image.fromarray(numpy_data)
        self._set_image_from_pil_image(pil_image)

    def set_canvas_size(self, width_npix, height_npix):
        """
        Set the canvas size.

        Parameters
        ----------
        width_npix : int|float
        height_npix : int|float

        Returns
        -------
        None
        """

        self.variables.canvas_width = width_npix
        self.variables.canvas_height = height_npix
        if self.variables.canvas_image_object is not None:
            self.variables.canvas_image_object.canvas_nx = width_npix
            self.variables.canvas_image_object.canvas_ny = height_npix
        self.config(width=width_npix, height=height_npix)

    def modify_existing_shape_using_canvas_coords(self, shape_id, new_coords, update_pixel_coords=True):
        """
        Modify an existing shape.

        Parameters
        ----------
        shape_id : int
        new_coords : Tuple|List
        update_pixel_coords : bool

        Returns
        -------
        None
        """
        vector_object = self.get_vector_object(shape_id)
        if vector_object.type == SHAPE_TYPES.POINT:
            point_size = vector_object.point_size
            x1, y1 = (new_coords[0] - point_size), (new_coords[1] - point_size)
            x2, y2 = (new_coords[0] + point_size), (new_coords[1] + point_size)
            canvas_drawing_coords = (x1, y1, x2, y2)
        else:
            canvas_drawing_coords = tuple(new_coords)
        self.coords(shape_id, canvas_drawing_coords)
        if update_pixel_coords:
            self.set_shape_pixel_coords_from_canvas_coords(shape_id, new_coords)

    def modify_existing_shape_using_image_coords(self, shape_id, image_coords):
        """
        Modify an existing shape.

        Parameters
        ----------
        shape_id : int
        image_coords : Tuple|List

        Returns
        -------
        None
        """

        self.set_shape_pixel_coords(shape_id, image_coords)
        canvas_coords = self.image_coords_to_canvas_coords(image_coords)
        self.modify_existing_shape_using_canvas_coords(shape_id, canvas_coords, update_pixel_coords=False)

    def event_drag_multipoint_line(self, event):
        """
        Drag multipoint line callback.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        if self.variables.current_shape_id:
            self.show_shape(self.variables.current_shape_id)
            event_x_pos = self.canvasx(event.x)
            event_y_pos = self.canvasy(event.y)
            coords = self.coords(self.variables.current_shape_id)
            new_coords = list(coords[0:-2]) + [event_x_pos, event_y_pos]
            vector_object = self.get_vector_object(self.variables.current_shape_id)
            if vector_object.type == SHAPE_TYPES.ARROW or vector_object.type == SHAPE_TYPES.LINE:
                self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id, new_coords)
        else:
            pass

    def event_drag_multipoint_polygon(self, event):
        """
        Drag a polygon callback.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        if self.variables.current_shape_id:
            event_x_pos = self.canvasx(event.x)
            event_y_pos = self.canvasy(event.y)
            drag_lims = self.get_vector_object(self.variables.current_shape_id).image_drag_limits
            if drag_lims:
                canvas_lims = self.image_coords_to_canvas_coords(drag_lims)
                if event_x_pos < canvas_lims[0]:
                    event_x_pos = canvas_lims[0]
                elif event_x_pos > canvas_lims[2]:
                    event_x_pos = canvas_lims[2]
                if event_y_pos < canvas_lims[1]:
                    event_y_pos = canvas_lims[1]
                elif event_y_pos > canvas_lims[3]:
                    event_y_pos = canvas_lims[3]

            self.show_shape(self.variables.current_shape_id)
            coords = self.coords(self.variables.current_shape_id)
            new_coords = list(coords[0:-2]) + [event_x_pos, event_y_pos]
            self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id, new_coords)
        else:
            pass

    def event_drag_line(self, event):
        """
        Drag a line callback.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        if self.variables.current_shape_id:
            self.show_shape(self.variables.current_shape_id)
            event_x_pos = self.canvasx(event.x)
            event_y_pos = self.canvasy(event.y)
            if self.get_vector_object(self.variables.current_shape_id).image_drag_limits:
                drag_lims = self.get_vector_object(self.variables.current_shape_id).image_drag_limits
                canvas_lims = self.image_coords_to_canvas_coords(drag_lims)
                if event_x_pos < canvas_lims[0]:
                    event_x_pos = canvas_lims[0]
                elif event_x_pos > canvas_lims[2]:
                    event_x_pos = canvas_lims[2]
                if event_y_pos < canvas_lims[1]:
                    event_y_pos = canvas_lims[1]
                elif event_y_pos > canvas_lims[3]:
                    event_y_pos = canvas_lims[3]
            self.modify_existing_shape_using_canvas_coords(
                self.variables.current_shape_id,
                (self.variables.current_shape_canvas_anchor_point_xy[0],
                 self.variables.current_shape_canvas_anchor_point_xy[1],
                 event_x_pos, event_y_pos))

    def event_click_line(self, event):
        """
        Click a line callback.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """
        event_x_pos = self.canvasx(event.x)
        event_y_pos = self.canvasy(event.y)
        if self.get_vector_object(self.variables.current_shape_id).image_drag_limits:
            drag_lims = self.get_vector_object(self.variables.current_shape_id).image_drag_limits
            canvas_lims = self.image_coords_to_canvas_coords(drag_lims)
            if event_x_pos < canvas_lims[0]:
                event_x_pos = canvas_lims[0]
            elif event_x_pos > canvas_lims[2]:
                event_x_pos = canvas_lims[2]
            if event_y_pos < canvas_lims[1]:
                event_y_pos = canvas_lims[1]
            elif event_y_pos > canvas_lims[3]:
                event_y_pos = canvas_lims[3]
        if self.variables.actively_drawing_shape:
            old_coords = self.get_shape_canvas_coords(self.variables.current_shape_id)
            new_coords = tuple(list(old_coords) + [event_x_pos, event_y_pos])
            self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id, new_coords)
        else:
            new_coords = (event_x_pos, event_y_pos, event_x_pos + 1, event_y_pos + 1)
            self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id, new_coords)
            self.variables.actively_drawing_shape = True

    def delete_shape(self, shape_id):
        """
        Deletes a shape by its id.

        Parameters
        ----------
        shape_id : int

        Returns
        -------
        None
        """

        self.variables.shape_ids.remove(shape_id)
        del self.variables.vector_objects[str(shape_id)]
        self.delete(shape_id)
        if shape_id == self.variables.current_shape_id:
            self.variables.current_shape_id = None

    def event_click_polygon(self, event):
        """
        Click a polygon callback.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        event_x_pos = self.canvasx(event.x)
        event_y_pos = self.canvasy(event.y)
        drag_lims = self.get_vector_object(self.variables.current_shape_id).image_drag_limits
        if drag_lims:
            canvas_lims = self.image_coords_to_canvas_coords(drag_lims)
            if event_x_pos < canvas_lims[0]:
                event_x_pos = canvas_lims[0]
            elif event_x_pos > canvas_lims[2]:
                event_x_pos = canvas_lims[2]
            if event_y_pos < canvas_lims[1]:
                event_y_pos = canvas_lims[1]
            elif event_y_pos > canvas_lims[3]:
                event_y_pos = canvas_lims[3]

        if self.variables.actively_drawing_shape:
            old_coords = self.get_shape_canvas_coords(self.variables.current_shape_id)
            new_coords = list(old_coords) + [event_x_pos, event_y_pos]
            self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id, new_coords)
        # re-initialize shape if we're not actively drawing
        else:
            new_coords = (event.x, event.y, event_x_pos+1, event_y_pos+1)
            self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id, new_coords)
            self.variables.actively_drawing_shape = True

    def create_new_text(self, *args, **kw):
        """Create text with coordinates x1,y1."""
        shape_id = self._create('text', args, kw)
        self.variables.shape_ids.append(shape_id)
        canvas_coords = args[0]
        self.variables.vector_objects[str(shape_id)] = VectorObject(SHAPE_TYPES.TEXT, None)
        self.variables.shape_ids.append(shape_id)
        self.set_shape_pixel_coords_from_canvas_coords(shape_id, canvas_coords)
        self.variables.current_shape_id = shape_id
        return shape_id

    def create_new_rect(self, canvas_coords, **options):
        """
        Create a new rectangle.

        Parameters
        ----------
        canvas_coords : Tuple|List
        options
            Optional Keyword arguments.

        Returns
        -------
        int
        """

        if 'outline' not in options:
            options['outline'] = self.variables.foreground_color
        if 'width' not in options:
            options['width'] = self.variables.rect_border_width
        shape_id = self.create_rectangle(*canvas_coords, **options)
        self.variables.vector_objects[str(shape_id)] = VectorObject(SHAPE_TYPES.RECT, options)
        self.variables.shape_ids.append(shape_id)
        self.set_shape_pixel_coords_from_canvas_coords(shape_id, canvas_coords)
        self.variables.current_shape_id = shape_id
        return shape_id

    def create_new_ellipse(self, canvas_coords, **options):
        """
        Create a new rectangle.

        Parameters
        ----------
        canvas_coords : Tuple|List
        options
            Optional Keyword arguments.

        Returns
        -------
        int
        """

        if 'outline' not in options:
            options['outline'] = self.variables.foreground_color
        if 'width' not in options:
            options['width'] = self.variables.rect_border_width
        shape_id = self.create_oval(*canvas_coords, **options)
        self.variables.vector_objects[str(shape_id)] = VectorObject(SHAPE_TYPES.RECT, options)
        self.variables.shape_ids.append(shape_id)
        self.set_shape_pixel_coords_from_canvas_coords(shape_id, canvas_coords)
        self.variables.current_shape_id = shape_id
        return shape_id

    def create_new_polygon(self, coords, **options):
        """
        Create a new polygon.

        Parameters
        ----------
        coords : Tuple|List
        options
            Optional keyword arguments.

        Returns
        -------
        int
        """

        if 'outline' not in options:
            options['outline'] = self.variables.foreground_color
        if 'width' not in options:
            options['width'] = self.variables.poly_border_width
        if 'fill' not in options:
            options['fill'] = ''

        shape_id = self.create_polygon(*coords, **options)
        self.variables.vector_objects[str(shape_id)] = VectorObject(SHAPE_TYPES.POLYGON, options)
        self.variables.shape_ids.append(shape_id)
        self.set_shape_pixel_coords_from_canvas_coords(shape_id, coords)
        self.variables.current_shape_id = shape_id
        return shape_id

    def create_new_arrow(self, coords, **options):
        """
        Create a new arrow.

        Parameters
        ----------
        coords : Tuple|List
        options
            Optional keyword arguments.

        Returns
        -------
        int
        """

        if 'fill' not in options:
            options['fill'] = self.variables.foreground_color
        if 'width' not in options:
            options['width'] = self.variables.line_width
        if 'arrow' not in options:
            options['arrow'] = tkinter.LAST

        shape_id = self.create_line(*coords, **options)
        self.variables.vector_objects[str(shape_id)] = VectorObject(SHAPE_TYPES.ARROW, options)
        self.variables.shape_ids.append(shape_id)
        self.set_shape_pixel_coords_from_canvas_coords(shape_id, coords)
        self.variables.current_shape_id = shape_id
        return shape_id

    def create_new_line(self, coords, **options):
        """
        Create a new line.

        Parameters
        ----------
        coords : Tuple|List
        options
            Optional keyword arguments.

        Returns
        -------
        int
        """

        if 'fill' not in options:
            options['fill'] = self.variables.foreground_color
        if 'width' not in options:
            options['width'] = self.variables.line_width

        shape_id = self.create_line(*coords, **options)
        self.variables.vector_objects[str(shape_id)] = VectorObject(SHAPE_TYPES.LINE, options)
        self.variables.shape_ids.append(shape_id)
        self.set_shape_pixel_coords_from_canvas_coords(shape_id, coords)
        self.variables.current_shape_id = shape_id
        return shape_id

    def create_new_point(self, coords, **options):
        """
        Create a new point.

        Parameters
        ----------
        coords : Tuple|List
        options
            Optional keyword arguments.

        Returns
        -------
        int
        """

        if 'fill' not in options:
            options['fill'] = self.variables.foreground_color

        x1, y1 = (coords[0] - self.variables.point_size), (coords[1] - self.variables.point_size)
        x2, y2 = (coords[0] + self.variables.point_size), (coords[1] + self.variables.point_size)
        shape_id = self.create_oval(x1, y1, x2, y2, **options)
        self.variables.vector_objects[str(shape_id)] = VectorObject(SHAPE_TYPES.POINT, options)
        self.variables.vector_objects[str(shape_id)].point_size = self.variables.point_size
        self.variables.shape_ids.append(shape_id)
        self.set_shape_pixel_coords_from_canvas_coords(shape_id, coords)
        self.variables.current_shape_id = shape_id
        return shape_id

    def change_shape_color(self, shape_id, color):
        """
        Change the shape color.

        Parameters
        ----------
        shape_id : int
        color : str

        Returns
        -------
        None
        """
        vector_object = self.get_vector_object(shape_id)
        shape_type = vector_object.type
        if shape_type == SHAPE_TYPES.RECT or shape_type == SHAPE_TYPES.POLYGON:
            self.itemconfig(shape_id, outline=color)
            vector_object.tkinter_options['outline'] = color
        else:
            self.itemconfig(shape_id, fill=color)
            vector_object.tkinter_options['fill'] = color

    def set_shape_pixel_coords_from_canvas_coords(self, shape_id, coords):
        """
        Sets the shape pixel coordinates from the canvas coordinates.

        Parameters
        ----------
        shape_id : int

        Returns
        -------
        None
        """

        if self.variables.canvas_image_object:
            image_coords = self.canvas_coords_to_image_coords(coords)
            self.set_shape_pixel_coords(shape_id, image_coords)

    def set_shape_pixel_coords(self, shape_id, image_coords):
        """
        Set the pixel coordinates for the given shape.

        Parameters
        ----------
        shape_id : int
        image_coords : Tuple|List

        Returns
        -------
        None
        """

        vector_object = self.get_vector_object(shape_id)
        vector_object.image_coords = image_coords

    def canvas_coords_to_image_coords(self, canvas_coords):
        """
        Converts the canvas coordinates to image coordinates.

        Parameters
        ----------
        canvas_coords : tuple

        Returns
        -------
        tuple
        """

        return self.variables.canvas_image_object.canvas_coords_to_full_image_yx(canvas_coords)

    def get_shape_canvas_coords(self, shape_id):
        """
        Fetches the canvas coordinates for the shape.

        Parameters
        ----------
        shape_id : int

        Returns
        -------
        Tuple
        """

        return self.image_coords_to_canvas_coords(self.get_vector_object(shape_id).image_coords)

    def get_shape_image_coords(self, shape_id):
        """
        Fetches the image coordinates for the shape.

        Parameters
        ----------
        shape_id : int

        Returns
        -------
        Tuple
        """

        return self.get_vector_object(shape_id).image_coords

    def shape_image_coords_to_canvas_coords(self, shape_id):
        """
        Converts the image coordinates to the shapoe coordinates.

        Parameters
        ----------
        shape_id : int

        Returns
        -------
        Tuple
        """

        image_coords = self.get_shape_image_coords(shape_id)
        return self.variables.canvas_image_object.full_image_yx_to_canvas_coords(image_coords)

    def image_coords_to_canvas_coords(self, image_coords):
        """
        Converts the image coordinates to the shapoe coordinates.

        Parameters
        ----------
        image_coords : tuple

        Returns
        -------
        Tuple
        """

        return self.variables.canvas_image_object.full_image_yx_to_canvas_coords(image_coords)

    def get_image_data_in_canvas_rect_by_id(self, rect_id, decimation=None):
        """
        Fetches the image data.

        Parameters
        ----------
        rect_id : int
        decimation : None|int

        Returns
        -------
        numpy.ndarray
        """

        image_coords = self.get_shape_image_coords(rect_id)
        tmp_image_coords = list(image_coords)
        if image_coords[0] > image_coords[2]:
            tmp_image_coords[0] = image_coords[2]
            tmp_image_coords[2] = image_coords[0]
        if image_coords[1] > image_coords[3]:
            tmp_image_coords[1] = image_coords[3]
            tmp_image_coords[3] = image_coords[1]
        if decimation is None:
            decimation = self.variables.canvas_image_object.\
                get_decimation_factor_from_full_image_rect(tmp_image_coords)
        tmp_image_coords = (int(tmp_image_coords[0]), int(tmp_image_coords[1]), int(tmp_image_coords[2]), int(tmp_image_coords[3]))
        image_data_in_rect = self.variables.canvas_image_object.\
            get_decimated_image_data_in_full_image_rect(tmp_image_coords, decimation)
        return image_data_in_rect

    def zoom_to_selection(self, canvas_rect, animate=False):
        """
        Zoom to the selection using canvas coordinates.

        Parameters
        ----------
        canvas_rect : Tuple|List
        animate : bool

        Returns
        -------
        None
        """

        self.variables.the_canvas_is_currently_zooming = True
        # fill up empty canvas space due to inconsistent ratios between the canvas rect and the canvas dimensions
        image_coords = self.variables.canvas_image_object.canvas_coords_to_full_image_yx(canvas_rect)
        self.zoom_to_full_image_selection(image_coords, animate=animate)

    def zoom_to_full_image_selection(self, image_rect, animate=False):
        """
        Zoom to the selection using image coordinates.

        Parameters
        ----------
        image_rect_rect : Tuple|List
        animate : bool

        Returns
        -------
        None
        """
        zoomed_image_height = image_rect[2] - image_rect[0]
        zoomed_image_width = image_rect[3] - image_rect[1]

        canvas_height_width_ratio = self.variables.canvas_height / self.variables.canvas_width
        zoomed_image_height_width_ratio = zoomed_image_height / zoomed_image_width

        new_image_width = zoomed_image_height / canvas_height_width_ratio
        new_image_height = zoomed_image_width * canvas_height_width_ratio

        if zoomed_image_height_width_ratio > canvas_height_width_ratio:
            image_zoom_point_center = (image_rect[3] + image_rect[1]) / 2
            image_rect[1] = image_zoom_point_center - new_image_width / 2
            image_rect[3] = image_zoom_point_center + new_image_width / 2
        else:
            image_zoom_point_center = (image_rect[2] + image_rect[0]) / 2
            image_rect[0] = image_zoom_point_center - new_image_height / 2
            image_rect[2] = image_zoom_point_center + new_image_height / 2

        # keep the rect within the image bounds
        image_y_ul = max(image_rect[0], 0)
        image_x_ul = max(image_rect[1], 0)
        image_y_br = min(image_rect[2], self.variables.canvas_image_object.image_reader.full_image_ny)
        image_x_br = min(image_rect[3], self.variables.canvas_image_object.image_reader.full_image_nx)

        # re-adjust if we ran off one of the edges
        if image_x_ul == 0:
            image_rect[3] = new_image_width
        if image_x_br == self.variables.canvas_image_object.image_reader.full_image_nx:
            image_rect[1] = self.variables.canvas_image_object.image_reader.full_image_nx - new_image_width
        if image_y_ul == 0:
            image_rect[2] = new_image_height
        if image_y_br == self.variables.canvas_image_object.image_reader.full_image_ny:
            image_rect[0] = self.variables.canvas_image_object.image_reader.full_image_ny - new_image_height

        # keep the rect within the image bounds
        image_y_ul = max(image_rect[0], 0)
        image_x_ul = max(image_rect[1], 0)
        image_y_br = min(image_rect[2], self.variables.canvas_image_object.image_reader.full_image_ny)
        image_x_br = min(image_rect[3], self.variables.canvas_image_object.image_reader.full_image_nx)

        new_canvas_rect = self.variables.canvas_image_object.full_image_yx_to_canvas_coords(
            (image_y_ul, image_x_ul, image_y_br, image_x_br))
        new_canvas_rect = (
        int(new_canvas_rect[0]), int(new_canvas_rect[1]), int(new_canvas_rect[2]), int(new_canvas_rect[3]))

        background_image = self.variables.canvas_image_object.display_image
        self.variables.canvas_image_object.update_canvas_display_image_from_canvas_rect(new_canvas_rect)
        if self.variables.rescale_image_to_fit_canvas:
            new_image = PIL.Image.fromarray(self.variables.canvas_image_object.display_image)
        else:
            new_image = PIL.Image.fromarray(self.variables.canvas_image_object.canvas_decimated_image)
        if animate is True:
            # create frame sequence
            n_animations = self.variables.n_zoom_animations
            background_image = background_image / 2
            background_image = numpy.asarray(background_image, dtype=numpy.uint8)
            canvas_x1, canvas_y1, canvas_x2, canvas_y2 = new_canvas_rect
            display_x_ul = min(canvas_x1, canvas_x2)
            display_x_br = max(canvas_x1, canvas_x2)
            display_y_ul = min(canvas_y1, canvas_y2)
            display_y_br = max(canvas_y1, canvas_y2)
            x_diff = new_image.width - (display_x_br - display_x_ul)
            y_diff = new_image.height - (display_y_br - display_y_ul)
            pil_background_image = PIL.Image.fromarray(background_image)
            frame_sequence = []
            for i in range(n_animations):
                new_x_ul = int(display_x_ul * (1 - i / (n_animations - 1)))
                new_y_ul = int(display_y_ul * (1 - i / (n_animations - 1)))
                new_size_x = int((display_x_br - display_x_ul) + x_diff * (i / (n_animations - 1)))
                new_size_y = int((display_y_br - display_y_ul) + y_diff * (i / (n_animations - 1)))
                resized_zoom_image = new_image.resize((new_size_x, new_size_y))
                animation_image = pil_background_image.copy()
                animation_image.paste(resized_zoom_image, (new_x_ul, new_y_ul))
                frame_sequence.append(animation_image)
            fps = n_animations / self.variables.animation_time_in_seconds
            self.animate_with_pil_frame_sequence(frame_sequence, frames_per_second=fps)
        if self.variables.rescale_image_to_fit_canvas:
            self.set_image_from_numpy_array(self.variables.canvas_image_object.display_image)
        else:
            self.set_image_from_numpy_array(self.variables.canvas_image_object.canvas_decimated_image)
        self.update()
        self.redraw_all_shapes()
        self.variables.the_canvas_is_currently_zooming = False

    def update_current_image(self):
        """
        Updates the current image.

        Returns
        -------
        None
        """

        rect = (0, 0, self.variables.canvas_width, self.variables.canvas_height)
        if self.variables.canvas_image_object is not None:
            self.variables.canvas_image_object.update_canvas_display_image_from_canvas_rect(rect)
            self.set_image_from_numpy_array(self.variables.canvas_image_object.display_image)
            self.update()

    def redraw_all_shapes(self):
        """
        Redraw all the shapes.

        Returns
        -------
        None
        """

        for shape_id in self.variables.shape_ids:
            pixel_coords = self.get_vector_object(shape_id).image_coords
            if pixel_coords:
                new_canvas_coords = self.shape_image_coords_to_canvas_coords(shape_id)
                self.modify_existing_shape_using_canvas_coords(shape_id, new_canvas_coords, update_pixel_coords=False)

    def set_current_tool_to_select_closest_shape(self):
        """
        Sets the tool to the closest shape.

        Returns
        -------
        None
        """

        self.variables.active_tool = TOOLS.SELECT_CLOSEST_SHAPE_TOOL
        self.variables.current_tool = TOOLS.SELECT_CLOSEST_SHAPE_TOOL

    def set_current_tool_to_zoom_out(self):
        """
        Sets the current tool to zoom out.

        Returns
        -------
        None
        """

        self.variables.current_shape_id = self.variables.zoom_rect_id
        self.variables.active_tool = TOOLS.ZOOM_OUT_TOOL
        self.variables.current_tool = TOOLS.ZOOM_OUT_TOOL

    def set_current_tool_to_zoom_in(self):
        """
        Sets the current tool to zoom in.

        Returns
        -------
        None
        """

        self.variables.current_shape_id = self.variables.zoom_rect_id
        self.variables.active_tool = TOOLS.ZOOM_IN_TOOL
        self.variables.current_tool = TOOLS.ZOOM_IN_TOOL

    def set_current_tool_to_draw_rect(self, rect_id=None):
        """
        Sets the current tool to draw rectangle.

        Parameters
        ----------
        rect_id : int|None

        Returns
        -------
        None
        """

        self.variables.current_shape_id = rect_id
        self.show_shape(rect_id)
        self.variables.active_tool = TOOLS.DRAW_RECT_BY_DRAGGING
        self.variables.current_tool = TOOLS.DRAW_RECT_BY_DRAGGING

    def set_current_tool_to_draw_ellipse(self, ellipse_id=None):
        """
        Sets the current tool to draw rectangle.

        Parameters
        ----------
        rect_id : int|None

        Returns
        -------
        None
        """

        self.variables.current_shape_id = ellipse_id
        self.show_shape(ellipse_id)
        self.variables.active_tool = TOOLS.DRAW_ELLIPSE_BY_DRAGGING
        self.variables.current_tool = TOOLS.DRAW_ELLIPSE_BY_DRAGGING

    def set_current_tool_to_draw_rect_by_clicking(self, rect_id=None):
        """
        Sets the current tool to draw rectangle by clicking.

        Parameters
        ----------
        rect_id : None|int

        Returns
        -------
        None
        """

        self.variables.current_shape_id = rect_id
        self.show_shape(rect_id)
        self.variables.active_tool = TOOLS.DRAW_RECT_BY_CLICKING
        self.variables.current_tool = TOOLS.DRAW_RECT_BY_CLICKING

    def set_current_tool_to_selection_tool(self):
        """
        Sets the current tool to the selection tool.

        Returns
        -------
        None
        """

        self.variables.current_shape_id = self.variables.select_rect_id
        self.variables.active_tool = TOOLS.SELECT_TOOL
        self.variables.current_tool = TOOLS.SELECT_TOOL

    def set_current_tool_to_draw_line_by_dragging(self, line_id=None):
        """
        Sets the current tool to draw line by dragging.

        Parameters
        ----------
        line_id : None|int

        Returns
        -------
        None
        """

        self.variables.current_shape_id = line_id
        self.show_shape(line_id)
        self.variables.active_tool = TOOLS.DRAW_LINE_BY_DRAGGING
        self.variables.current_tool = TOOLS.DRAW_LINE_BY_DRAGGING

    def set_current_tool_to_draw_line_by_clicking(self, line_id=None):
        """
        Sets the current tool to draw line by clicking.

        Parameters
        ----------
        line_id : None|int

        Returns
        -------
        None
        """

        self.variables.current_shape_id = line_id
        self.show_shape(line_id)
        self.variables.active_tool = TOOLS.DRAW_LINE_BY_CLICKING
        self.variables.current_tool = TOOLS.DRAW_LINE_BY_CLICKING

    def set_current_tool_to_draw_arrow_by_dragging(self, arrow_id=None):
        """
        Sets the current tool to draw arrow by dragging.

        Parameters
        ----------
        arrow_id : None|int

        Returns
        -------
        None
        """

        self.variables.current_shape_id = arrow_id
        self.show_shape(arrow_id)
        self.variables.active_tool = TOOLS.DRAW_ARROW_BY_DRAGGING
        self.variables.current_tool = TOOLS.DRAW_ARROW_BY_DRAGGING

    def set_current_tool_to_draw_arrow_by_clicking(self, arrow_id=None):
        """
        Sets the current tool to draw arrow by clicking.

        Parameters
        ----------
        arrow_id : None|int

        Returns
        -------
        None
        """

        self.variables.current_shape_id = arrow_id
        self.show_shape(arrow_id)
        self.variables.active_tool = TOOLS.DRAW_ARROW_BY_CLICKING
        self.variables.current_tool = TOOLS.DRAW_ARROW_BY_CLICKING

    def set_current_tool_to_draw_polygon_by_clicking(self, polygon_id=None):
        """
        Sets the current tool to draw polygon by clicking.

        Parameters
        ----------
        polygon_id : None|int

        Returns
        -------
        None
        """

        self.variables.current_shape_id = polygon_id
        self.show_shape(polygon_id)
        self.variables.active_tool = TOOLS.DRAW_POLYGON_BY_CLICKING
        self.variables.current_tool = TOOLS.DRAW_POLYGON_BY_CLICKING

    def set_current_tool_to_draw_point(self, point_id=None):
        """
        Sets the current tool to draw point.

        Parameters
        ----------
        point_id : None|int

        Returns
        -------
        None
        """

        self.variables.current_shape_id = point_id
        self.show_shape(point_id)
        self.variables.active_tool = TOOLS.DRAW_POINT_BY_CLICKING
        self.variables.current_tool = TOOLS.DRAW_POINT_BY_CLICKING

    def set_current_tool_to_translate_shape(self):
        """
        Sets the current tool to translate shape.

        Returns
        -------
        None
        """

        self.variables.active_tool = TOOLS.TRANSLATE_SHAPE_TOOL
        self.variables.current_tool = TOOLS.TRANSLATE_SHAPE_TOOL

    def set_current_tool_to_none(self):
        """
        Sets the current tool to None.

        Returns
        -------
        None
        """

        self.variables.active_tool = None
        self.variables.current_tool = None

    def set_current_tool_to_edit_shape(self):
        """
        Sets the current tool to edit shape.

        Returns
        -------
        None
        """

        self.variables.active_tool = TOOLS.EDIT_SHAPE_TOOL
        self.variables.current_tool = TOOLS.EDIT_SHAPE_TOOL

    def set_current_tool_to_edit_shape_coords(self):
        """
        Sets the current tool to edit shape coordinates.

        Returns
        -------
        None
        """

        self.variables.active_tool = TOOLS.EDIT_SHAPE_COORDS_TOOL
        self.variables.current_tool = TOOLS.EDIT_SHAPE_COORDS_TOOL

    def set_current_tool_to_pan(self):
        """
        Sets the current tool to pan.

        Returns
        -------
        None
        """

        self.variables.active_tool = TOOLS.PAN_TOOL
        self.variables.current_tool = TOOLS.PAN_TOOL

    def _set_image_from_pil_image(self, pil_image):
        """
        Set image from a PIL image.

        Parameters
        ----------
        pil_image : PIL.Image

        Returns
        -------
        None
        """

        nx_pix, ny_pix = pil_image.size
        self.config(scrollregion=(0, 0, nx_pix, ny_pix))
        self.variables._tk_im = ImageTk.PhotoImage(pil_image)
        self.variables.image_id = self.create_image(0, 0, anchor="nw", image=self.variables._tk_im)
        self.tag_lower(self.variables.image_id)

    def _pan(self, event):
        """
        A pan event.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        new_canvas_x_ul = self.variables.pan_anchor_point_xy[0] - event.x
        new_canvas_y_ul = self.variables.pan_anchor_point_xy[1] - event.y
        new_canvas_x_br = new_canvas_x_ul + self.variables.canvas_width
        new_canvas_y_br = new_canvas_y_ul + self.variables.canvas_height
        canvas_coords = (new_canvas_x_ul, new_canvas_y_ul, new_canvas_x_br, new_canvas_y_br)
        image_coords = self.variables.canvas_image_object.canvas_coords_to_full_image_yx(canvas_coords)
        image_y_ul = image_coords[0]
        image_x_ul = image_coords[1]
        image_y_br = image_coords[2]
        image_x_br = image_coords[3]
        # TODO: fix this, it just snaps back to the original position if the x or y coords are less than zero
        if image_y_ul < 0:
            new_canvas_y_ul = 0
            new_canvas_y_br = self.variables.canvas_height
        if image_x_ul < 0:
            new_canvas_x_ul = 0
            new_canvas_x_br = self.variables.canvas_width
        if image_y_br > self.variables.canvas_image_object.image_reader.full_image_ny:
            image_y_br = self.variables.canvas_image_object.image_reader.full_image_ny
            new_canvas_x_br, new_canvas_y_br = self.variables.canvas_image_object.full_image_yx_to_canvas_coords(
                (image_y_br, image_x_br))
            new_canvas_x_ul, new_canvas_y_ul = int(new_canvas_x_br - self.variables.canvas_width), int(
                new_canvas_y_br - self.variables.canvas_height)
        if image_x_br > self.variables.canvas_image_object.image_reader.full_image_nx:
            image_x_br = self.variables.canvas_image_object.image_reader.full_image_nx
            new_canvas_x_br, new_canvas_y_br = self.variables.canvas_image_object.full_image_yx_to_canvas_coords(
                (image_y_br, image_x_br))
            new_canvas_x_ul, new_canvas_y_ul = int(new_canvas_x_br - self.variables.canvas_width), int(
                new_canvas_y_br - self.variables.canvas_height)

        canvas_rect = (new_canvas_x_ul, new_canvas_y_ul, new_canvas_x_br, new_canvas_y_br)
        self.zoom_to_selection(canvas_rect, self.variables.animate_pan)
        self.hide_shape(self.variables.zoom_rect_id)

    def config_do_not_scale_image_to_fit(self):
        """
        Set configuration to not scale image to fit.

        Returns
        -------
        None
        """
        # establish scrollbars
        self.sbarv = tkinter.Scrollbar(self, orient=tkinter.VERTICAL)
        self.sbarh = tkinter.Scrollbar(self, orient=tkinter.HORIZONTAL)
        self.sbarv.config(command=self.yview)
        self.sbarh.config(command=self.xview)

        self.config(yscrollcommand=self.sbarv.set)
        self.config(xscrollcommand=self.sbarh.set)
        self.sbarv.grid(row=0, column=1, stick=tkinter.N+tkinter.S)
        self.sbarh.grid(row=1, column=0, sticky=tkinter.E+tkinter.W)

    # TODO: this should have png -> image or image_file.
    #   It's not the full canvas? This is confusing.
    def save_full_canvas_as_png(self, output_fname):
        """
        Save the canvas as a image file.

        Parameters
        ----------
        output_fname : str
            The path of the output file.

        Returns
        -------
        None
        """

        # put a sleep in here in case there is a dialog covering the screen
        # before this method is called.
        time.sleep(0.1)
        # TODO: are we missing a PIL.Image conversion here?
        im = self.save_currently_displayed_canvas_to_numpy_array()
        im.save(output_fname)

    # TODO: figure out proper offsets, the current solution is close but not perfect
    def save_currently_displayed_canvas_to_numpy_array(self):
        """
        Export the currently displayed canvas as a numpy array.

        Returns
        -------
        numpy.ndarray
        """

        x_ul = self.winfo_rootx() + 1
        y_ul = self.winfo_rooty() + 1

        x_lr = x_ul + self.variables.canvas_width
        y_lr = y_ul + self.variables.canvas_height
        im = ImageGrab.grab()
        im = im.crop((x_ul, y_ul, x_lr, y_lr))
        return im

    # noinspection PyUnusedLocal
    def activate_color_selector(self, event):
        """
        The activate color selector callback function.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        color = colorchooser.askcolor()[1]
        self.variables.foreground_color = color
        self.change_shape_color(self.variables.current_shape_id, color)

    def find_closest_shape_coord(self, shape_id, canvas_x, canvas_y):
        """
        Finds the closest shape to the provided coordinates, and returns its id.

        Parameters
        ----------
        shape_id : int
        canvas_x : int
        canvas_y : int

        Returns
        -------
        int
        """
        vector_object = self.get_vector_object(self.variables.current_shape_id)
        coords = self.get_shape_canvas_coords(shape_id)
        if vector_object.type == SHAPE_TYPES.RECT:
            select_x1, select_y1, select_x2, select_y2 = coords
            select_xul = min(select_x1, select_x2)
            select_xlr = max(select_x1, select_x2)
            select_yul = min(select_y1, select_y2)
            select_ylr = max(select_y1, select_y2)

            ul = (select_xul, select_yul)
            ur = (select_xlr, select_yul)
            lr = (select_xlr, select_ylr)
            ll = (select_xul, select_ylr)

            rect_coords = [(select_x1, select_y1), (select_x2, select_y2)]

            all_coords = [ul, ur, lr, ll]

            squared_distances = []
            for corner_coord in all_coords:
                coord_x, coord_y = corner_coord
                d = (coord_x - canvas_x)**2 + (coord_y - canvas_y)**2
                squared_distances.append(d)
            closest_coord_index = numpy.where(squared_distances == numpy.min(squared_distances))[0][0]
            closest_coord = all_coords[closest_coord_index]
            if closest_coord not in rect_coords:
                if closest_coord == ul:
                    self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id, (ul[0], ul[1], lr[0], lr[1]))
                if closest_coord == ur:
                    self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id, (ur[0], ur[1], ll[0], ll[1]))
                if closest_coord == lr:
                    self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id, (ul[0], ul[1], lr[0], lr[1]))
                if closest_coord == ll:
                    self.modify_existing_shape_using_canvas_coords(self.variables.current_shape_id, (ll[0], ll[1], ur[0], ur[1]))

            coords = self.get_shape_canvas_coords(shape_id)

        squared_distances = []
        coord_indices = numpy.arange(0, len(coords), step=2)
        for i in coord_indices:
            coord_x, coord_y = coords[i], coords[i+1]
            d = (coord_x - canvas_x)**2 + (coord_y - canvas_y)**2
            squared_distances.append(d)
        closest_coord_index = numpy.where(squared_distances == numpy.min(squared_distances))[0][0]
        return closest_coord_index

    def find_closest_shape(self, canvas_x, canvas_y):
        """
        Finds the closest shape to the provided canvas coordinates, and returns its id.

        Parameters
        ----------
        canvas_x : float
        canvas_y : float

        Returns
        -------
        int
        """

        # TODO: improve this.  Right now it finds closest shape just based on distance to corners.
        #   Improvements should include:
        #       finding a closest point if the x/y coordinate is inside a polygon.
        #       finding closest distance to each line of a polygon.

        non_tool_shape_ids = self.get_non_tool_shape_ids()
        closest_distances = []
        for shape_id in non_tool_shape_ids:
            coords = self.get_shape_canvas_coords(shape_id)
            squared_distances = []
            coord_indices = numpy.arange(0, len(coords), step=2)
            for i in coord_indices:
                coord_x, coord_y = coords[i], coords[i + 1]
                d = (coord_x - canvas_x) ** 2 + (coord_y - canvas_y) ** 2
                squared_distances.append(d)
            closest_distances.append(numpy.min(squared_distances))
        closest_shape_id = non_tool_shape_ids[numpy.where(closest_distances == numpy.min(closest_distances))[0][0]]
        return closest_shape_id

    def get_non_tool_shape_ids(self):
        """
        Gets the shape ids for the everything except shapes assigned to tools, such as the zoom and selection shapes

        Returns
        -------
        List
        """

        all_shape_ids = self.variables.shape_ids
        tool_shape_ids = self.get_tool_shape_ids()
        return list(numpy.setdiff1d(all_shape_ids, tool_shape_ids))

    def get_tool_shape_ids(self):
        """
        Gets the shape ids for the zoom rectangle and select rectangle.

        Returns
        -------
        List
        """

        tool_shape_ids = [self.variables.zoom_rect_id,
                          self.variables.select_rect_id]
        return tool_shape_ids
