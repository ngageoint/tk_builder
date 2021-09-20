"""
Establishes the basic structure for an image canvas tool.
"""

__classification__ = "UNCLASSIFIED"
__author__ = "Thomas McCullough"


import logging
from collections import OrderedDict
import numpy
from typing import Tuple, List

from sarpy.compliance import string_types
from sarpy.geometry.geometry_elements import LinearRing


logger = logging.getLogger(__name__)
_DEFAULTS_REGISTERED = False
_TOOL_DICT = OrderedDict()
_CURRENT_ENUM_VALUE = -1
_TOOL_NAME_TO_ENUM = OrderedDict()
_TOOL_ENUM_TO_NAME = OrderedDict()


############
# helper class and methods

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
    _values_to_names = {value: key for key, value in _names_to_values.items()}

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


def normalized_rectangle_coordinates(coords):
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


def _get_canvas_event_coords(image_canvas, event):
    """
    Gets the event coordinates in image canvas coordinates.

    Parameters
    ----------
    image_canvas : tk_builder.widgets.image_canvas.ImageCanvas
    event
        The tkinter mouse event, expected to have .x and .y populated.

    Returns
    -------
    Tuple
    """

    return image_canvas.canvasx(event.x), image_canvas.canvasy(event.y)


def _modify_coords(image_canvas, shape_id, coords, event_x_pos, event_y_pos, at_index, insert=False):
    """
    Modify the coordinates for lines/polygons.

    Parameters
    ----------
    image_canvas : tk_builder.widgets.image_canvas.ImageCanvas
    shape_id : int
    coords : List|Tuple
    event_x_pos : float
    event_y_pos : float
    at_index : int
        The index at which to insert or replace
    insert : bool
        Insert a new point, or replace?

    Returns
    -------
    (list, int)
        The new coordinates and update index.
    """

    def trim_to_drag_limits(event_x, event_y):
        """
        Trim coordinates to the given drag limits.

        Parameters
        ----------
        event_x : int|float
        event_y : int|float

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
            canvas_lims = image_canvas.image_coords_to_canvas_coords(drag_lims)
            event_x = trim(event_x, canvas_lims[0], canvas_lims[2])
            event_y = trim(event_y, canvas_lims[1], canvas_lims[3])
        return event_x, event_y

    drag_lims = image_canvas.get_vector_object(shape_id).image_drag_limits
    event_x_pos, event_y_pos = trim_to_drag_limits(event_x_pos, event_y_pos)
    if insert:
        if 2*at_index == len(coords) - 2:
            # it's the final coordinate
            out = list(coords) + [event_x_pos, event_y_pos]
        else:
            index_insert = 2*at_index
            out = list(coords[:index_insert + 2]) + [event_x_pos, event_y_pos] + list(coords[index_insert + 2:])
        # increment insert_at_index
        at_index += 1
        return out, at_index
    else:
        if at_index == 0:
            out = [event_x_pos, event_y_pos] + list(coords[2:])
        elif 2*at_index == len(coords) - 2:
            out = list(coords[:-2]) + [event_x_pos, event_y_pos]
        else:
            index_insert = 2*at_index
            out = list(coords[:index_insert]) + [event_x_pos, event_y_pos] + list(coords[index_insert + 2:])
        return out, at_index


def _shift_shape_coords(canvas_event, anchor, coords, canvas_limits):
    """
    Helper function. Define new coordinates based on the given shift.

    Parameters
    ----------
    canvas_event
        The tkinter mouse event x/y in canvas coordinates
    anchor : Tuple
        The anchor point
    coords : Tuple
        The canvas coordinate array
    canvas_limits : None|Tuple
        The canvas limits, in canvas coordinates

    Returns
    -------
    numpy.ndarray
    """

    x_dist = canvas_event[0] - anchor[0]
    y_dist = canvas_event[1] - anchor[1]
    new_coords = numpy.asarray(coords) + x_dist
    new_coords_y = numpy.asarray(coords) + y_dist
    new_coords[1::2] = new_coords_y[1::2]
    if canvas_limits is not None:
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
            new_coords[0::2] = coords[0::2]
        if not within_y_limits:
            new_coords[1::2] = coords[1::2]
    return new_coords


def _perform_shape_shift(image_canvas, shape_id, canvas_event, anchor, emit=True):
    """
    Helper function to actually perform the shape shift operation.

    Parameters
    ----------
    image_canvas : tk_builder.widgets.image_canvas.ImageCanvas
    shape_id : int
        The shape id, with respect to the image canvas.
    canvas_event : tuple
        The event coordinates wrt the image canvas.
    anchor : tuple
        The anchor coordinates wrt the image canvas.
    emit : bool
        Emit the signal, via the image canvas, that the shape has been updated?
    """

    vector_object = image_canvas.get_vector_object(shape_id)
    if vector_object.image_drag_limits is not None:
        canvas_limits = image_canvas.image_coords_to_canvas_coords(
            vector_object.image_drag_limits)
    else:
        canvas_limits = None
    new_coords = _shift_shape_coords(
        canvas_event, anchor,
        image_canvas.get_shape_canvas_coords(shape_id), canvas_limits)
    image_canvas.modify_existing_shape_using_canvas_coords(shape_id, new_coords, emit=emit)


############
# abstract object

class ImageCanvasTool(object):
    """
    The basic structure for an image canvas tool. This should handle and implement
    the specifics of the behavior for the basic GUI actions.
    """

    _name = 'ImageCanvasTool'
    _mode = "normal"
    _mode_values = {"normal", }  # the allowed mode values

    def __init__(self, image_canvas):
        """

        Parameters
        ----------
        image_canvas : tk_builder.widgets.image_canvas.ImageCanvas
        """

        self.image_canvas = image_canvas

    @property
    def name(self):
        """
        str: The (read only) tool name.
        """

        return self._name

    @property
    def mode(self):
        """
        str: The mode
        """

        return self._mode

    @mode.setter
    def mode(self, value):
        if self._mode == value:
            return

        if not isinstance(value, string_types):
            raise TypeError('string value required')
        value = value.lower()

        if value not in self._mode_values:
            raise ValueError('Got disallowed value `{}`'.format(value))
        self._mode = value

    def initialize_tool(self):
        """
        This should be executed as an step step for this tool (as the tool gets set).
        """

        pass

    def finalize_tool(self):
        """
        This should be executed as a final step for this tool.
        """

        pass

    def on_left_mouse_click(self, event):
        """
        Handle the event pass through behavior.
        
        Parameters
        ----------
        event
            the tkinter event
        """
        
        pass

    def on_right_mouse_click(self, event):
        """
        Handle the event pass through behavior.
        
        Parameters
        ----------
        event
            the tkinter event
        """
        
        pass

    def on_left_mouse_double_click(self, event):
        """
        Handle the event pass through behavior.

        Parameters
        ----------
        event
            the tkinter event
        """

        pass

    def on_right_mouse_double_click(self, event):
        """
        Handle the event pass through behavior.
        
        Parameters
        ----------
        event
            the tkinter event
        """
        
        pass

    def on_left_mouse_release(self, event):
        """
        Handle the event pass through behavior.
        
        Parameters
        ----------
        event
            the tkinter event
        """
        
        pass

    def on_right_mouse_release(self, event):
        """
        Handle the event pass through behavior.
        
        Parameters
        ----------
        event
            the tkinter event
        """
        
        pass

    def on_mouse_motion(self, event):
        """
        Handle the event pass through behavior.
        
        Parameters
        ----------
        event
            the tkinter event
        """
        
        pass

    def on_left_mouse_motion(self, event):
        """
        Handle the event pass through behavior.
        
        Parameters
        ----------
        event
            the tkinter event
        """
        
        pass

    def on_right_mouse_motion(self, event):
        """
        Handle the event pass through behavior.
        
        Parameters
        ----------
        event
            the tkinter event
        """
        
        pass

    def on_mouse_wheel(self, event):
        """
        Handle the event pass through behavior.
        
        Parameters
        ----------
        event
            the tkinter event
        """
        
        pass

    def on_shift_mouse_wheel(self, event):
        """
        Handle the event pass through behavior.

        Parameters
        ----------
        event
            the tkinter event
        """

        pass

    def on_mouse_enter(self, event):
        """
        Handle the event pass through behavior.
        
        Parameters
        ----------
        event
            the tkinter event
        """
        
        pass

    def on_mouse_leave(self, event):
        """
        Handle the event pass through behavior.
        
        Parameters
        ----------
        event
            the tkinter event
        """
        
        pass


###########
# concrete implementations

class _ZoomTool(ImageCanvasTool):
    """Helper class not meant to instantiated except by extension."""
    _name = "_ZoomTool"

    def __init__(self, image_canvas):
        ImageCanvasTool.__init__(self, image_canvas)
        self.shape_id = self.image_canvas.variables.zoom_rect.uid
        self.size_threshold = self.image_canvas.variables.config.zoom_box_size_threshold
        self.anchor = (0, 0)
        self.rect_coords = (0, 0, 0, 0)
        self.mouse_moved = False

    def initialize_tool(self):
        self.shape_id = self.image_canvas.variables.zoom_rect.uid
        self.size_threshold = self.image_canvas.variables.config.zoom_box_size_threshold
        self.anchor = (0, 0)
        self.rect_coords = (0, 0, 0, 0)
        self.mouse_moved = False

    def finalize_tool(self):
        self.image_canvas.hide_shape(self.shape_id)
        self.image_canvas.modify_existing_shape_using_canvas_coords(self.shape_id, (0, 0, 0, 0))

    def on_left_mouse_click(self, event):
        self.mouse_moved = False
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        self.image_canvas.modify_existing_shape_using_canvas_coords(
            self.shape_id, canvas_event + canvas_event)
        self.anchor = canvas_event
        self.image_canvas.show_shape(self.shape_id)

    def on_left_mouse_motion(self, event):
        self.mouse_moved = True
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        new_coords = self.anchor + canvas_event
        self.image_canvas.modify_existing_shape_using_canvas_coords(
            self.shape_id, new_coords, update_pixel_coords=True)

    def on_left_mouse_release(self, event):
        if self.mouse_moved:
            self.rect_coords = self.image_canvas.coords(self.shape_id)
            self.image_canvas.hide_shape(self.shape_id)
            self.image_canvas.modify_existing_shape_using_canvas_coords(
                self.shape_id, (0, 0, 0, 0))
        # NB: mouse moved state change handled in extension

    def _check_size_threshold(self):
        x_diff = abs(self.rect_coords[0] - self.rect_coords[2])
        y_diff = abs(self.rect_coords[1] - self.rect_coords[3])
        return (x_diff >= self.size_threshold) and (y_diff >= self.size_threshold)


class ZoomInTool(_ZoomTool):
    _name = 'ZOOM_IN'

    def on_left_mouse_release(self, event):
        _ZoomTool.on_left_mouse_release(self, event)
        if self.mouse_moved and self._check_size_threshold():
            self.image_canvas.zoom_to_canvas_selection(self.rect_coords)
        self.mouse_moved = False


class ZoomOutTool(_ZoomTool):
    _name = 'ZOOM_OUT'

    def on_left_mouse_release(self, event):
        _ZoomTool.on_left_mouse_release(self, event)
        if self.mouse_moved and self._check_size_threshold():
            x1 = -self.rect_coords[0]
            x2 = self.image_canvas.variables.state.canvas_width + self.rect_coords[2]
            y1 = -self.rect_coords[1]
            y2 = self.image_canvas.variables.state.canvas_height + self.rect_coords[3]
            zoom_rect = (x1, y1, x2, y2)
            self.image_canvas.zoom_to_canvas_selection(zoom_rect)
        self.mouse_moved = False


class PanTool(ImageCanvasTool):
    """
    Basic pan tool
    """
    _name = 'PAN'

    def __init__(self, image_canvas):
        ImageCanvasTool.__init__(self, image_canvas)
        self.anchor = (0, 0)
        self.threshold = self.image_canvas.variables.config.pan_pixel_threshold

    def initialize_tool(self):
        self.anchor = (0, 0)
        self.threshold = self.image_canvas.variables.config.pan_pixel_threshold

    def on_left_mouse_click(self, event):
        self.anchor = _get_canvas_event_coords(self.image_canvas, event)

    def pan(self, event, check_distance=True):
        def get_shift_limit(the_shift, the_limit, lower_value, upper_value):
            if lower_value < 0 or upper_value > the_limit:
                raise ValueError('This is not sensible.')

            if the_shift < 0:
                return max(the_shift, -lower_value)
            else:
                return min(the_shift, the_limit - upper_value)

        # get the current image bounds
        image_bounds, decimation = self.image_canvas.get_image_extent()
        # get the full image size
        full_y = self.image_canvas.variables.canvas_image_object.image_reader.full_image_ny
        full_x = self.image_canvas.variables.canvas_image_object.image_reader.full_image_nx

        # determine how to modify the current image bounds
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        canvas_x_diff = self.anchor[0] - canvas_event[0]
        canvas_y_diff = self.anchor[1] - canvas_event[1]
        canvas_diff = (canvas_x_diff * canvas_x_diff + canvas_y_diff * canvas_y_diff) ** 0.5

        if check_distance and canvas_diff < self.threshold:
            # we haven't moved far enough
            return

        x_diff = decimation * canvas_x_diff
        y_diff = decimation * canvas_y_diff

        # verify that the shift limits make sense
        y_diff = get_shift_limit(y_diff, full_y, image_bounds[0], image_bounds[2])
        x_diff = get_shift_limit(x_diff, full_x, image_bounds[1], image_bounds[3])

        new_image_bounds = list(image_bounds)
        new_image_bounds[0] += y_diff
        new_image_bounds[1] += x_diff
        new_image_bounds[2] += y_diff
        new_image_bounds[3] += x_diff

        # apply view to the new rectangle
        self.image_canvas.zoom_to_full_image_selection(
            new_image_bounds, decimation=decimation)  # ensure use of constant decimation

        # update the anchor point to the current point
        self.anchor = canvas_event

    def on_left_mouse_motion(self, event):
        self.pan(event, check_distance=True)

    def on_left_mouse_release(self, event):
        self.pan(event, check_distance=False)


class SelectTool(ImageCanvasTool):
    _name = 'SELECT'
    _mode_values = {"normal", "edit", "shift"}

    def __init__(self, image_canvas):
        self._cursors = ["top_left_corner", "top_right_corner", "bottom_right_corner", "bottom_left_corner"]
        ImageCanvasTool.__init__(self, image_canvas)
        self.size_threshold = self.image_canvas.variables.config.select_size_threshold
        self.vertex_threshold = self.image_canvas.variables.config.vertex_selector_pixel_threshold
        self.anchor = (0, 0)
        self.shape_id = self.image_canvas.variables.select_rect.uid
        self.vector_object = None
        self.mouse_moved = False

    def initialize_tool(self):
        self.mode = "normal"
        self.shape_id = self.image_canvas.variables.select_rect.uid
        self.image_canvas.show_shape(self.shape_id)
        self.vector_object = self.image_canvas.get_vector_object(self.shape_id)
        self.size_threshold = self.image_canvas.variables.config.select_size_threshold
        self.vertex_threshold = self.image_canvas.variables.config.vertex_selector_pixel_threshold
        self.anchor = (0, 0)
        self.mouse_moved = False

    def finalize_tool(self):
        self.image_canvas.hide_shape(self.shape_id)

    def _perform_shift(self, canvas_event, emit=True):
        _perform_shape_shift(
            self.image_canvas, self.shape_id, canvas_event, self.anchor, emit=False)
        self.anchor = canvas_event
        if emit:
            self.image_canvas.emit_select_changed()

    def _perform_edit(self, canvas_event, emit=True):
        new_coords = [canvas_event[0], canvas_event[1], self.anchor[0], self.anchor[1]]
        self.image_canvas.modify_existing_shape_using_canvas_coords(self.shape_id, new_coords, emit=False)
        if emit:
            self.image_canvas.emit_select_changed()

    def on_left_mouse_click(self, event):
        self.mouse_moved = False
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        if self.mode == "normal":
            self.anchor = canvas_event
            self.mode = "edit"
            new_coords = canvas_event + canvas_event
            self.image_canvas.modify_existing_shape_using_canvas_coords(
                self.shape_id, new_coords)
            self.image_canvas.emit_select_changed()
        elif self.mode == "shift":
            self.anchor = canvas_event
        elif self.mode == "edit":
            pass

    def on_left_mouse_motion(self, event):
        self.mouse_moved = True
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        if self.mode == "shift":
            self._perform_shift(canvas_event, emit=True)
        elif self.mode == "edit":
            self._perform_edit(canvas_event, emit=True)

    def on_left_mouse_release(self, event):
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        if self.mode == "shift":
            if self.mouse_moved:
                self._perform_shift(canvas_event, emit=False)
                self.image_canvas.emit_select_finalized()
        elif self.mode == "edit":
            if self.mouse_moved:
                self._perform_edit(canvas_event, emit=False)
                self.image_canvas.emit_select_finalized()
        self.mouse_moved = False

    def on_mouse_motion(self, event):
        previous_mode = self.mode

        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        the_point = numpy.array(canvas_event)
        coords = self.image_canvas.get_shape_canvas_coords(self.shape_id)
        the_coords = normalized_rectangle_coordinates(coords)
        coords_diff = the_coords - the_point
        dists = numpy.sqrt(numpy.sum(coords_diff * coords_diff, axis=1))

        arg_min = numpy.argmin(dists)

        if dists[arg_min] < self.vertex_threshold:
            opposite_corner = ((arg_min + 2) % 4)
            new_mode = "edit"
            self.anchor = int(the_coords[opposite_corner, 0]), int(the_coords[opposite_corner, 1])
            cursor = self._cursors[arg_min]
        elif (the_coords[0, 0] < canvas_event[0] < the_coords[1, 0]) and \
                (the_coords[0, 1] < canvas_event[1] < the_coords[3, 1]):
            new_mode = "shift"
            cursor = "fleur"
        else:
            new_mode = "normal"
            cursor = "arrow"

        if previous_mode != new_mode:
            self.mode = new_mode
            self.image_canvas.config(cursor=cursor)

    def on_mouse_wheel(self, event):
        if self.mode in ['normal', ]:
            self.image_canvas.zoom_on_mouse(event)


class ViewTool(ImageCanvasTool):
    _name = 'VIEW'

    def __init__(self, image_canvas):
        ImageCanvasTool.__init__(self, image_canvas)

    def on_mouse_motion(self, event):
        self.image_canvas.emit_coordinate_changed(event)

    def on_mouse_wheel(self, event):
        self.image_canvas.zoom_on_mouse(event)


class ShapeSelectTool(ViewTool):
    """
    Tool for selecting the closest shape.
    """
    _name = 'SHAPE_SELECT'

    def on_left_mouse_click(self, event):
        self.image_canvas.select_closest_shape(event, set_as_current=True)


class ShiftShapeTool(ImageCanvasTool):
    """
    The tool for applying a constant shift to a given polygon.
    """
    _name = 'SHIFT_SHAPE'
    _mode_values = {"normal", "shift"}

    def __init__(self, image_canvas):
        ImageCanvasTool.__init__(self, image_canvas)
        self.shape_id = -1
        self.anchor = (0, 0)
        self.mouse_moved = False

    def initialize_tool(self):
        self.shape_id = self.image_canvas.current_shape_id
        self.anchor = (0, 0)
        self.mode = "normal"
        self.mouse_moved = False

    def finalize_tool(self):
        pass

    def on_left_mouse_click(self, event):
        self.mouse_moved = False
        if self.shape_id is None:
            self.image_canvas.select_closest_shape(event, set_as_current=True)
            self.initialize_tool()
        else:
            self.anchor = _get_canvas_event_coords(self.image_canvas, event)
            self.mode = "shift"

    def on_left_mouse_motion(self, event):
        self.mouse_moved = True
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        _perform_shape_shift(self.image_canvas, self.shape_id, canvas_event, self.anchor, emit=True)
        self.anchor = canvas_event

    def on_left_mouse_release(self, event):
        if self.mode == "normal" or not self.mouse_moved:
            return

        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        _perform_shape_shift(self.image_canvas, self.shape_id, canvas_event, self.anchor, emit=False)
        self.image_canvas.emit_shape_coords_finalized(the_id=self.shape_id)
        self.mode = "normal"
        self.mouse_moved = False

    def on_mouse_wheel(self, event):
        if self.mode in ['normal', ]:
            self.image_canvas.zoom_on_mouse(event)


class NewShapeTool(ViewTool):
    _name = 'NEW_SHAPE'

    def on_left_mouse_click(self, event):
        def staggered_coord():
            return canvas_event[0], canvas_event[1], canvas_event[0]+1, canvas_event[1]+1

        new_shape_type = self.image_canvas.new_shape_type
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        insert_at_index = 1
        if new_shape_type == ShapeTypeConstants.POINT:
            self.image_canvas.create_new_point(canvas_event)
            insert_at_index = 0
        elif new_shape_type == ShapeTypeConstants.TEXT:
            self.image_canvas.create_new_text(canvas_event, text='Text')
            insert_at_index = 0
        elif new_shape_type == ShapeTypeConstants.LINE:
            self.image_canvas.create_new_line(staggered_coord())
        elif new_shape_type == ShapeTypeConstants.ARROW:
            self.image_canvas.create_new_arrow(staggered_coord())
        elif new_shape_type == ShapeTypeConstants.RECT:
            self.image_canvas.create_new_rect(staggered_coord())
        elif new_shape_type == ShapeTypeConstants.ELLIPSE:
            self.image_canvas.create_new_ellipse(staggered_coord())
        elif new_shape_type == ShapeTypeConstants.POLYGON:
            self.image_canvas.create_new_polygon(canvas_event + canvas_event)
        else:
            raise ValueError(
                'Got unhandled shape type ShapeTypeConstants.{}'.format(
                    ShapeTypeConstants.get_name(new_shape_type)))

        # change the tool to edit the newly created shape
        self.image_canvas.current_tool = 'EDIT_SHAPE'
        self.image_canvas.current_tool.insert_at_index = insert_at_index
        self.image_canvas.current_tool.anchor = canvas_event


class EditShapeTool(ImageCanvasTool):
    _name = 'EDIT_SHAPE'
    _mode_values = {"normal", "shift"}

    def __init__(self, image_canvas):
        ImageCanvasTool.__init__(self, image_canvas)
        self.shape_id = None
        self.vector_object = None
        self.insert_at_index = 0
        self.anchor = (0, 0)
        self.mouse_moved = False
        self.vertex_threshold = self.image_canvas.variables.config.vertex_selector_pixel_threshold
        self._rect_cursors = ["top_left_corner", "top_right_corner", "bottom_right_corner", "bottom_left_corner"]

    def initialize_tool(self):
        self.shape_id = self.image_canvas.current_shape_id
        self.vector_object = self.image_canvas.get_vector_object(self.shape_id)
        self.insert_at_index = 0
        self.anchor = (0, 0)
        self.mouse_moved = False
        self.vertex_threshold = self.image_canvas.variables.config.vertex_selector_pixel_threshold
        self.mode = "normal"

    def finalize_tool(self):
        pass

    def _update_text_or_point(self, event):
        self.image_canvas.modify_existing_shape_using_canvas_coords(
            self.shape_id, _get_canvas_event_coords(self.image_canvas, event), update_pixel_coords=True)

    def _update_line_or_polygon(self, event, insert=True):
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        old_coords = self.image_canvas.get_shape_canvas_coords(self.shape_id)
        new_coords, self.insert_at_index = _modify_coords(
            self.image_canvas, self.shape_id, old_coords,
            canvas_event[0], canvas_event[1],
            self.insert_at_index, insert=insert)
        self.image_canvas.modify_existing_shape_using_canvas_coords(
            self.shape_id, new_coords, update_pixel_coords=True)

    def _update_arrow(self, event):
        if self.insert_at_index > 1:
            self.insert_at_index = 1
        if self.insert_at_index < 0:
            self.insert_at_index = 0
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        old_coords = self.image_canvas.get_shape_canvas_coords(self.shape_id)
        new_coords, _ = _modify_coords(
            self.image_canvas, self.shape_id, old_coords,
            canvas_event[0], canvas_event[1],
            self.insert_at_index, insert=False)
        self.image_canvas.modify_existing_shape_using_canvas_coords(
            self.shape_id, new_coords, update_pixel_coords=True)

    def on_left_mouse_click(self, event):
        self.mouse_moved = False
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        if self.shape_id is None:
            closest_shape_id = self.image_canvas.select_closest_shape(event, set_as_current=True)
            if closest_shape_id is not None:
                self.image_canvas.current_shape_id = closest_shape_id
                self.vector_object = self.image_canvas.get_vector_object(closest_shape_id)
                coord_index, the_distance, coord_x, coord_y = self.image_canvas.find_closest_shape_coord(
                    closest_shape_id, canvas_event[0], canvas_event[1])
                self.insert_at_index = coord_index
                self.anchor = (coord_x, coord_y)
            self.mode = "normal"
            return
        if self.vector_object is None:
            raise ValueError('Bad state')

        if self.mode == "shift":
            self.anchor = canvas_event
            return

        if self.vector_object.type in [ShapeTypeConstants.POINT, ShapeTypeConstants.TEXT]:
            self._update_text_or_point(event)
            return

        coord_index, the_distance, coord_x, coord_y = self.image_canvas.find_closest_shape_coord(
            self.shape_id, canvas_event[0], canvas_event[1])
        if the_distance < self.vertex_threshold:
            self.insert_at_index = coord_index
            return

        if self.vector_object.type in [ShapeTypeConstants.LINE, ShapeTypeConstants.POLYGON]:
            self._update_line_or_polygon(event, insert=True)
        elif self.vector_object.type == ShapeTypeConstants.ARROW:
            self._update_arrow(event)
        elif self.vector_object.type in [ShapeTypeConstants.RECT, ShapeTypeConstants.ELLIPSE]:
            self.image_canvas.modify_existing_shape_using_canvas_coords(
                self.shape_id, canvas_event + canvas_event)
            self.anchor = canvas_event
            self.insert_at_index = 1

    def on_left_mouse_motion(self, event):
        self.mouse_moved = True
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        if self.mode == "normal":
            previous_coords = self.image_canvas.get_shape_canvas_coords(self.shape_id)
            new_coords, _ = _modify_coords(
                self.image_canvas, self.shape_id, previous_coords,
                canvas_event[0], canvas_event[1],
                self.insert_at_index, insert=False)
            self.image_canvas.modify_existing_shape_using_canvas_coords(self.shape_id, new_coords)
        elif self.mode == "shift":
            _perform_shape_shift(self.image_canvas, self.shape_id, canvas_event, self.anchor, emit=True)
            self.anchor = canvas_event

    def on_left_mouse_release(self, event):
        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        if self.mode == "normal":
            if self.mouse_moved:
                previous_coords = self.image_canvas.get_shape_canvas_coords(self.shape_id)
                new_coords, _ = _modify_coords(
                    self.image_canvas, self.shape_id, previous_coords,
                    canvas_event[0], canvas_event[1],
                    self.insert_at_index, insert=False)
                self.image_canvas.modify_existing_shape_using_canvas_coords(self.shape_id, new_coords, emit=False)
                self.image_canvas.emit_shape_coords_finalized(the_id=self.shape_id)
        elif self.mode == "shift":
            if self.mouse_moved:
                _perform_shape_shift(self.image_canvas, self.shape_id, canvas_event, self.anchor, emit=False)
                self.image_canvas.emit_shape_coords_finalized(the_id=self.shape_id)
                self.mode = "normal"
        self.mouse_moved = False

    def on_mouse_motion(self, event):
        if self.shape_id is None:
            return
        if self.vector_object is None:
            raise ValueError('Bad state')

        canvas_event = _get_canvas_event_coords(self.image_canvas, event)
        if self.vector_object.type in [ShapeTypeConstants.RECT, ShapeTypeConstants.ELLIPSE]:
            the_point = numpy.array(canvas_event, dtype='float64')
            coords = self.image_canvas.get_shape_canvas_coords(self.shape_id)
            the_coords = normalized_rectangle_coordinates(coords)
            coords_diff = the_coords - the_point
            dists = numpy.sum(coords_diff * coords_diff, axis=1)

            arg_min = numpy.argmin(dists)
            previous_mode = self.mode
            if dists[arg_min] < self.vertex_threshold:
                new_mode = "normal"
                self.anchor = int(the_coords[arg_min, 0]), int(the_coords[arg_min, 1])
                cursor = self._rect_cursors[arg_min]
            elif (the_coords[0, 0] < canvas_event[0] < the_coords[1, 0]) and \
                    (the_coords[0, 1] < canvas_event[1] < the_coords[3, 1]):
                new_mode = "shift"
                cursor = "fleur"
            else:
                new_mode = "normal"
                cursor = "arrow"

            if previous_mode != new_mode:
                self.mode = new_mode
                self.image_canvas.config(cursor=cursor)

        elif self.vector_object.type in [ShapeTypeConstants.LINE, ShapeTypeConstants.ARROW]:
            the_dist = self.image_canvas.find_distance_from_shape(
                self.vector_object.uid, canvas_event[0], canvas_event[1])
            the_vertex, vertex_distance, _, _ = self.image_canvas.find_closest_shape_coord(
                self.vector_object.uid, canvas_event[0], canvas_event[1])

            if vertex_distance < self.vertex_threshold:
                self.image_canvas.config(cursor='cross')
                self.mode = "normal"
            elif the_dist < self.vertex_threshold:
                self.image_canvas.config(cursor='fleur')
                self.mode = "shift"
            else:
                self.mode = "normal"
                self.image_canvas.config(cursor='arrow')
        elif self.vector_object.type == ShapeTypeConstants.POLYGON:
            the_vertex, vertex_distance, _, _ = self.image_canvas.find_closest_shape_coord(
                self.shape_id, canvas_event[0], canvas_event[1])

            # noinspection PyBroadException
            try:
                geometry_object = self.image_canvas.get_geometry_for_shape(
                    self.shape_id, coordinate_type='canvas')
            except Exception:
                geometry_object = None

            if geometry_object is None:
                contained = False
                the_dist = float('inf')
            else:
                assert isinstance(geometry_object, LinearRing)

                # noinspection PyBroadException
                try:
                    contained = geometry_object.contain_coordinates(canvas_event[0], canvas_event[1])
                except Exception:
                    # should only be from a feeble linear ring
                    contained = False
                the_dist = geometry_object.get_minimum_distance(canvas_event)

            if vertex_distance < self.vertex_threshold:
                self.image_canvas.config(cursor='cross')
                self.mode = "normal"
            elif contained or the_dist < self.vertex_threshold:
                self.image_canvas.config(cursor='fleur')
                self.mode = "shift"
            else:
                self.image_canvas.config(cursor='arrow')
                self.mode = "normal"
        elif self.vector_object.type in [ShapeTypeConstants.POINT, ShapeTypeConstants.TEXT]:
            the_dist = self.image_canvas.find_distance_from_shape(
                self.shape_id, canvas_event[0], canvas_event[1])
            if the_dist < self.vertex_threshold:
                self.image_canvas.config(cursor='fleur')
                self.mode = "shift"
            else:
                self.image_canvas.config(cursor='arrow')
                self.mode = "normal"

    def on_right_mouse_click(self, event):
        if self.shape_id is None:
            return

        if self.mode == "normal":
            if self.vector_object.type not in [ShapeTypeConstants.LINE, ShapeTypeConstants.POLYGON]:
                return

            # delete the coordinate at the current insertion index
            coords = self.image_canvas.get_shape_canvas_coords(self.shape_id)
            point_count = int(len(coords) / 2)

            if point_count < 3:
                return

            index_remove = 2*self.insert_at_index
            if index_remove == 0:
                self.image_canvas.modify_existing_shape_using_canvas_coords(
                    self.shape_id, coords[2:], update_pixel_coords=True)
            elif index_remove >= point_count:
                self.image_canvas.modify_existing_shape_using_canvas_coords(
                    self.shape_id, coords[:-2], update_pixel_coords=True)
                self.insert_at_index = self.insert_at_index - 1
            else:
                self.image_canvas.modify_existing_shape_using_canvas_coords(
                    self.shape_id, coords[:index_remove] + coords[index_remove + 2:], update_pixel_coords=True)
                self.insert_at_index = self.insert_at_index - 1
            self.image_canvas.emit_shape_coords_finalized(the_id=self.shape_id)

    def on_mouse_wheel(self, event):
        if self.mode in ['normal', ]:
            self.image_canvas.zoom_on_mouse(event)


#########
# tool tracking methods

def register_tool(the_tool, overwrite=False):
    """
    Register a canvas tool for general usage.

    Parameters
    ----------
    the_tool : type
    overwrite : bool
        Should we replace the current tool, if one with the given name already exists?
    """

    global _CURRENT_ENUM_VALUE
    if not issubclass(the_tool, ImageCanvasTool):
        raise TypeError('requires a subclass of ImageCanvasTool, got type `{}`'.format(the_tool))

    # noinspection PyProtectedMember
    the_name = the_tool._name
    this_enum_value = _CURRENT_ENUM_VALUE + 1

    if the_name not in _TOOL_DICT:
        _TOOL_DICT[the_name] = the_tool
        _TOOL_NAME_TO_ENUM[the_name] = this_enum_value
        _TOOL_ENUM_TO_NAME[this_enum_value] = the_name
        logger.info('Registered tool `{}` under name `{}`'.format(the_tool, the_name))
        _CURRENT_ENUM_VALUE = this_enum_value
    elif overwrite:
        _TOOL_DICT[the_name] = the_tool
        logger.info('Redefined tool under name `{}` under to `{}`'.format(the_name, the_tool))
    else:
        logger.warning('Tool under name `{}` is already registered. Skipping registration.'.format(the_name))


def _register_defaults():
    global _DEFAULTS_REGISTERED
    if _DEFAULTS_REGISTERED:
        return
    for tool in [
            ViewTool, ZoomInTool, ZoomOutTool, PanTool, SelectTool,
            ShapeSelectTool, ShiftShapeTool, NewShapeTool, EditShapeTool]:
        register_tool(tool, overwrite=False)
    _DEFAULTS_REGISTERED = True


def get_tool_type(the_type):
    """
    Gets the type for the referenced tool.

    Parameters
    ----------
    the_type : type|str

    Returns
    -------
    type
    """

    if isinstance(the_type, string_types):
        return _TOOL_DICT[the_type]
    elif issubclass(the_type, ImageCanvasTool):
        return the_type
    else:
        raise ValueError('Got unexpected input `{}`'.format(the_type))


def get_tool_name(the_enum):
    """
    Gets the tool name from the enum value.

    Parameters
    ----------
    the_enum : int

    Returns
    -------
    str
    """

    return _TOOL_ENUM_TO_NAME[the_enum]


def get_tool_enum(the_name):
    """
    Gets the tool enum value from the name.

    Parameters
    ----------
    the_name : str

    Returns
    -------
    int
    """

    return _TOOL_NAME_TO_ENUM[the_name]


# actually register the defaults upon import or any reference
_register_defaults()
