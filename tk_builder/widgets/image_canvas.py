# -*- coding: utf-8 -*-
"""
This module provides functionality for main image canvas functionality. This is
expected to be the main building block for any image based tool.
"""

__classification__ = "UNCLASSIFIED"
__author__ = ("Jason Casey", "Thomas McCullough")

import logging
import io
from PIL import ImageTk, Image
import platform
import tkinter
import tkinter.colorchooser as colorchooser
from tkinter.messagebox import showinfo
from typing import Union, Tuple, List, Dict
from collections import OrderedDict

import numpy

from tk_builder.base_elements import BooleanDescriptor, IntegerDescriptor, \
    IntegerTupleDescriptor, StringDescriptor, TypedDescriptor, FloatDescriptor
from tk_builder.image_reader import ImageReader
from tk_builder.utils.color_utils.color_cycler import ColorCycler
from tk_builder.utils.color_utils.hex_color_palettes import SeabornHexPalettes
from tk_builder.widgets import basic_widgets

from sarpy.compliance import string_types
from sarpy.io.general.base import BaseReader
from sarpy.geometry.geometry_elements import GeometryObject, LinearRing, LineString, Point
import sarpy.visualization.remap as remap


#######
# shape drawing explanations

# TODO: populate this drawing explanations
_POINT_EXPLANATION = """
"""

_LINE_EXPLANATION = """
"""

_ARROW_EXPLANATION = """
"""

_RECT_EXPLANATION = """
"""

_ELLIPSE_EXPLANATION = """
"""

_POLYGON_EXPLANATION = """
"""

_TEXT_EXPLANATION = """
"""

#######
# enum type objects

class ToolConstants(object):
    VIEW = 0  # the default tool
    ZOOM_IN = 1  # tool for defining zoom rectangle, for zooming in
    ZOOM_OUT = 2  # tool for defining zoom rectangle, for zooming out
    SELECT = 3  # tool for defining selection rectangle, for a region
    PAN = 4  # tool for defining pan behavior
    NEW_SHAPE = 5  # tool for starting to draw a new shape
    EDIT_SHAPE = 6  # tool for editing a shape
    SELECT_CLOSEST_SHAPE = 7  # tool for selecting a shape, and setting to current
    SHIFT_SHAPE = 8  # tool for moving a shape via affine shift

    _names_to_values = OrderedDict([
        ('VIEW', VIEW),
        ('ZOOM_IN', ZOOM_IN),
        ('ZOOM_OUT', ZOOM_OUT),
        ('SELECT', SELECT),
        ('PAN', PAN),
        ('NEW_SHAPE', NEW_SHAPE),
        ('EDIT_SHAPE', EDIT_SHAPE),
        ('SELECT_CLOSEST_SHAPE', SELECT_CLOSEST_SHAPE),
        ('SHIFT_SHAPE', SHIFT_SHAPE)])
    _values_to_names = OrderedDict([(value, key) for key, value in _names_to_values.items()])

    @classmethod
    def validate(cls, value):
        """
        The tool enumeration value, if valid. Otherwise, None.

        Parameters
        ----------
        value
            The int value for validation, or the string value to evaluate.

        Returns
        -------
        None|int
        """

        if value in cls._names_to_values:
            return cls._names_to_values[value]
        if value in cls._values_to_names:
            return value
        return None

    @classmethod
    def get_name(cls, value):
        """
        None|str: Gets the name for the corresponding value.
        """

        return cls._values_to_names.get(value, None)


class ShapeTypeConstants(object):
    POINT = 0
    LINE = 1
    ARROW = 2
    RECT = 3
    ELLIPSE = 4
    POLYGON = 5
    TEXT = 6

    _names_to_values = OrderedDict([
        ('POINT', POINT),
        ('LINE', LINE),
        ('ARROW', ARROW),
        ('RECT', RECT),
        ('ELLIPSE', ELLIPSE),
        ('POLYGON', POLYGON),
        ('TEXT', TEXT)])
    _values_to_names = {value:key for key, value in _names_to_values.items()}

    @classmethod
    def validate(cls, value):
        """
        The shape enumeration value, if valid. Otherwise, None.

        Parameters
        ----------
        value
            The int value for validation, or the string value to evaluate.

        Returns
        -------
        None|int
        """

        if value in cls._names_to_values:
            return cls._names_to_values[value]
        if value in cls._values_to_names:
            return value
        return None

    @classmethod
    def get_name(cls, value):
        """
        None|str: Gets the name for the corresponding value.
        """

        return cls._values_to_names.get(value, None)

    @classmethod
    def geometric_shapes(cls):
        """
        Returns the collection of geometric shape types.

        Returns
        -------
        List[str]
        """

        return [cls.RECT, cls.LINE, cls.POLYGON, cls.ARROW, cls.ELLIPSE]

    @classmethod
    def point_shapes(cls):
        """
        Returns the collection of point type shapes.

        Returns
        -------
        List[str]
        """

        return [cls.POINT, cls.TEXT]


########
# component objects

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
        docstring='The display rescaling factor.')  # type: float
    canvas_full_image_upper_left_yx = IntegerTupleDescriptor(
        'canvas_full_image_upper_left_yx', length=2, default_value=(0, 0),
        docstring='The upper left corner of the full image canvas in '
                  'yx order.')  # type: Tuple
    canvas_ny = IntegerDescriptor(
        'canvas_ny', docstring='')  # type: int
    canvas_nx = IntegerDescriptor(
        'canvas_nx', docstring='')  # type: int

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
        pil_image = Image.fromarray(decimated_image)
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

        decimated_image_nx = decimated_image.shape[1]
        decimated_image_ny = decimated_image.shape[0]
        scale_factor_1 = float(self.canvas_nx)/decimated_image_nx
        scale_factor_2 = float(self.canvas_ny)/decimated_image_ny
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

    def update_canvas_display_image_from_full_image_rect(self, full_image_rect, decimation=None):
        """
        Update the canvas to the given image rectangle.

        Parameters
        ----------
        full_image_rect : Tuple|List
        decimation : None|int
            The decimation to use. If not provided, then an appropriate decimation
            will be determined.

        Returns
        -------
        None
        """

        int_rect = (int(full_image_rect[0]), int(full_image_rect[1]), int(full_image_rect[2]), int(full_image_rect[3]))
        if decimation is None:
            self.set_decimation_from_full_image_rect(int_rect)
        else:
            self.decimation_factor = decimation
        decimated_image_data = self.get_decimated_image_data_in_full_image_rect(int_rect, self.decimation_factor)
        self.update_canvas_display_from_numpy_array(decimated_image_data)
        self.canvas_full_image_upper_left_yx = (int_rect[0], int_rect[1])

    def update_canvas_display_image_from_canvas_rect(self, canvas_rect, decimation=None):
        """
        Update the canvas to the given canvas rectangle.

        Parameters
        ----------
        canvas_rect : Tuple|List
        decimation : None|int
            The decimation to use. An appropriate value will be calculated if not provided here.

        Returns
        -------
        None
        """

        full_image_rect = self.canvas_rect_to_full_image_rect(canvas_rect)
        full_image_rect = (int(round(full_image_rect[0])),
                           int(round(full_image_rect[1])),
                           int(round(full_image_rect[2])),
                           int(round(full_image_rect[3])))
        self.update_canvas_display_image_from_full_image_rect(full_image_rect, decimation=decimation)

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
        scale_factor = self.compute_display_scale_factor(image_data)
        self.display_rescaling_factor = scale_factor
        self.display_image = self.get_scaled_display_data(image_data)

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
        decimation_y = numpy.ceil(ny/float(self.canvas_ny))
        decimation_x = numpy.ceil(nx/float(self.canvas_nx))
        decimation_factor = max(decimation_y, decimation_x)
        decimation_factor = int(decimation_factor)

        min_decimation = 1
        max_decimation = min(int(nx-1), int(ny-1))

        decimation_factor = max(min_decimation, decimation_factor)
        decimation_factor = min(max_decimation, decimation_factor)
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
        decimation_factor = decimation_factor / self.display_rescaling_factor

        siz = int(len(full_image_yx)/2)
        out = []
        for i in range(siz):
            out.extend(
                (float(full_image_yx[2*i+1] - self.canvas_full_image_upper_left_yx[1]) / decimation_factor,
                 float(full_image_yx[2*i] - self.canvas_full_image_upper_left_yx[0]) / decimation_factor))
        return out


class VectorObject(object):
    """
    The vector object - for shapes rendered on the image canvas.
    """

    # noinspection PyUnusedLocal
    def __init__(self,
                 uid, vector_type, image_coords=None, point_size=None,
                 image_drag_limits=None, outline=None, fill=None, color=None, **kwargs):
        """

        Parameters
        ----------
        uid : int
        vector_type : str|int
        image_coords
        point_size
        image_drag_limits
        outline
        fill
        """

        self._uid = uid
        v_type = ShapeTypeConstants.validate(vector_type)
        if v_type is None:
            raise ValueError('Unable to validate vector type {}'.format(vector_type))

        self._type = v_type
        self._color = None
        self.image_coords = image_coords
        self.point_size = point_size
        self.image_drag_limits = image_drag_limits
        if color is not None:
            self.color = color
        else:
            if v_type in [ShapeTypeConstants.RECT, ShapeTypeConstants.POLYGON, ShapeTypeConstants.ELLIPSE, ShapeTypeConstants.POINT]:
                self.color = outline
            elif v_type in [ShapeTypeConstants.LINE, ShapeTypeConstants.ARROW]:
                self.color = fill
            # TODO: text?

        if self._color is None:
            self._color = 'cyan'

    @property
    def uid(self):
        """
        int: The vector object id.
        """

        return self._uid

    @property
    def type(self):
        """
        int: The type of vector object. The feasible values should be governed by `ShapeTypeConstants`.
        """

        return self._type

    @property
    def color(self):
        """
        None|str: The color.
        """

        return self._color

    @color.setter
    def color(self, value):
        """

        Parameters
        ----------
        value : None|str
        """

        if value is None:
            self._color = 'cyan'
            return
        if not isinstance(value, string_types):
            raise TypeError('Requires a string.')
        self._color = value


########
# component variables containers

class RectangleTool(object):
    rect_id = IntegerDescriptor(
        'uid',
        docstring='The rectangle id.')  # type: int
    rect_color = StringDescriptor(
        'color', default_value='cyan',
        docstring='The rectangle color (named or hexidecimal).')  # type: str
    border_width = IntegerDescriptor(
        'border_width', default_value=2,
        docstring='The rectangle border width, in pixels.')  # type: int

    def __init__(self, uid, color='cyan', border_width=2):
        """
        Rectangle tool properties.

        Parameters
        ----------
        uid
        color
        border_width
        """

        self.uid = uid
        self.color = color
        self.border_width = border_width


class CanvasConfig(object):
    """
    Configuration state for the image canvas object
    """

    vertex_selector_pixel_threshold = FloatDescriptor(
        'vertex_selector_pixel_threshold', default_value=10.0,
        docstring='The threshold in canvas pixel distance for vertex selection.')  # type: float
    shape_selector_pixel_threshold = FloatDescriptor(
        'shape_selector_pixel_threshold', default_value=10.0,
        docstring='The threshold in canvas pixel distance for shape selection.')  # type: float
    zoom_box_size_threshold = FloatDescriptor(
        'zoom_box_size_threshold', default_value=20.0,
        docstring='minimum size in canvas pixels for the zoom box for any action to take place.')  # type: float
    pan_pixel_threshold = FloatDescriptor(
        'pan_pixel_threshold', default_value=10,
        docstring='The threshold for in canvas pixels for actually performing a pan operation.')  # type: float
    zoom_pixel_threshold = FloatDescriptor(
        'zoom_pixel_threshold', default_value=20,
        docstring='The threshold in canvas pixels (either dimension) beyond which '
                  'zooming will not actually occur.')  # type: float
    select_size_threshold = FloatDescriptor(
        'select_size_threshold', default_value=10,
        docstring='The threshold in canvas pixels (either dimension) beyond which '
                  'selection should not occur.')  # type: float


class CanvasState(object):
    """
    Some state variable for the image canvas.
    """

    canvas_height = IntegerDescriptor(
        'canvas_height', default_value=400,
        docstring='The default canvas height, in pixels.')  # type: int
    canvas_width = IntegerDescriptor(
        'canvas_width', default_value=600,
        docstring='The default canvas width, in pixels.')  # type: int
    max_height = IntegerDescriptor(
        'max_height', default_value=800,
        docstring='The maximum canvas height, in pixels.')  # type: int
    max_width = IntegerDescriptor(
        'max_width', default_value=800,
        docstring='The maximum canvas height, in pixels.')  # type: int
    min_height = IntegerDescriptor(
        'min_height', default_value=100,
        docstring='The minimum canvas width, in pixels.')  # type: int
    min_width = IntegerDescriptor(
        'min_width', default_value=100,
        docstring='The minimum canvas width, in pixels.')  # type: int
    rect_border_width = IntegerDescriptor(
        'rect_border_width', default_value=2,
        docstring='The (margin) rectangular border width, in pixels.')  # type: int
    line_width = IntegerDescriptor(
        'line_width', default_value=3,
        docstring='The line width, in pixels.')  # type: int
    point_size = IntegerDescriptor(
        'point_size', default_value=5,
        docstring='The point size, in pixels.')  # type: int
    poly_border_width = IntegerDescriptor(
        'poly_border_width', default_value=3,
        docstring='The polygon border width, in pixels.')  # type: int
    foreground_color = StringDescriptor(
        'foreground_color', default_value='red',
        docstring='The foreground color (named or hexidecimal string).')  # type: str


class ShapeDrawingState(object):
    """
    An object for keeping the state of partially drawn shapes/tool jobs. Note that not
    all properties apply for any given tool.
    """

    actively_drawing = BooleanDescriptor(
        'actively_drawing', default_value=False,
        docstring='Are we actively drawing a polygon?')  # type: bool
    insert_at_index = IntegerDescriptor(
        'insert_at_index', default_value=0,
        docstring='For lines and polygons. At what index should the point be edited '
                  'or inserted?')  # type: int
    anchor_point_xy = IntegerTupleDescriptor(
        'anchor_point_xy', length=2, default_value=(0, 0),
        docstring='The anchor point, in canvas coordinates in xy order.')  # type: Union[None, Tuple]
    # not actively maintained state
    tmp_anchor_point_xy = IntegerTupleDescriptor(
        'tmp_anchor_point_xy', length=2, default_value=(0, 0),
        docstring='The temporary anchor point, in canvas coordinates in xy order.')  # type: Union[None, Tuple]

    def __init__(self):
        self._other_state = OrderedDict()

    @property
    def other_state(self):
        # type: () -> Dict
        """
        Dict: Other state variables.
        """

        return self._other_state

    def set_inactive(self):
        """
        Set the state to inactive.

        Returns
        -------
        None
        """

        self.actively_drawing = False
        self.insert_at_index = 0
        self.anchor_point_xy = (0, 0)
        self._other_state = OrderedDict()

    def set_active(self, insert_at_index=0, anchor_point_xy=(0, 0)):
        """
        Start drawing object.

        Parameters
        ----------
        insert_at_index : int
        anchor_point_xy : Tuple

        Returns
        -------
        None
        """

        self.actively_drawing = True
        self.insert_at_index = insert_at_index
        self.anchor_point_xy = anchor_point_xy
        self._other_state = OrderedDict()


#########
# main variables container

class AppVariables(object):
    """
    The canvas image application variables.
    """

    image_id = IntegerDescriptor(
        'image_id',
        docstring='The image id.')  # type: Union[None, int]
    current_shape_id = IntegerDescriptor(
        'current_shape_id',
        docstring='The current shape id.')  # type: Union[None, int]
    canvas_image_object = TypedDescriptor(
        'canvas_image_object', CanvasImage,
        docstring='The canvas image object.')  # type: CanvasImage
    tk_im = TypedDescriptor(
        'tk_im', ImageTk.PhotoImage,
        docstring='The Tkinter Image.')  # type: ImageTk.PhotoImage
    # some configuration properties
    config = TypedDescriptor(
        'config', CanvasConfig,
        docstring='Some basic configuration properties for the image canvas.')  # type: CanvasConfig
    # zoom rectangle properties
    zoom_rect = TypedDescriptor(
        'zoom_rect', RectangleTool,
        docstring='The zoom rectangle properties.')  # type: RectangleTool
    # selection rectangle properties
    select_rect = TypedDescriptor(
        'select_rect', RectangleTool,
        docstring='The select rectangle properties.')  # type: RectangleTool
    # some state properties
    state = TypedDescriptor(
        'state', CanvasState,
        docstring='Some basic state variables for the canvas.')  # type: CanvasState
    # shape drawing state
    shape_drawing = TypedDescriptor(
        'shape_drawing', ShapeDrawingState,
        docstring='State variables for shape drawing.')  # type: ShapeDrawingState

    def __init__(self):
        self.config = CanvasConfig()
        self.state = CanvasState()
        self.zoom_rect = RectangleTool(-1, color='blue', border_width=3)
        self.select_rect = RectangleTool(-1, color='red', border_width=3)
        self.shape_drawing = ShapeDrawingState()

        self._shape_ids = []
        self._vector_objects = OrderedDict()
        self._remap_function = remap.density
        self.highlight_color_palette = SeabornHexPalettes.blues  # type: List[str]

    @property
    def shape_ids(self):
        # type: () -> List[int]
        """
        List[int]: The list of shape ids. This should not be manipulated directly.
        """

        return self._shape_ids

    @property
    def vector_objects(self):
        # type: () -> Dict[int, VectorObject]
        """
        Dict[int, VectorObject]: The dictionary associating the shape id with the vector object.
        This should be be manipulated directly.
        """
        return self._vector_objects

    def track_shape(self, vector_object):
        """
        Adds the provided vector object to tracking.

        Parameters
        ----------
        vector_object : VectorObject

        Returns
        -------
        None
        """

        self._shape_ids.append(vector_object.uid)
        self._vector_objects[vector_object.uid] = vector_object

    @property
    def remap_function(self):
        """
        Callable: the remap function for usage.
        """

        return self._remap_function

    def set_remap_type(self, remap_type):
        if callable(remap_type):
            self._remap_function = remap_type
        elif hasattr(remap, remap_type):
            self._remap_function = getattr(remap, remap_type)
        else:
            logging.error('Got unexpected value for remap {}. Using "density".'.format(remap_type))
            self._remap_function = remap.density


######
# image canvas widget

class ImageCanvas(basic_widgets.Canvas):
    def __init__(self, master):
        """

        Parameters
        ----------
        master
            The primary widget.
        """

        osplat = platform.system()
        if osplat == "Windows":
            import ctypes
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()

        # for properties of image canvas
        self._new_shape_type = ShapeTypeConstants.POLYGON
        self._current_tool = ToolConstants.VIEW
        self._active_tool = ToolConstants.VIEW
        self._current_shape_id = None

        basic_widgets.Canvas.__init__(self, master, highlightthickness=0)
        self.pack(fill=tkinter.BOTH, expand=tkinter.NO)

        self.variables = AppVariables()

        self.variables.zoom_rect.uid = self.create_new_rect(
            (0, 0, 0, 0), make_current=False, is_tool=True, increment_color=False,
            outline=self.variables.zoom_rect.color, width=self.variables.zoom_rect.border_width)
        self.variables.select_rect.uid = self.create_new_rect(
            (0, 0, 0, 0), make_current=False, is_tool=True, increment_color=False,
            outline=self.variables.select_rect.color, width=self.variables.select_rect.border_width)

        # hide the shapes we initialize
        self.hide_shape(self.variables.select_rect.uid)
        self.hide_shape(self.variables.zoom_rect.uid)

        self.on_resize(self.callback_handle_resize)
        self.on_left_mouse_click(self.callback_handle_left_mouse_click)
        self.on_left_mouse_motion(self.callback_handle_left_mouse_motion)
        self.on_left_mouse_release(self.callback_handle_left_mouse_release)
        self.on_left_mouse_double_click(self.callback_handle_left_mouse_double_click)
        self.on_right_mouse_click(self.callback_handle_right_mouse_click)
        self.on_right_mouse_motion(self.callback_handle_right_mouse_motion)
        self.on_right_mouse_release(self.callback_handle_right_mouse_release)
        self.on_mouse_motion(self.callback_handle_mouse_motion)
        self._color_cycler = ColorCycler(n_colors=10)

    @property
    def color_cycler(self):
        return self._color_cycler

    def set_color_cycler(self, n_colors, hex_color_palette):
        self._color_cycler = ColorCycler(n_colors, hex_color_palette)

    @property
    def current_tool(self):
        """
        int: The current tool.
        """

        return self._current_tool

    @current_tool.setter
    def current_tool(self, value):
        old_tool = self._current_tool

        the_value = ToolConstants.validate(value)
        if the_value is None:
            logging.error('Got unhandled tool value {}, set to VIEW.'.format(value))
            the_value = ToolConstants.VIEW
        self._current_tool = the_value
        if old_tool != the_value:
            self.emit_current_tool_changed()

    @property
    def active_tool(self):
        return self._active_tool

    @active_tool.setter
    def active_tool(self, value):
        the_value = ToolConstants.validate(value)
        if the_value is None:
            logging.error('Got unhandled tool value {}, set to VIEW.'.format(value))
            the_value = ToolConstants.VIEW
        self._active_tool = the_value

    @property
    def new_shape_type(self):
        """
        int: What shape type will be drawn next? See ShapeTypeConstants for the enumeration.
        """

        return self._new_shape_type

    @new_shape_type.setter
    def new_shape_type(self, value):
        """
        Sets the new shape type from enum value, or enum string.

        Parameters
        ----------
        value : int|str
        """

        the_value = ShapeTypeConstants.validate(value)
        if the_value is None:
            raise ValueError('Got unexpected value {} for shape type'.format(value))

        old_type = self._new_shape_type
        if old_type != the_value:
            self._new_shape_type = the_value
            self.emit_new_shape_type_changed()

    @property
    def current_shape_id(self):
        """
        None|int: The current shape id.
        """

        return self._current_shape_id

    @current_shape_id.setter
    def current_shape_id(self, shape_id):
        """
        Set the current shape id as appropriate. Emits signals, as required.

        Parameters
        ----------
        shape_id : None|int
        """

        old_vector_obj = self.get_vector_object(self._current_shape_id)
        new_vector_obj = self.get_vector_object(shape_id)
        if old_vector_obj is None:
            old_id = None
            old_type = None
        else:
            old_id = old_vector_obj.uid
            old_type = old_vector_obj.type


        if (old_id is None and shape_id is None) or (old_id == shape_id):
            return  # nothing to be done

        self.lowlight_existing_shape(old_id)
        self._current_shape_id = shape_id
        self.highlight_existing_shape(shape_id)
        self.emit_shape_deselect(old_id, old_type)
        self.show_shape(shape_id)
        if shape_id is not None:
            self.emit_shape_select(shape_id, new_vector_obj.type)

    def activate_color_selector(self):
        """
        The activate color selector callback function.

        Returns
        -------
        None
        """

        color = colorchooser.askcolor()[1]
        self.variables.state.foreground_color = color
        self.change_shape_color(self._current_shape_id, color)

    def _increment_color(self):
        """
        Increment the color to the next color.

        Returns
        -------
        None
        """

        self.variables.state.foreground_color = self.color_cycler.next_color

    def do_nothing(self, event):
        pass

    def _reinitialize_reader(self):
        """
        Re-initializes image view, based on an image reader change, or change in image index.

        Returns
        -------
        None
        """

        self.reinitialize_shapes()
        full_ny = self.variables.canvas_image_object.image_reader.full_image_ny
        full_nx = self.variables.canvas_image_object.image_reader.full_image_nx
        self.zoom_to_full_image_selection([0, 0, full_ny, full_nx])
        self.set_current_tool_to_view()
        # update drag limits for the tools
        zoom_object = self.get_vector_object(self.variables.zoom_rect.uid)
        zoom_object.image_drag_limits = (0, 0, full_ny, full_nx)
        select_object = self.get_vector_object(self.variables.select_rect.uid)
        select_object.image_drag_limits = (0, 0, full_ny, full_nx)

    def set_image_reader(self, image_reader):
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
            image_reader, self.variables.state.canvas_width, self.variables.state.canvas_height)
        # set the remap
        self.variables.canvas_image_object.image_reader.set_remap_type(self.variables.remap_function)
        # update the canvas elements
        self._reinitialize_reader()

    def get_image_reader(self):
        """
        Gets the underlying image reader.

        Returns
        -------
        None|ImageReader
        """

        return self.variables.canvas_image_object.image_reader

    def get_base_reader(self):
        """
        Gets the base reader underlying image reader.

        Returns
        -------
        None|BaseReader
        """

        return getattr(self.variables.canvas_image_object.image_reader, 'base_reader', None)

    def set_image_index(self, the_value):
        """
        Sets the image index for the reader, which re-initializes the image data.
        This assumes that vetting for the prospective value has already been performed.

        Parameters
        ----------
        the_value : int
        """

        if self.variables.canvas_image_object is None or self.variables.canvas_image_object.image_reader is None:
            return

        current_value = self.variables.canvas_image_object.image_reader.index
        if the_value == current_value:
            return # nothing to be done

        try:
            self.variables.canvas_image_object.image_reader.index = the_value
            self._reinitialize_reader()
            self.emit_image_index_changed()
        except AttributeError:
            return  # nothing to be done

    def get_image_index(self):
        """
        Gets the current image index.

        Returns
        -------
        None|int
        """

        if self.variables.canvas_image_object is None or \
                self.variables.canvas_image_object.image_reader is None:
            return None
        return self.variables.canvas_image_object.image_reader.index

    def get_image_remap(self):
        """
        Gets the current remap function.

        Returns
        -------
        None|Callable
        """

        if self.variables.canvas_image_object is None or \
                self.variables.canvas_image_object.image_reader is None:
            return None
        return self.variables.canvas_image_object.image_reader.remap_function

    def get_image_extent(self):
        """
        Get the actual extent of the displayed image. Note that the image
        canvas might not be completely full.

        Returns
        -------
        None|(Tuple, int)
            The image extent of the form `(start y, start x, end y, end x)` and
            the decimation factor. In the SICD convention `y = row` and `x = column`.
        """

        if self.variables.canvas_image_object is None or \
                self.variables.canvas_image_object.image_reader is None:
            return None

        # the actual image bounds
        y_limit = self.variables.canvas_image_object.image_reader.full_image_ny
        x_limit = self.variables.canvas_image_object.image_reader.full_image_nx

        # the basics about the canvas object
        the_origin = self.variables.canvas_image_object.canvas_full_image_upper_left_yx
        the_decimation = self.variables.canvas_image_object.decimation_factor/self.variables.canvas_image_object.display_rescaling_factor
        # the canvas size
        the_height = self.variables.canvas_image_object.canvas_ny
        the_width = self.variables.canvas_image_object.canvas_nx

        the_bounds = (
            the_origin[0],
            the_origin[1],
            the_origin[0] + the_decimation*min(int(the_height), int((y_limit-the_origin[0])/float(the_decimation))),
            the_origin[1] + the_decimation*min(int(the_width), int((x_limit-the_origin[1])/float(the_decimation))))
        return the_bounds, self.variables.canvas_image_object.decimation_factor

    def get_vector_object(self, vector_id):
        """

        Parameters
        ----------
        vector_id : int

        Returns
        -------
        VectorObject
        """

        return self.variables.vector_objects.get(vector_id, None)

    def get_current_vector_object(self):
        """
        Gets the current vector object.

        Returns
        -------
        None|VectorObject
        """

        return self.get_vector_object(self._current_shape_id)

    def get_current_nontool_vector_object(self):
        """
        Gets the current vector object, provided that it is not one tool shapes.

        Returns
        -------
        None|VectorObject
        """

        current_id = self._current_shape_id
        if current_id is None or current_id in self.get_tool_shape_ids():
            return None
        return self.get_vector_object(current_id)

    def get_non_tool_shape_ids(self):
        """
        Gets the shape ids for the everything except shapes assigned to tools,
        such as the zoom and selection shapes.

        Returns
        -------
        List[int]
        """

        all_shape_ids = set(self.variables.shape_ids)
        return list(all_shape_ids.difference(self.get_tool_shape_ids()))

    def get_tool_shape_ids(self):
        """
        Gets the shape ids for the zoom rectangle and select rectangle.

        Returns
        -------
        List[int]
        """

        return [self.variables.zoom_rect.uid, self.variables.select_rect.uid]

    def show_shape_drawing_explanation(self):
        """
        Show a pop-up explanation with the explanation for how to draw the given shape.

        Returns
        -------
        None
        """

        the_shape_type = self.new_shape_type
        if the_shape_type is None:
            showinfo('No shape selected', message='No shape is selected for drawing.')
        elif the_shape_type == ShapeTypeConstants.POINT:
            showinfo('Point Drawing', message=_POINT_EXPLANATION)
        elif the_shape_type == ShapeTypeConstants.LINE:
            showinfo('Line Drawing', message=_LINE_EXPLANATION)
        elif the_shape_type == ShapeTypeConstants.ARROW:
            showinfo('Arrow Drawing', message=_ARROW_EXPLANATION)
        elif the_shape_type == ShapeTypeConstants.RECT:
            showinfo('Rectangle Drawing', message=_RECT_EXPLANATION)
        elif the_shape_type == ShapeTypeConstants.ELLIPSE:
            showinfo('Ellipse drawing', message=_ELLIPSE_EXPLANATION)
        elif the_shape_type == ShapeTypeConstants.POLYGON:
            showinfo('Polygon Drawing', message=_POLYGON_EXPLANATION)
        else:
            showinfo('No Information',
                     message='No drawing information for type '
                             '{}'.format(ShapeTypeConstants.get_name(the_shape_type)))

    def callback_handle_resize(self, event):
        """
        Handle a resize event.

        Parameters
        ----------
        event
        """

        width = event.width
        height = event.height
        self.resize_contents(width, height)

    def resize_contents(self, width, height):
        """
        Modify the image canvas contents based on a resize of the
        Resize the image canvas size.

        Parameters
        ----------
        width : int
        height : int
        """

        self.variables.state.canvas_width = width
        self.variables.state.canvas_height = height

        if self.variables.canvas_image_object is None:
            return

        self.variables.canvas_image_object.canvas_nx = width
        self.variables.canvas_image_object.canvas_ny = height

        if self.variables.canvas_image_object.image_reader is None:
            return  # nothing more to be done

        decimation = self.variables.canvas_image_object.decimation_factor
        the_height = height*decimation  # in image pixels
        the_width = width*decimation  # in image pixels

        # what is the current displayed image origin? (i.e. upper left)
        y_lower, x_lower = self.variables.canvas_image_object.canvas_full_image_upper_left_yx

        # what are the image limits?
        y_limit = self.variables.canvas_image_object.image_reader.full_image_ny  # row
        x_limit = self.variables.canvas_image_object.image_reader.full_image_nx  # column

        y_upper = y_lower + the_height
        if y_upper > y_limit:
            y_upper = y_limit
            y_lower = max(0, y_limit-the_height)
        x_upper = x_lower + the_width
        if x_upper > x_limit:
            x_upper = x_limit
            x_lower = max(0, x_limit-the_width)
        full_rectangle = [y_lower, x_lower, y_upper, x_upper]
        self.zoom_to_full_image_selection(full_rectangle)

    def set_remap(self, remap_value):
        """
        Sets the remap, where applicable. Emits the <<RemapChanged>> event.

        Parameters
        ----------
        remap_value : str|Callable
        """

        self.variables.set_remap_type(remap_value)
        if self.variables.canvas_image_object is None or self.variables.canvas_image_object.image_reader is None:
            return
        self.variables.canvas_image_object.image_reader.set_remap_type(remap_value)
        self.update_current_image()
        self.emit_remap_changed()

    # mouse event callbacks
    def callback_handle_left_mouse_click(self, event):
        """
        Left mouse click callback.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        if self.active_tool == ToolConstants.VIEW:
            return  # nothing to be done
        elif self.current_tool in [ToolConstants.ZOOM_IN, ToolConstants.ZOOM_OUT]:
            self.modify_existing_shape_using_canvas_coords(self.variables.zoom_rect.uid, (event.x, event.y, event.x, event.y))
            anchor = (event.x, event.y)
            self.variables.shape_drawing.set_active(insert_at_index=1, anchor_point_xy=anchor)
            self.variables.shape_drawing.tmp_anchor_point_xy = anchor
            self.show_shape(self.variables.zoom_rect.uid)
            return
        elif self.active_tool == ToolConstants.SELECT:
            self.modify_existing_shape_using_canvas_coords(self.variables.select_rect.uid, (event.x, event.y, event.x, event.y))
            anchor = (event.x, event.y)
            self.set_select_initial_state(anchor)
            return
        elif self.current_tool == ToolConstants.PAN:
            self.modify_existing_shape_using_image_coords(self.variables.zoom_rect.uid, (0, 0, 0, 0))
            self.current_shape_id = self.variables.zoom_rect.uid
            self.variables.shape_drawing.set_active(anchor_point_xy=(event.x, event.y))
            self.variables.shape_drawing.tmp_anchor_point_xy = (event.x, event.y)
            return
        elif self.active_tool == ToolConstants.SHIFT_SHAPE:
            if self._current_shape_id is None:
                self._select_closest_shape(event)
                return
            self.variables.shape_drawing.tmp_anchor_point_xy = event.x, event.y
            return
        elif self.active_tool == ToolConstants.SELECT_CLOSEST_SHAPE:
            self._select_closest_shape(event)
            return
        elif self.current_tool == ToolConstants.NEW_SHAPE:
            new_shape_type = self.new_shape_type

            start_x = self.canvasx(event.x)
            start_y = self.canvasy(event.y)
            coords = (start_x, start_y)
            if new_shape_type == ShapeTypeConstants.POINT:
                self.create_new_point(coords)
                self.variables.shape_drawing.set_active(insert_at_index=0, anchor_point_xy=coords)
            elif new_shape_type == ShapeTypeConstants.TEXT:
                self.create_new_text(coords, text='Text')
                self.variables.shape_drawing.set_active(insert_at_index=0, anchor_point_xy=coords)
            elif new_shape_type == ShapeTypeConstants.LINE:
                self.create_new_line((start_x, start_y, start_x+1, start_y+1))
                self.variables.shape_drawing.set_active(insert_at_index=1, anchor_point_xy=coords)
            elif new_shape_type == ShapeTypeConstants.ARROW:
                self.create_new_arrow((start_x, start_y, start_x+1, start_y+1))
                self.variables.shape_drawing.set_active(insert_at_index=1, anchor_point_xy=coords)
            elif new_shape_type == ShapeTypeConstants.RECT:
                self.create_new_rect((start_x, start_y, start_x+1, start_y+1))
                self.variables.shape_drawing.set_active(insert_at_index=1, anchor_point_xy=coords)
            elif new_shape_type == ShapeTypeConstants.ELLIPSE:
                self.create_new_ellipse((start_x, start_y, start_x+1, start_y+1))
                self.variables.shape_drawing.set_active(insert_at_index=1, anchor_point_xy=coords)
            elif new_shape_type == ShapeTypeConstants.POLYGON:
                self.create_new_polygon((start_x, start_y, start_x, start_y))
                self.variables.shape_drawing.set_active(insert_at_index=1, anchor_point_xy=coords)
            else:
                raise ValueError('Got unhandled shape type ShapeTypeConstants.{}'.format(ShapeTypeConstants.get_name(new_shape_type)))

            self._set_current_and_active_tool(ToolConstants.EDIT_SHAPE)
        elif self.active_tool == ToolConstants.EDIT_SHAPE:
            if self.current_shape_id is None:
                closest_shape_id = self._select_closest_shape(event)
                if closest_shape_id is not None:
                    self.current_shape_id = closest_shape_id
                    coord_index, the_distance, coord_x, coord_y = self.find_closest_shape_coord(closest_shape_id, event.x, event.y)
                    self.variables.shape_drawing.set_active(insert_at_index=coord_index, anchor_point_xy=(coord_x, coord_y))
                    # TODO: we should somehow indicate this event?
                return

            vector_object = self.get_current_vector_object()
            if vector_object.type in [ShapeTypeConstants.POINT, ShapeTypeConstants.TEXT]:
                self._update_text_or_point_event(event)
                return

            coord_index, the_distance, coord_x, coord_y = self.find_closest_shape_coord(vector_object.uid, event.x, event.y)
            if not self.variables.shape_drawing.actively_drawing:
                self.variables.shape_drawing.set_active(insert_at_index=coord_index, anchor_point_xy=(coord_x, coord_y))
                return
            elif the_distance < self.variables.config.vertex_selector_pixel_threshold:
                self.variables.shape_drawing.insert_at_index = coord_index
                # TODO: we should somehow indicate this event?
                return

            if vector_object.type == ShapeTypeConstants.LINE:
                self._update_line_event(event, insert=True)
            elif vector_object.type == ShapeTypeConstants.ARROW:
                self._update_arrow_event(event)
            elif vector_object.type in [ShapeTypeConstants.RECT, ShapeTypeConstants.ELLIPSE]:
                self.modify_existing_shape_using_canvas_coords(
                    vector_object.uid, (event.x, event.y, event.x, event.y))
                anchor = (event.x, event.y)
                self.variables.shape_drawing.set_active(insert_at_index=1, anchor_point_xy=anchor)
                self.variables.shape_drawing.tmp_anchor_point_xy = anchor
                return
            elif vector_object.type == ShapeTypeConstants.POLYGON:
                self._update_polygon_event(event, insert=True)
        else:
            raise ValueError('Got unhandled tool type ToolConstants.{}'.format(ToolConstants.get_name(self.active_tool)))

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

        active_tool = self.active_tool

        if active_tool in [ToolConstants.VIEW, ToolConstants.NEW_SHAPE, ToolConstants.SELECT_CLOSEST_SHAPE]:
            return  # nothing to be done
        if active_tool in [ToolConstants.ZOOM_IN, ToolConstants.ZOOM_OUT]:
            self._drag_zoom_rectangle(event)
        elif active_tool == ToolConstants.PAN:
            self._pan(event)
        elif active_tool == ToolConstants.SHIFT_SHAPE:
            shape_id = self.current_shape_id
            anchor = self.variables.shape_drawing.tmp_anchor_point_xy
            x_dist = event.x - anchor[0]
            y_dist = event.y - anchor[1]

            vector_object = self.get_vector_object(shape_id)
            t_coords = self.get_shape_canvas_coords(shape_id)
            new_coords = numpy.asarray(t_coords) + x_dist
            new_coords_y = numpy.asarray(t_coords) + y_dist
            new_coords[1::2] = new_coords_y[1::2]
            if vector_object.image_drag_limits is not None:
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
            self.modify_existing_shape_using_canvas_coords(shape_id, new_coords)
            self.variables.shape_drawing.tmp_anchor_point_xy = event.x, event.y
        elif active_tool == ToolConstants.EDIT_SHAPE:
            previous_coords = self.get_shape_canvas_coords(self.current_shape_id)
            new_coords = self._modify_coords(previous_coords, event.x, event.y, insert=False)
            self.modify_existing_shape_using_canvas_coords(self.current_shape_id, new_coords)

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

        if self.active_tool == ToolConstants.PAN:
            self._pan_finish(event)
            return
        elif self.current_tool == ToolConstants.ZOOM_IN:
            rect_coords = self.coords(self.variables.zoom_rect.uid)
            x_diff = abs(rect_coords[0] - rect_coords[2])
            y_diff = abs(rect_coords[1] - rect_coords[3])
            if x_diff >= self.variables.config.zoom_box_size_threshold and \
                    y_diff >= self.variables.config.zoom_box_size_threshold:
                self.zoom_to_canvas_selection(rect_coords)
            self.variables.shape_drawing.set_inactive()
            self.hide_shape(self.variables.zoom_rect.uid)
            self.modify_existing_shape_using_canvas_coords(self.variables.zoom_rect.uid, (0, 0, 0, 0))
            return
        elif self.current_tool == ToolConstants.ZOOM_OUT:
            rect_coords = self.coords(self.variables.zoom_rect.uid)
            x_diff = abs(rect_coords[0] - rect_coords[2])
            y_diff = abs(rect_coords[1] - rect_coords[3])
            if x_diff >= self.variables.config.zoom_box_size_threshold and \
                    y_diff >= self.variables.config.zoom_box_size_threshold:
                x1 = -rect_coords[0]
                x2 = self.variables.state.canvas_width + rect_coords[2]
                y1 = -rect_coords[1]
                y2 = self.variables.state.canvas_height + rect_coords[3]
                zoom_rect = (x1, y1, x2, y2)
                self.zoom_to_canvas_selection(zoom_rect)
            self.variables.shape_drawing.set_inactive()
            self.hide_shape(self.variables.zoom_rect.uid)
            self.modify_existing_shape_using_canvas_coords(self.variables.zoom_rect.uid, (0, 0, 0, 0))
            return
        elif self.current_tool == ToolConstants.SELECT:
            canvas_coords = self.get_shape_canvas_coords(self.variables.select_rect.uid)
            rect_coords = self.coords(self.variables.select_rect.uid)
            x_diff = abs(rect_coords[0] - rect_coords[2])
            y_diff = abs(rect_coords[1] - rect_coords[3])
            if x_diff < self.variables.config.select_size_threshold or \
                    y_diff < self.variables.config.select_size_threshold:
                # reset things, and start the selection over
                self.modify_existing_shape_using_canvas_coords(self.variables.select_rect.uid, (0, 0, 0, 0))
                self.variables.shape_drawing.set_inactive()
                return
            self.emit_select_finalized()
            return
        elif self.current_tool in [ToolConstants.EDIT_SHAPE, ToolConstants.SHIFT_SHAPE]:
            self.emit_shape_coords_finalized()
            return

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

        if self.current_tool == ToolConstants.VIEW:
            self.emit_coordinate_changed(event)
            return
        elif self.current_tool in [ToolConstants.EDIT_SHAPE, ToolConstants.SELECT]:
            if not self.variables.shape_drawing.actively_drawing:
                return
            vector_object = self.get_current_vector_object()
            if vector_object is None:
                return
            if vector_object.type in [ShapeTypeConstants.RECT, ShapeTypeConstants.ELLIPSE]:
                the_point = numpy.array([event.x, event.y])
                coords = self.get_shape_canvas_coords(self.current_shape_id)
                the_coords = self._normalized_rectangle_coordinates(coords)
                coords_diff = the_coords - the_point
                dists = numpy.sum(coords_diff * coords_diff, axis=1)

                self.active_tool = ToolConstants.EDIT_SHAPE
                if dists[0] < self.variables.config.vertex_selector_pixel_threshold:
                    self.config(cursor="top_left_corner")
                    self.variables.shape_drawing.tmp_anchor_point_xy = int(the_coords[0, 0]), int(the_coords[0, 1])
                elif dists[1] < self.variables.config.vertex_selector_pixel_threshold:
                    self.config(cursor="top_right_corner")
                    self.variables.shape_drawing.tmp_anchor_point_xy = int(the_coords[1, 0]), int(the_coords[1, 1])
                elif dists[2] < self.variables.config.vertex_selector_pixel_threshold:
                    self.config(cursor="bottom_right_corner")
                    self.variables.shape_drawing.tmp_anchor_point_xy = int(the_coords[2, 0]), int(the_coords[2, 1])
                elif dists[3] < self.variables.config.vertex_selector_pixel_threshold:
                    self.config(cursor="bottom_left_corner")
                    self.variables.shape_drawing.tmp_anchor_point_xy = int(the_coords[3, 0]), int(the_coords[3, 1])
                elif the_coords[0, 0] < event.x < the_coords[1, 0] and \
                        the_coords[0, 1] < event.y < the_coords[3, 1]:
                    # inside the rectangle
                    self.config(cursor="fleur")
                    self.active_tool = ToolConstants.SHIFT_SHAPE
                    self.variables.shape_drawing.tmp_anchor_point_xy = event.x, event.y
                else:
                    self.config(cursor="arrow")
            elif vector_object.type in [ShapeTypeConstants.LINE, ShapeTypeConstants.ARROW]:
                the_dist = self.find_distance_from_shape(vector_object.uid, event.x, event.y)
                the_vertex, vertex_distance, _, _ = self.find_closest_shape_coord(vector_object.uid, event.x, event.y)
                self.active_tool = ToolConstants.EDIT_SHAPE
                if vertex_distance < self.variables.config.vertex_selector_pixel_threshold:
                    self.config(cursor='cross')
                elif the_dist < self.variables.config.vertex_selector_pixel_threshold:
                    self.config(cursor='fleur')
                    self.active_tool = ToolConstants.SHIFT_SHAPE
                    self.variables.shape_drawing.tmp_anchor_point_xy = event.x, event.y
                else:
                    self.config(cursor='arrow')
            elif vector_object.type == ShapeTypeConstants.POLYGON:
                the_vertex, vertex_distance, _, _ = self.find_closest_shape_coord(vector_object.uid, event.x, event.y)

                # noinspection PyBroadException
                try:
                    geometry_object = self.get_geometry_for_shape(vector_object.uid, coordinate_type='canvas')
                except Exception:
                    geometry_object = None

                if geometry_object is None:
                    contained = False
                    the_dist = float('inf')
                else:
                    assert isinstance(geometry_object, LinearRing)

                    # noinspection PyBroadException
                    try:
                        contained = geometry_object.contain_coordinates(event.x, event.y)
                    except Exception:
                        # should only be from a feeble linear ring
                        contained = False
                    the_dist = geometry_object.get_minimum_distance((event.x, event.y))

                self.active_tool = ToolConstants.EDIT_SHAPE
                if vertex_distance < self.variables.config.vertex_selector_pixel_threshold:
                    self.config(cursor='cross')
                elif contained or the_dist < self.variables.config.vertex_selector_pixel_threshold:
                    self.config(cursor='fleur')
                    self.active_tool = ToolConstants.SHIFT_SHAPE
                    self.variables.shape_drawing.tmp_anchor_point_xy = event.x, event.y
                else:
                    self.config(cursor='arrow')
            elif vector_object.type in [ShapeTypeConstants.POINT, ShapeTypeConstants.TEXT]:
                the_dist = self.find_distance_from_shape(vector_object.uid, event.x, event.y)
                if the_dist < self.variables.config.vertex_selector_pixel_threshold:
                    self.config(cursor='fleur')
                    self.active_tool = ToolConstants.SHIFT_SHAPE
                    self.variables.shape_drawing.tmp_anchor_point_xy = event.x, event.y
                else:
                    self.config(cursor='arrow')
                    self.active_tool = ToolConstants.EDIT_SHAPE
            else:
                raise ValueError('Unhandled shape type ShapeTypeConstants.{}'.format(ShapeTypeConstants.get_name(vector_object.type)))

    # noinspection PyUnusedLocal
    def callback_handle_left_mouse_double_click(self, event):
        """
        Callback for left mouse double click.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        if self.current_tool == ToolConstants.EDIT_SHAPE:
            self.set_current_tool_to_view()

        pass

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

        if self.active_tool == ToolConstants.EDIT_SHAPE:
            if not self.variables.shape_drawing.actively_drawing:
                return

            vector_object = self.get_current_vector_object()
            if vector_object is not None and \
                    vector_object.type in [ShapeTypeConstants.LINE, ShapeTypeConstants.POLYGON]:
                # delete the coordinate at the current insertion index
                self._remove_current_coord()

    def callback_handle_right_mouse_motion(self, event):
        """
        Callback for motion while holding the right mouse button.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        pass

    def callback_handle_right_mouse_release(self, event):
        """
        Callback for releasing the right mouse button.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        pass

    def _pan(self, event, check_distance=True):
        """
        Perform the pan operation.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        def get_shift_limit(the_shift, the_limit, lower_value, upper_value):
            if lower_value < 0 or upper_value > the_limit:
                raise ValueError('This is not sensible.')

            if the_shift < 0:
                return max(the_shift, -lower_value)
            else:
                return min(the_shift, the_limit - upper_value)

        # get the current image bounds
        image_bounds, decimation = self.get_image_extent()
        # get the full image size
        full_y = self.variables.canvas_image_object.image_reader.full_image_ny
        full_x = self.variables.canvas_image_object.image_reader.full_image_nx

        # determine how to modify the current image bounds
        anchor = self.variables.shape_drawing.anchor_point_xy
        canvas_x_diff = anchor[0] - event.x
        canvas_y_diff = anchor[1] - event.y
        canvas_diff = (canvas_x_diff*canvas_x_diff + canvas_y_diff*canvas_y_diff)**0.5

        if check_distance and (canvas_diff < self.variables.config.pan_pixel_threshold):
            # we haven't moved far enough
            return

        x_diff = decimation*canvas_x_diff
        y_diff = decimation*canvas_y_diff

        # verify that the shift limits make sense
        y_diff = get_shift_limit(y_diff, full_y, image_bounds[0], image_bounds[2])
        x_diff = get_shift_limit(x_diff, full_x, image_bounds[1], image_bounds[3])

        new_image_bounds = list(image_bounds)
        new_image_bounds[0] += y_diff
        new_image_bounds[1] += x_diff
        new_image_bounds[2] += y_diff
        new_image_bounds[3] += x_diff

        # apply view to the new rectangle
        self.zoom_to_full_image_selection(new_image_bounds, decimation=decimation)  # ensure use of constant decimation
        image_bounds, decimation = self.get_image_extent()
        # update the anchor point to the current point
        self.variables.shape_drawing.anchor_point_xy = event.x, event.y
        return

    def _pan_finish(self, event):
        """
        A pan event.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        self._pan(event, check_distance=False)
        self.variables.shape_drawing.set_inactive()
        self.current_shape_id = None
        self.hide_shape(self.variables.zoom_rect.uid)  # this should never have been unhidden?

    def _select_closest_shape(self, event):
        """
        Shape selection method, based on the given mouse event. If successful,
        this sets the current_shape_id.

        Parameters
        ----------
        event

        Returns
        -------
        None|int
            The discovered shape id.
        """

        closest_shape_id = self.find_closest_shape(event.x, event.y)
        if closest_shape_id is not None:
            self.current_shape_id = closest_shape_id
        return closest_shape_id

    # image properties and manipulation
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

        pil_image = Image.fromarray(numpy_data)
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

        if self.variables.state.canvas_width == width_npix and \
                self.variables.state.canvas_height == height_npix:
            return  # nothing to be done.

        # this will trigger a resize event
        self.config(width=width_npix, height=height_npix)

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
        if image_coords is None or image_coords[0] == image_coords[2] or image_coords[1] == image_coords[3]:
            return None

        tmp_image_coords = list(image_coords)
        if image_coords[0] > image_coords[2]:
            tmp_image_coords[0] = image_coords[2]
            tmp_image_coords[2] = image_coords[0]
        if image_coords[1] > image_coords[3]:
            tmp_image_coords[1] = image_coords[3]
            tmp_image_coords[3] = image_coords[1]
        if decimation is None:
            decimation = self.variables.canvas_image_object.get_decimation_factor_from_full_image_rect(tmp_image_coords)
        tmp_image_coords = (int(tmp_image_coords[0]), int(tmp_image_coords[1]), int(tmp_image_coords[2]), int(tmp_image_coords[3]))
        image_data_in_rect = self.variables.canvas_image_object.get_decimated_image_data_in_full_image_rect(
            tmp_image_coords, decimation)
        return image_data_in_rect

    def zoom_to_canvas_selection(self, canvas_rect):
        """
        Zoom to the selection using canvas coordinates.

        Parameters
        ----------
        canvas_rect : Tuple|List

        Returns
        -------
        None
        """

        image_coords = self.variables.canvas_image_object.canvas_coords_to_full_image_yx(canvas_rect)
        self.zoom_to_full_image_selection(image_coords)

    def zoom_to_full_image_selection(self, image_rect, decimation=None):
        """
        Zoom to the selection using image coordinates. This should fit the entire
        given region.

        Parameters
        ----------
        image_rect : Tuple|List
        decimation : None|int
            The decimation to use. If not provided, then the appropriate decimation
            will be calculated.

        Returns
        -------
        None
        """

        # what is the aspect ratio of the zoom rectangle?
        zoom_height = image_rect[2] - image_rect[0]
        zoom_width = image_rect[3] - image_rect[1]
        if zoom_height < 0:
            temp_image_rect = image_rect.copy()
            temp_image_rect[0] = image_rect[2]
            temp_image_rect[2] = image_rect[0]
            zoom_height *= -1
            image_rect = temp_image_rect
        if zoom_width < 0:
            temp_image_rect = image_rect.copy()
            temp_image_rect[1] = image_rect[3]
            temp_image_rect[3] = image_rect[1]
            zoom_width *= -1
            image_rect = temp_image_rect

        # validate that our sizes make sense
        if zoom_width <= 0 or zoom_height <= 0:
            showinfo('Poorly defined zoom rectangle', message='Zoom rectangle {}. Aborting zoom.'.format(image_rect))
            return  # do nothing
        if zoom_height < self.variables.config.zoom_pixel_threshold or \
                zoom_width < self.variables.config.zoom_pixel_threshold:
            # do not perform this zoom
            return
        zoom_ratio = zoom_height/float(zoom_width)

        # what is the aspect ratio of the canvas?
        window_height = self.variables.canvas_image_object.canvas_ny
        window_width = self.variables.canvas_image_object.canvas_nx
        window_ratio = window_height/float(window_width)

        # craft an image rectangle containing the input rectangle, of the same ratio as the window rectangle
        if zoom_ratio >= window_ratio:
            # the zoom rectangle is taller than the window rectangle.
            # Keep the height, and extend the width
            image_rect = [image_rect[0], image_rect[1], image_rect[2], image_rect[1] + zoom_width*zoom_ratio/window_ratio]
        else:
            # the zoom rectangle is longer than the window rectangle
            # Keep the width, and expand the height
            image_rect = [image_rect[0], image_rect[1], image_rect[0] + zoom_height*window_ratio/zoom_ratio, image_rect[3]]

        # ensure that sensible limits apply
        if image_rect[0] < 0:
            image_rect[0] = 0
        if image_rect[1] < 0:
            image_rect[1] = 0
        if image_rect[2] > self.variables.canvas_image_object.image_reader.full_image_ny:
            image_rect[2] = self.variables.canvas_image_object.image_reader.full_image_ny
        if image_rect[3] > self.variables.canvas_image_object.image_reader.full_image_nx:
            image_rect[3] = self.variables.canvas_image_object.image_reader.full_image_nx

        self.variables.canvas_image_object.update_canvas_display_image_from_full_image_rect(image_rect, decimation=decimation)
        self.set_image_from_numpy_array(self.variables.canvas_image_object.display_image)
        self.redraw_all_shapes()
        self.emit_image_extent_changed()

    def update_current_image(self):
        """
        Updates the current image.

        Returns
        -------
        None
        """

        if self.variables.canvas_image_object is not None:
            rect = (0, 0, self.variables.state.canvas_width, self.variables.state.canvas_height)
            self.variables.canvas_image_object.update_canvas_display_image_from_canvas_rect(rect)
            self.set_image_from_numpy_array(self.variables.canvas_image_object.display_image)
            self.update()

    def _set_image_from_pil_image(self, pil_image):
        """
        Set image from a PIL image.

        Parameters
        ----------
        pil_image : Image

        Returns
        -------
        None
        """

        self.variables.tk_im = ImageTk.PhotoImage(pil_image)
        self.variables.image_id = self.create_image(0, 0, anchor="nw", image=self.variables.tk_im)
        self.tag_lower(self.variables.image_id)

    def save_full_canvas_as_image_file(self, output_fname):
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

        image_data = self.save_currently_displayed_canvas_to_numpy_array()
        pil_image = Image.fromarray(image_data)
        pil_image.save(output_fname)

    def save_currently_displayed_canvas_to_numpy_array(self):
        """
        Export the currently displayed canvas as a numpy array.

        This method exports a tkinter canvas to postscript, generates an oversampled
        image based on the postscript output, and then rescales the oversampled image to
        match the dimensions of the canvas displayed on the screen.
        This means that both image data and vector data that are displayed on an image
        canvas are rasterized to a numpy array. Tkinter accomplishes this by using
        ghostscript under the hood, so ghostscript must be installed as a dependency
        to use this method.

        Returns
        -------
        numpy.ndarray
        """

        ps = self.postscript(colormode='color')
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        scale = 4
        img.load(scale=scale)
        new_width = self.winfo_width()
        new_height = self.winfo_height()
        resized = img.resize((new_width, new_height), Image.BILINEAR)
        return numpy.array(resized)

    # shape analytics methods
    @staticmethod
    def _normalized_rectangle_coordinates(coords):
        """
        Common pattern for comparing an rectangle/ellipse bounds and event coordinates.

        Parameters
        ----------
        coords : Tuple

        Returns
        -------
        numpy.ndarray
            (upper left, upper right, lower right, lower left)
            upper left = minimum x, minimum y
            upper right = maximum x, minimum y
            lower right = maximum x, maximum y
            lower left = minumum x, maximum y
        """

        select_x1, select_y1, select_x2, select_y2 = coords

        xul = min(select_x1, select_x2)
        xlr = max(select_x1, select_x2)
        yul = min(select_y1, select_y2)
        ylr = max(select_y1, select_y2)

        the_coords = numpy.array([[xul, yul], [xlr, yul], [xlr, ylr], [xul, ylr]])
        return the_coords

    def find_distance_from_shape(self, shape_id, canvas_x, canvas_y):
        """
        Gets the distance between the given shape and point.

        Parameters
        ----------
        shape_id : int
        canvas_x : int|float
        canvas_y : int|float

        Returns
        -------
        float
        """

        geometry_obj = self.get_geometry_for_shape(shape_id, coordinate_type='canvas')
        if geometry_obj is None:
            return float('inf')
        return geometry_obj.get_minimum_distance((canvas_x, canvas_y))

    def find_closest_shape(self, canvas_x, canvas_y, min_threshold=None):
        """
        Finds the closest shape to the provided canvas coordinates, and returns its id.

        Parameters
        ----------
        canvas_x : float
        canvas_y : float
        min_threshold : None|float|int

        Returns
        -------
        int
        """

        return self.get_closest_shape_and_distance(canvas_x, canvas_y, min_threshold=min_threshold)[0]

    def get_closest_shape_and_distance(self, canvas_x, canvas_y, min_threshold=None):
        """
        Finds the closest shape to the provided canvas coordinates, and returns its id.

        Parameters
        ----------
        canvas_x : float
        canvas_y : float
        min_threshold : None|float|int

        Returns
        -------
        (int, float)
        """

        if min_threshold is None:
            min_threshold = self.variables.config.shape_selector_pixel_threshold

        closest_distance = float('inf')
        closest_id = None

        for shape_id in self.get_non_tool_shape_ids():
            the_distance = self.find_distance_from_shape(shape_id, canvas_x, canvas_y)
            if the_distance <= min_threshold:
                return shape_id, the_distance
            if the_distance < closest_distance:
                closest_distance = the_distance
                closest_id = shape_id
        return closest_id, closest_distance

    def get_canvas_line_length(self, line_id):
        """
        Gets the canvas line length.

        Parameters
        ----------
        line_id : int

        Returns
        -------
        float
        """

        the_line = self.get_geometry_for_shape(line_id, coordinate_type='canvas')
        if isinstance(the_line, LineString):
            return the_line.get_length()
        else:
            return None

    def get_image_line_length(self, line_id):
        """
        Gets the image line length.

        Parameters
        ----------
        line_id : int

        Returns
        -------
        float
        """

        canvas_line_length = self.get_canvas_line_length(line_id)
        if canvas_line_length is None:
            return None
        return canvas_line_length*self.variables.canvas_image_object.decimation_factor

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
        Tuple[int, float, int, int]
            The index of the nearest coordinate.
            The distance in canvas pixel units.
            The integer y canvas coordinate of the nearest vertex.
            The integer x canvas coordinate of the nearest vertex.
        """

        the_point = numpy.array([canvas_x, canvas_y])
        vector_object = self.get_vector_object(self.current_shape_id)
        coords = self.get_shape_canvas_coords(shape_id)
        if vector_object.type in [ShapeTypeConstants.RECT, ShapeTypeConstants.ELLIPSE]:
            # we may have to reformat the shape for the selection to make sense
            rect_coords = numpy.array(coords).reshape((2, 2))
            the_coords = self._normalized_rectangle_coordinates(coords)

            coords_diff = the_coords - the_point
            dists = numpy.sqrt(numpy.sum(coords_diff*coords_diff, axis=1))
            the_index = numpy.argmin(dists)
            closest = the_coords[the_index, :]

            if not (numpy.all(closest == rect_coords[0, :]) or numpy.all(closest == rect_coords[1, :])):
                # the rectangle definition involves one of the corners which is not selected, so switch
                ul = the_coords[0, :].tolist()
                ur = the_coords[1, :].tolist()
                lr = the_coords[2, :].tolist()
                ll = the_coords[3, :].tolist()

                if the_index == 0:  # upper left
                    self.modify_existing_shape_using_canvas_coords(self.current_shape_id, ul+lr)
                elif the_index == 1:  # upper right
                    self.modify_existing_shape_using_canvas_coords(self.current_shape_id, ur+ll)
                elif the_index == 2:  # lower right
                    self.modify_existing_shape_using_canvas_coords(self.current_shape_id, ul+lr)
                else:  # lower left
                    self.modify_existing_shape_using_canvas_coords(self.current_shape_id, ll+ur)
                coords = self.get_shape_canvas_coords(shape_id)

        the_coords = numpy.array(coords).reshape((-1, 2))
        coords_diff = the_coords - the_point
        dists = numpy.sqrt(numpy.sum(coords_diff*coords_diff, axis=1))
        min_ind = numpy.argmin(dists)
        the_index = int(min_ind)
        return the_index, float(dists[min_ind]), int(the_coords[min_ind, 0]), int(the_coords[min_ind, 1])

    # shape modification and manipulation methods
    def reinitialize_shapes(self):
        """
        Delete all non-tool shapes, hide all tool shapes.

        Returns
        -------
        None
        """

        if self.variables.canvas_image_object is None:
            return  # nothing to be done

        shape_ids = self.variables.shape_ids.copy()
        tool_shapes = self.get_tool_shape_ids()
        for shape_id in shape_ids:
            if shape_id in tool_shapes:
                self.hide_shape(shape_id)
            else:
                # noinspection PyBroadException
                try:
                    self.delete_shape(shape_id)
                except:
                    continue
        self.redraw_all_shapes()
        # reset the initial coordinates for zoom and select rectangles.
        self.modify_existing_shape_using_image_coords(self.variables.zoom_rect.uid, (0, 0, 0, 0))
        self.modify_existing_shape_using_image_coords(self.variables.select_rect.uid, (0, 0, 0, 0))

    def redraw_all_shapes(self):
        """
        Redraw all the shapes.

        Returns
        -------
        None
        """

        if self.variables.canvas_image_object is None:
            return  # nothing to be done

        for shape_id in self.variables.shape_ids:
            vector_object = self.get_vector_object(shape_id)
            if vector_object is None:
                continue
            pixel_coords = vector_object.image_coords
            if pixel_coords is None:
                continue
            new_canvas_coords = self.shape_image_coords_to_canvas_coords(shape_id)
            self.modify_existing_shape_using_canvas_coords(shape_id, new_canvas_coords, update_pixel_coords=False)

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

        if shape_id is None:
            return

        # noinspection PyBroadException
        try:
            self.itemconfigure(shape_id, state="hidden")
        except:
            pass

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

        if shape_id is None:
            return
        self.itemconfigure(shape_id, state="normal")

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

        vector_object = self.get_vector_object(shape_id)
        if vector_object is None:
            return
        shape_type = vector_object.type
        if shape_type in ShapeTypeConstants.geometric_shapes() and \
                shape_id not in self.get_tool_shape_ids():
            self.itemconfigure(shape_id, dash=(5, 5))

    def lowlight_existing_shape(self, shape_id):
        vector_object = self.get_vector_object(shape_id)
        if vector_object is None:
            return
        shape_type = vector_object.type
        if shape_type in ShapeTypeConstants.geometric_shapes() and \
                shape_id not in self.get_tool_shape_ids():
            self.itemconfigure(shape_id, dash=())

    def modify_existing_shape_using_canvas_coords(self, shape_id, new_coords, update_pixel_coords=True):
        """
        Modify the canvas coordinates of an existing shape.

        Parameters
        ----------
        shape_id : int
        new_coords : Tuple|List
        update_pixel_coords : bool
            Should be True if the definition of the underlying shape is being changed.
            Should be False if the shape is just being re-rendered, like after a zoom
            or pan operation.

        Returns
        -------
        None
        """

        def make_int(the_coords):
            return tuple(int(entry) for entry in the_coords)

        vector_object = self.get_vector_object(shape_id)
        if vector_object is None:
            return
        elif vector_object.type == ShapeTypeConstants.POINT:
            point_size = vector_object.point_size
            x1, y1 = (new_coords[0] - point_size), (new_coords[1] - point_size)
            x2, y2 = (new_coords[0] + point_size), (new_coords[1] + point_size)
            canvas_drawing_coords = make_int([x1, y1, x2, y2])
        else:
            canvas_drawing_coords = make_int(new_coords)

        # noinspection PyBroadException
        try:
            self.coords(shape_id, canvas_drawing_coords)
            if update_pixel_coords:
                self._set_shape_pixel_coords_from_canvas_coords(shape_id, new_coords)
        except:
            pass

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

        self._set_shape_pixel_coords(shape_id, image_coords)
        canvas_coords = self.image_coords_to_canvas_coords(image_coords)
        self.modify_existing_shape_using_canvas_coords(shape_id, canvas_coords, update_pixel_coords=False)

    def _trim_to_drag_limits(self, event_x, event_y, drag_lims):
        """
        Trim coordinates to the given drag limits.

        Parameters
        ----------
        event_x : int|float
        event_y : int|float
        drag_lims

        Returns
        -------
        float, float
        """

        def trim(value, l_bound, u_bound):
            if value < l_bound:
                return l_bound
            elif value > u_bound:
                return u_bound
            else:
                return value

        if drag_lims:
            canvas_lims = self.image_coords_to_canvas_coords(drag_lims)
            event_x = trim(event_x, canvas_lims[0], canvas_lims[2])
            event_y = trim(event_y, canvas_lims[1], canvas_lims[3])
        return event_x, event_y

    def _update_text_or_point_event(self, event):
        """
        Actions for updating text or point coordinates based on some mouse event. This implicitly
        assumes that the current shape is a point.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        self.modify_existing_shape_using_canvas_coords(self.current_shape_id, (event.x, event.y), update_pixel_coords=True)

    def _modify_coords(self, coords, event_x_pos, event_y_pos, insert=False):
        """
        Modify the present coordinate string for lines and polygons.

        Parameters
        ----------
        coords : List|Tuple
        event_x_pos : float
        event_y_pos : float
        insert : bool
            Insert the new point, or replace the current?

        Returns
        -------
        List
        """

        drag_lims = self.get_vector_object(self.current_shape_id).image_drag_limits
        event_x_pos, event_y_pos = self._trim_to_drag_limits(event_x_pos, event_y_pos, drag_lims)
        if insert:
            if 2*self.variables.shape_drawing.insert_at_index == len(coords) - 2:
                # it's the final coordinate
                out = list(coords) + [event_x_pos, event_y_pos]
            else:
                index_insert = 2*self.variables.shape_drawing.insert_at_index
                out = list(coords[:index_insert+2]) + [event_x_pos, event_y_pos] + list(coords[index_insert+2:])
            # increment insert_at_index
            self.variables.shape_drawing.insert_at_index += 1
            return out
        else:
            if self.variables.shape_drawing.insert_at_index == 0:
                return [event_x_pos, event_y_pos] + list(coords[2:])
            elif 2*self.variables.shape_drawing.insert_at_index == len(coords) - 2:
                return list(coords[:-2]) + [event_x_pos, event_y_pos]
            else:
                index_insert = 2 * self.variables.shape_drawing.insert_at_index
                return list(coords[:index_insert]) + [event_x_pos, event_y_pos] + list(coords[index_insert+2:])

    def _remove_current_coord(self):
        """
        Remove the present coordinate. This assumes that the corresponding shape is a
        line or polygon.

        Returns
        -------
        None
        """

        shape_id = self.current_shape_id
        if shape_id is None or not self.variables.shape_drawing.actively_drawing:
            return

        coords = self.get_shape_canvas_coords(shape_id)
        point_count = int(len(coords)/2)

        if point_count < 3:
            return

        index_remove = 2*self.variables.shape_drawing.insert_at_index
        if index_remove == 0:
            self.modify_existing_shape_using_canvas_coords(
                shape_id, coords[2:], update_pixel_coords=True)
        elif index_remove >= point_count:
            self.modify_existing_shape_using_canvas_coords(
                shape_id, coords[:-2], update_pixel_coords=True)
            self.variables.shape_drawing.insert_at_index = index_remove-1
        else:
            self.modify_existing_shape_using_canvas_coords(
                shape_id, coords[:index_remove] + coords[index_remove+2:], update_pixel_coords=True)
            self.variables.shape_drawing.insert_at_index = index_remove-1
        self.emit_shape_coords_finalized()

    def _update_arrow_event(self, event):
        """
        Actions for updating arrow coordinates based on some mouse event. This implicitly
        assumes that the current shape is an arrow (line segment).

        Parameters
        ----------
        event

        Returns
        -------
        None
        """


        if self.current_shape_id is None or \
                not self.variables.shape_drawing.actively_drawing:
            return

        if self.variables.shape_drawing.insert_at_index > 1:
            self.variables.shape_drawing.insert_at_index = 1
        if self.variables.shape_drawing.insert_at_index < 0:
            self.variables.shape_drawing.insert_at_index = 0
        event_x_pos = self.canvasx(event.x)
        event_y_pos = self.canvasy(event.y)
        old_coords = self.get_shape_canvas_coords(self.current_shape_id)
        new_coords = self._modify_coords(old_coords, event_x_pos, event_y_pos, insert=False)
        self.modify_existing_shape_using_canvas_coords(self.current_shape_id, new_coords, update_pixel_coords=True)

    def _update_line_event(self, event, insert=True):
        """
        Actions for updating line coordinates based on some mouse event.

        Parameters
        ----------
        event
        insert : bool
            Insert a new point at the current index, or modify the current point.

        Returns
        -------
        None
        """

        if self.current_shape_id is None or not self.variables.shape_drawing.actively_drawing:
            return

        event_x_pos = self.canvasx(event.x)
        event_y_pos = self.canvasy(event.y)
        old_coords = self.get_shape_canvas_coords(self.current_shape_id)
        new_coords = self._modify_coords(old_coords, event_x_pos, event_y_pos, insert=insert)
        self.modify_existing_shape_using_canvas_coords(self.current_shape_id, new_coords, update_pixel_coords=True)

    def _update_polygon_event(self, event, insert=True):
        """
        Click a polygon callback for editing the current polygon shape.
        This also emits <<ShapeCoordsFinalized>> event.

        Parameters
        ----------
        event
        insert : bool
            Insert a new point at the current index, or modify the current point.

        Returns
        -------
        None
        """

        if self.current_shape_id is None or not self.variables.shape_drawing.actively_drawing:
            return

        event_x_pos = self.canvasx(event.x)
        event_y_pos = self.canvasy(event.y)
        old_coords = self.get_shape_canvas_coords(self.current_shape_id)
        new_coords = self._modify_coords(old_coords, event_x_pos, event_y_pos, insert=insert)
        self.modify_existing_shape_using_canvas_coords(self.current_shape_id, new_coords, update_pixel_coords=True)
        self.emit_shape_coords_finalized()

    def _drag_zoom_rectangle(self, event):
        """
        Function for dragging the zoom rectangle.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        shape_id = self.variables.zoom_rect.uid
        event_x_pos = self.canvasx(event.x)
        event_y_pos = self.canvasy(event.y)
        new_coords = self.variables.shape_drawing.anchor_point_xy + (event_x_pos, event_y_pos)
        self.modify_existing_shape_using_canvas_coords(shape_id, new_coords, update_pixel_coords=True)

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
        vector_object.color = color
        if vector_object.type in [ShapeTypeConstants.RECT, ShapeTypeConstants.POLYGON]:
            self.itemconfigure(shape_id, outline=color)
        else:
            self.itemconfigure(shape_id, fill=color)

    def _set_shape_pixel_coords_from_canvas_coords(self, shape_id, coords):
        """
        Sets the shape pixel coordinates from the canvas coordinates. This only
        modifies the vector object, and does not update the tkinter canvas
        shape. This should not be used directly.

        Parameters
        ----------
        shape_id : int
        coords : Tuple|List

        Returns
        -------
        None
        """

        if self.variables.canvas_image_object is not None:
            image_coords = self.canvas_coords_to_image_coords(coords)
            self._set_shape_pixel_coords(shape_id, image_coords)

    def _set_shape_pixel_coords(self, shape_id, image_coords):
        """
        Set the pixel coordinates for the given shape. This only
        modifies the vector object, and does not update the tkinter canvas
        shape. This should not be used directly.

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
        self.emit_shape_coords_edit(vector_object.uid, vector_object.type)

    # shape creation/deletion methods
    def _track_shape(self, vector_object, make_current=True, is_tool=False):
        """
        Track the new shape.

        Parameters
        ----------
        vector_object : VectorObject
        make_current : bool
            Make this new object the current object?
        """

        self.variables.track_shape(vector_object)
        if not is_tool:
            self.emit_shape_create(vector_object.uid, vector_object.type)
        if make_current:
            self.current_shape_id = vector_object.uid

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

        if shape_id in self.get_tool_shape_ids():
            logging.error('Cannot delete shape {}, because it is associated with a tool'.format(shape_id))
            return

        the_vector = self.get_vector_object(shape_id)
        if the_vector is None:
            return # nothing to be done

        the_type = the_vector.type
        self.variables.shape_ids.remove(shape_id)
        del self.variables.vector_objects[shape_id]
        self.delete(shape_id)
        if shape_id == self.current_shape_id:
            self.current_shape_id = None
        self.emit_shape_delete(shape_id, the_type)

    def create_new_point(self, coords, make_current=True, increment_color=True, is_tool=False, color=None, **options):
        """
        Create a new point.

        Parameters
        ----------
        coords : Tuple|List
        make_current : bool
            Should the new shape be set as the current shape?
        increment_color : bool
            Increment the color after creating this object?
        is_tool : bool
            Is this a tool? No signal emitted, in that case.
        color : None|str
            The color.
        options
            Optional keyword arguments.

        Returns
        -------
        int
        """

        if 'fill' not in options:
            options['fill'] = self.variables.state.foreground_color

        x1, y1 = (coords[0] - self.variables.state.point_size), (coords[1] - self.variables.state.point_size)
        x2, y2 = (coords[0] + self.variables.state.point_size), (coords[1] + self.variables.state.point_size)
        shape_id = self.create_oval(x1, y1, x2, y2, **options)
        image_coords = self.canvas_coords_to_image_coords(coords)
        vector_obj = VectorObject(
            shape_id, ShapeTypeConstants.POINT,
            image_coords=image_coords, point_size=self.variables.state.point_size, color=color, **options)
        self._track_shape(vector_obj, make_current=make_current, is_tool=is_tool)

        if color is None and increment_color:
            self._increment_color()
        return shape_id

    def create_new_text(self, *args, make_current=True, increment_color=True, is_tool=False, color=None, **kwargs):
        """
        Create text with coordinates x1,y1.

        Parameters
        ----------
        args
        make_current : bool
            Should the new shape be set as the current shape?
        increment_color : bool
            Increment the foreground color?
        is_tool : bool
            Is this a tool? No signal emitted, in that case.
        color : None|str
            The color.
        kwargs
            The keyword arguments

        Returns
        -------
        int
        """

        shape_id = self._create('text', args, kwargs)
        self.variables.shape_ids.append(shape_id)
        canvas_coords = args[0]
        image_coords = self.canvas_coords_to_image_coords(canvas_coords)
        vector_obj = VectorObject(shape_id, ShapeTypeConstants.TEXT, image_coords=image_coords, color=color)
        self._track_shape(vector_obj, make_current=make_current, is_tool=is_tool)
        if make_current:
            self.current_shape_id = shape_id
        if color is None and increment_color:
            self._increment_color()
        return shape_id

    def create_new_rect(self, canvas_coords, make_current=True, increment_color=True, is_tool=False, color=None, **options):
        """
        Create a new rectangle.

        Parameters
        ----------
        canvas_coords : Tuple|List
        make_current : bool
            Should the new shape be set as the current shape?
        increment_color : bool
            Increment the foreground color?
        is_tool : bool
            Is this a tool? No signal emitted, in that case.
        color : None|str
            The color.
        options
            Optional Keyword arguments.

        Returns
        -------
        int
        """

        if 'outline' not in options:
            options['outline'] = self.variables.state.foreground_color
        if 'width' not in options:
            options['width'] = self.variables.state.rect_border_width
        shape_id = self.create_rectangle(*canvas_coords, **options)
        image_coords = self.canvas_coords_to_image_coords(canvas_coords)
        vector_obj = VectorObject(shape_id, ShapeTypeConstants.RECT, image_coords=image_coords, color=color, **options)
        self._track_shape(vector_obj, make_current=make_current, is_tool=is_tool)
        if make_current:
            self.current_shape_id = shape_id
        if color is None and increment_color:
            self._increment_color()
        return shape_id

    def create_new_ellipse(self, canvas_coords, make_current=True, increment_color=True, is_tool=False, color=None, **options):
        """
        Create a new rectangle.

        Parameters
        ----------
        canvas_coords : Tuple|List
        make_current : bool
            Should the new shape be set as the current shape?
        increment_color : bool
            Increment the foreground color?
        is_tool : bool
            Is this a tool? No signal emitted, in that case.
        color : None|str
            The color.
        options
            Optional Keyword arguments.

        Returns
        -------
        int
        """

        if 'outline' not in options:
            options['outline'] = self.variables.state.foreground_color
        if 'width' not in options:
            options['width'] = self.variables.state.rect_border_width
        shape_id = self.create_oval(*canvas_coords, **options)
        image_coords = self.canvas_coords_to_image_coords(canvas_coords)
        vector_obj = VectorObject(shape_id, ShapeTypeConstants.ELLIPSE, image_coords=image_coords, color=color, **options)
        self._track_shape(vector_obj, make_current=make_current, is_tool=is_tool)
        if make_current:
            self.current_shape_id = shape_id
        if color is None and increment_color:
            self._increment_color()
        return shape_id

    def create_new_line(self, coords, make_current=True, increment_color=True, is_tool=False, color=None, **options):
        """
        Create a new line.

        Parameters
        ----------
        coords : Tuple|List
        make_current : bool
            Should the new shape be set as the current shape?
        increment_color : bool
            Increment the foreground color?
        is_tool : bool
            Is this a tool? No signal emitted, in that case.
        color : None|str
            The color.
        options
            Optional keyword arguments.

        Returns
        -------
        int
        """

        if 'fill' not in options:
            options['fill'] = self.variables.state.foreground_color
        if 'width' not in options:
            options['width'] = self.variables.state.line_width

        shape_id = self.create_line(*coords, **options)
        image_coords = self.canvas_coords_to_image_coords(coords)
        vector_obj = VectorObject(shape_id, ShapeTypeConstants.LINE, image_coords=image_coords, color=color, **options)
        self._track_shape(vector_obj, make_current=make_current, is_tool=is_tool)
        if make_current:
            self.current_shape_id = shape_id
        if color is None and increment_color:
            self._increment_color()
        return shape_id

    def create_new_arrow(self, coords, make_current=True, increment_color=True, is_tool=False, color=None, **options):
        """
        Create a new arrow.

        Parameters
        ----------
        coords : Tuple|List
        make_current : bool
            Should the new shape be set as the current shape?
        increment_color : bool
            Increment the foreground color?
        is_tool : bool
            Is this a tool? No signal emitted, in that case.
        color : None|str
            The color.
        options
            Optional keyword arguments.

        Returns
        -------
        int
        """

        if 'fill' not in options:
            options['fill'] = self.variables.state.foreground_color
        if 'width' not in options:
            options['width'] = self.variables.state.line_width
        if 'arrow' not in options:
            options['arrow'] = tkinter.LAST

        shape_id = self.create_line(*coords, **options)
        image_coords = self.canvas_coords_to_image_coords(coords)
        vector_obj = VectorObject(shape_id, ShapeTypeConstants.ARROW, image_coords=image_coords, color=color, **options)
        self._track_shape(vector_obj, make_current=make_current, is_tool=is_tool)
        if make_current:
            self.current_shape_id = shape_id
        if color is None and increment_color:
            self._increment_color()
        return shape_id

    def create_new_polygon(self, coords, make_current=True, increment_color=True, is_tool=False, color=None, **options):
        """
        Create a new polygon.

        Parameters
        ----------
        coords : Tuple|List
        make_current : bool
            Should the new shape be set as the current shape?
        increment_color : bool
            Increment the foreground color?
        is_tool : bool
            Is this a tool? No signal emitted, in that case.
        color : None|str
            The color.
        options
            Optional keyword arguments.

        Returns
        -------
        int
        """

        if 'outline' not in options:
            options['outline'] = self.variables.state.foreground_color
        if 'width' not in options:
            options['width'] = self.variables.state.poly_border_width
        if 'fill' not in options:
            options['fill'] = ''

        shape_id = self.create_polygon(*coords, **options)
        image_coords = self.canvas_coords_to_image_coords(coords)
        vector_obj = VectorObject(shape_id, ShapeTypeConstants.POLYGON, image_coords=image_coords, color=color, **options)
        self._track_shape(vector_obj, make_current=make_current, is_tool=is_tool)
        if make_current:
            self.current_shape_id = shape_id
        if color is None and increment_color:
            self._increment_color()
        return shape_id

    # shape as geometry methods
    def get_geometry_for_shape(self, shape_id, coordinate_type='image'):
        """
        Get the geometry version of the given shape in either image or canvas
        coordinates.

        Parameters
        ----------
        shape_id : int
        coordinate_type : str
            Either "image" or "canvas". Not case-sensitive.

        Returns
        -------
        GeometryObject
        """

        vector_object = self.get_vector_object(shape_id)
        if coordinate_type.lower() == 'canvas':
            coords = self.get_shape_canvas_coords(shape_id)
        else:
            coords = self.get_shape_image_coords(shape_id)
        coords_array = numpy.array(coords, dtype='float64').reshape((-1, 2))

        if vector_object.type == ShapeTypeConstants.TEXT:
            return Point(coordinates=coords_array[0, :])
        elif vector_object.type == ShapeTypeConstants.POINT:
            return Point(coordinates=coords_array[0, :])
        elif vector_object.type == ShapeTypeConstants.RECT:
            rect_coords = numpy.zeros((4, 2), dtype='float64')
            rect_coords[0, :] = coords_array[0, :]
            rect_coords[1, :] = [coords_array[0, 0], coords_array[1, 1]]
            rect_coords[2, :] = coords_array[1, :]
            rect_coords[3, :] = [coords_array[1, 0], coords_array[0, 1]]
            return LinearRing(coordinates=rect_coords)
        elif vector_object.type == ShapeTypeConstants.ELLIPSE:
            mid_point = 0.5*(coords_array[0, :] + coords_array[1, :])
            r_0 = 0.5*numpy.abs(coords_array[1, 0] - coords_array[0, 0])
            r_1 = 0.5*numpy.abs(coords_array[1, 1] - coords_array[0, 1])
            pts = 60
            theta = numpy.linspace(0, 2*numpy.pi, pts)
            ellipse_coords = numpy.zeros((pts, 2), dtype='float64')
            ellipse_coords[:, 0] = mid_point[0] + r_0*numpy.cos(theta)
            ellipse_coords[:, 1] = mid_point[1] + r_1*numpy.sin(theta)
            return LinearRing(coordinates=ellipse_coords)
        elif vector_object.type in [ShapeTypeConstants.LINE, ShapeTypeConstants.ARROW]:
            return LineString(coordinates=coords_array)
        elif vector_object.type == ShapeTypeConstants.POLYGON:
            return LinearRing(coordinates=coords_array)
        else:
            raise ValueError('Unhandled geometry type {} for conversion from tkinter to sarpy geometry type')

    # shape coordinate methods
    def canvas_coords_to_image_coords(self, canvas_coords):
        """
        Converts the canvas coordinates to image coordinates.

        Parameters
        ----------
        canvas_coords : Tuple|List

        Returns
        -------
        Tuple
        """

        if self.variables.canvas_image_object is None:
            return canvas_coords

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

    # set tool methods
    def set_tool(self, tool):
        """
        Sets the image canvas current tool. This should be in keeping with the ToolConstants
        class in "image_canvas.py".

        Parameters
        ----------
        tool : int|str
            The string name or integer enum value for the tool.

        Returns
        -------
        None
        """

        value = ToolConstants.validate(tool)
        if tool is not None and value is None:
            logging.error('Got nonsense tool value {}'.format(tool))

        if value is None or value == ToolConstants.VIEW:
            self.set_current_tool_to_view()
        elif value == ToolConstants.ZOOM_IN:
            self.set_current_tool_to_zoom_in()
        elif value == ToolConstants.ZOOM_OUT:
            self.set_current_tool_to_zoom_out()
        elif value == ToolConstants.SELECT:
            self.set_current_tool_to_select()
        elif value == ToolConstants.PAN:
            self.set_current_tool_to_pan()
        elif value == ToolConstants.SELECT_CLOSEST_SHAPE:
            self.set_current_tool_to_select_closest_shape()
        elif value == ToolConstants.NEW_SHAPE:
            self.set_current_tool_to_new_shape()
        elif value == ToolConstants.EDIT_SHAPE:
            self.set_current_tool_to_edit_shape()
        elif value == ToolConstants.SHIFT_SHAPE:
            self.set_current_tool_to_shift_shape()
        else:
            raise ValueError('Unhandled case ToolConstants.{}'.format(ToolConstants.get_name(value)))

    def _set_current_and_active_tool(self, tool):
        """
        Sets the current and active tool.

        Parameters
        ----------
        tool : int
        """

        self.current_tool = tool
        self.active_tool = tool

    def set_current_tool_to_view(self):
        """
        Sets the current tool to view (default).

        Returns
        -------
        None
        """

        self._set_current_and_active_tool(ToolConstants.VIEW)

    def set_current_tool_to_zoom_in(self):
        """
        Sets the current tool to zoom in.

        Returns
        -------
        None
        """

        self.current_shape_id = self.variables.zoom_rect.uid
        self._set_current_and_active_tool(ToolConstants.ZOOM_IN)

    def set_current_tool_to_zoom_out(self):
        """
        Sets the current tool to zoom out.

        Returns
        -------
        None
        """

        self.current_shape_id = self.variables.zoom_rect.uid
        self._set_current_and_active_tool(ToolConstants.ZOOM_OUT)

    def set_current_tool_to_select(self):
        """
        Sets the current tool to the selection tool.

        Returns
        -------
        None
        """

        self.current_shape_id = self.variables.select_rect.uid
        self.show_shape(self.variables.select_rect.uid)
        self._set_current_and_active_tool(ToolConstants.SELECT)

    def set_current_tool_to_pan(self):
        """
        Sets the current tool to pan.

        Returns
        -------
        None
        """

        self.current_shape_id = self.variables.zoom_rect.uid
        self._set_current_and_active_tool(ToolConstants.PAN)

    def set_current_tool_to_select_closest_shape(self):
        """
        Sets the tool to the closest shape.

        Returns
        -------
        None
        """

        self._set_current_and_active_tool(ToolConstants.SELECT_CLOSEST_SHAPE)

    def set_current_tool_to_shift_shape(self):
        """
        Sets the tool to shifting a shape.

        Returns
        -------
        None
        """

        self.current_shape_id = None
        self._set_current_and_active_tool(ToolConstants.SHIFT_SHAPE)

    def set_current_tool_to_new_shape(self, shape_type=None):
        """
        Sets the current tool to new shape of the type given. If shape_type is given
        the value of property `new_shape_type` is set to this value. Otherwise,
        the type of shape to create is determined by `new_shape_type`.

        Parameters
        ----------
        shape_type : None|int|str

        Returns
        -------
        None
        """

        self.current_shape_id = None
        if shape_type is not None:
            self.new_shape_type = shape_type
        self._set_current_and_active_tool(ToolConstants.NEW_SHAPE)

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

        self.new_shape_type = ShapeTypeConstants.POINT
        self.set_tool_to_new_or_edit_shape(point_id)

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

        self.new_shape_type = ShapeTypeConstants.RECT
        self.set_tool_to_new_or_edit_shape(rect_id)

    def set_current_tool_to_draw_ellipse(self, ellipse_id=None):
        """
        Sets the current tool to draw rectangle.

        Parameters
        ----------
        ellipse_id : int|None

        Returns
        -------
        None
        """

        self.new_shape_type = ShapeTypeConstants.ELLIPSE
        self.set_tool_to_new_or_edit_shape(ellipse_id)

    def set_current_tool_to_draw_line(self, line_id=None):
        """
        Sets the current tool to draw line by clicking.

        Parameters
        ----------
        line_id : None|int

        Returns
        -------
        None
        """

        self.new_shape_type = ShapeTypeConstants.LINE
        self.set_tool_to_new_or_edit_shape(line_id)

    def set_current_tool_to_draw_arrow(self, arrow_id=None):
        """
        Sets the current tool to draw arrow by dragging.

        Parameters
        ----------
        arrow_id : None|int

        Returns
        -------
        None
        """

        self.new_shape_type = ShapeTypeConstants.ARROW
        self.set_tool_to_new_or_edit_shape(arrow_id)

    def set_current_tool_to_draw_polygon(self, polygon_id=None):
        """
        Sets the current tool to draw polygon by clicking.

        Parameters
        ----------
        polygon_id : None|int

        Returns
        -------
        None
        """

        self.new_shape_type = ShapeTypeConstants.POLYGON
        self.set_tool_to_new_or_edit_shape(polygon_id)

    def set_current_tool_to_edit_shape(self, shape_id=None):
        """
        Sets the current tool to edit shape.

        Returns
        -------
        None
        """

        self._set_current_and_active_tool(ToolConstants.EDIT_SHAPE)
        if shape_id is not None:
            self.current_shape_id = shape_id

    def set_tool_to_new_or_edit_shape(self, shape_id=None):
        """
        If shape_id is None, this sets the current tool to new shape. If shape_id
        is not None, this sets the current tool to edit shape.

        Parameters
        ----------
        shape_id : None|int

        Returns
        -------
        None
        """

        if shape_id is None:
            self.current_shape_id = None
            self._set_current_and_active_tool(ToolConstants.NEW_SHAPE)
        else:
            self.show_shape(shape_id)
            self.set_current_tool_to_edit_shape(shape_id)

    def set_select_initial_state(self, anchor):
        """
        Set the initial state for select too for the given anchor point.

        Parameters
        ----------
        anchor : tuple
        """

        self.variables.shape_drawing.set_active(insert_at_index=1, anchor_point_xy=anchor)
        self.variables.shape_drawing.tmp_anchor_point_xy = anchor
        self.show_shape(self.variables.select_rect.uid)
        self.active_tool = ToolConstants.EDIT_SHAPE

    # custom event creation methods
    def emit_coordinate_changed(self, event):
        """
        Emits the <<CoordinateChanged>> event. This passes through the x and y
        canvas coordinates.

        Parameters
        ----------
        event
        """

        self.event_generate('<<CoordinateChanged>>', x=event.x, y=event.y)

    def emit_shape_create(self, shape_id, shape_type):
        """
        Emit the <<ShapeCreate>> event. This will be emitted after the shape has been created.

        Parameters
        ----------
        shape_id : int
        shape_type : int
        """

        if shape_id is None:
            return
        self.event_generate('<<ShapeCreate>>', x=shape_id, y=shape_type)

    def emit_shape_delete(self, shape_id, shape_type):
        """
        Emit the <<ShapeDelete>> event. This will be emitted after the shape has been
        deleted.

        Parameters
        ----------
        shape_id : int
        shape_type : int
        """

        if shape_id is None:
            return
        self.event_generate('<<ShapeDelete>>', x=shape_id, y=shape_type)

    def emit_shape_select(self, shape_id, shape_type):
        """
        Emit the <<ShapeSelect>> event. This will be emitted after the shape has been
        selected.

        Parameters
        ----------
        shape_id : int
        shape_type : int
        """

        if shape_id is None or shape_id in self.get_tool_shape_ids():
            return
        self.event_generate('<<ShapeSelect>>', x=shape_id, y=shape_type)

    def emit_shape_deselect(self, shape_id, shape_type):
        """
        Emit the <<ShapeDeselect>> event. This will be emitted after the shape has been
        deselected.

        Parameters
        ----------
        shape_id : int
        shape_type : int
        """

        if shape_id is None or shape_id in self.get_tool_shape_ids():
            return
        self.event_generate('<<ShapeDeselect>>', x=shape_id, y=shape_type)

    def emit_shape_coords_edit(self, shape_id, shape_type):
        """
        Emit the <<ShapeCoordsEdit>> or <<SelectionChanged>> event. This will be emitted
        after the shape has been edited.

        Parameters
        ----------
        shape_id : int
        shape_type : int
        """

        if shape_id is None:
            return
        elif shape_id == self.variables.select_rect.uid:
            self.event_generate('<<SelectionChanged>>', x=shape_id, y=shape_type)
        elif shape_id not in self.get_tool_shape_ids():
            self.event_generate('<<ShapeCoordsEdit>>', x=shape_id, y=shape_type)

    def emit_select_finalized(self):
        """
        Emit the <<SelectionFinalized>> event. This will be emitted
        after the shape has been edited.
        """

        self.event_generate('<<SelectionFinalized>>')

    def emit_shape_coords_finalized(self):
        """
        Emits the <<ShapeCoordsFinalized>> event, indicating that the current
        editing step for the current shape is finished (i.e. not being dragged).
        """

        vector_object = self.get_current_vector_object()
        if vector_object is None or vector_object.uid in self.get_tool_shape_ids():
            return
        self.event_generate('<<ShapeCoordsFinalized>>', x=vector_object.uid, y=vector_object.type)

    def emit_current_tool_changed(self):
        """
        Emits the <<CurrentToolChanged>> event, after the tool has changed.
        """

        self.event_generate('<<CurrentToolChanged>>')

    def emit_new_shape_type_changed(self):
        """
        Emits the <<ShapeTypeChanged>> event, after the new shape type has changed.
        """

        self.event_generate('<<ShapeTypeChanged>>')

    def emit_remap_changed(self):
        """
        Emits the <<RemapChanged>> event, after the remap value has been changed.
        Note that the new image index can be determined from the `get_current_remap()`
        method.
        """

        self.event_generate('<<RemapChanged>>')

    def emit_image_index_changed(self):
        """
        Emits the <<ImageIndexChanged>> event, after the index value has changed.
        Note that the new image index can be determined from the `get_image_index()`
        method.
        """

        self.event_generate('<<ImageIndexChanged>>')

    def emit_image_extent_changed(self):
        """
        Emit the <<ImageExtentChanged>> event, after the image extent has changed.
        Note that the new image extent can be determine from the `get_image_extent()`
        method.
        """

        self.event_generate('<<ImageExtentChanged>>')
