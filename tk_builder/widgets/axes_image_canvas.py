import tkinter

import numpy

from tk_builder.widgets.image_canvas import ImageCanvas
from tk_builder.widgets.basic_widgets import Frame
from tk_builder.widgets.image_canvas import AppVariables as CanvasAppVariables
from tk_builder.image_readers.numpy_image_reader import NumpyImageReader
from tk_builder.utils.image_utils.create_checkerboard import create_checkerboard
from tk_builder.base_elements import IntegerDescriptor, StringDescriptor, FloatDescriptor
from tk_builder.image_readers.image_reader import ImageReader
from PIL import Image


class AppVariables(CanvasAppVariables):
    """
    The canvas image application variables.
    """

    title = StringDescriptor('title', default_value="", docstring='')  # type: str
    x_label = StringDescriptor('x_label', default_value="", docstring='')  # type: str
    y_label = StringDescriptor('y_label', default_value="", docstring='')  # type: str
    image_x_start = FloatDescriptor('image_x_start', default_value=None)  # type: int
    image_x_end = FloatDescriptor('image_x_end', default_value=None)  # type: int
    image_y_start = FloatDescriptor('image_y_start', default_value=None)  # type: int
    image_y_end = FloatDescriptor('image_y_end', default_value=None)  # type: int
    top_margin = IntegerDescriptor('top_margin', default_value=0)  # type: int
    bottom_margin = IntegerDescriptor('bottom_margin', default_value=0)  # type: int
    left_margin = IntegerDescriptor('left_margin', default_value=0)  # type: int
    right_margin = IntegerDescriptor('right_margin', default_value=0)  # type: int
    n_x_axis_ticks = IntegerDescriptor('n_x_axis_ticks', default_value=5)  # type: int
    n_y_axis_ticks = IntegerDescriptor('n_y_axis_ticks', default_value=5)  # type: int
    outer_canvas_reader = None  # type: ImageReader
    inner_canvas_reader = None  # type: ImageReader
    resizeable = False  # type: bool
    update_outer_canvas_on_resize = False  # type: bool


class AxesImageCanvas(ImageCanvas):
    def __init__(self,
                 parent,
                 ):
        ImageCanvas.__init__(self, parent)

        self.variables = AppVariables()
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        self.inner_frame = Frame(self)
        self.inner_canvas = ImageCanvas(self)
        self.inner_frame.pack()
        self.inner_canvas.pack()
        square_size = 50
        n_squares_x = 20
        n_squares_y = 20
        canvas_height = square_size * n_squares_y
        canvas_width = square_size * n_squares_x
        self.set_canvas_size(canvas_width, canvas_height)
        canvas_image = create_checkerboard(square_size, n_squares_x, n_squares_y) * 255
        canvas_image = numpy.asarray(canvas_image, dtype=numpy.uint8)

        background_image = create_checkerboard(square_size, 4, 4) * 255
        background_image = numpy.asarray(background_image, dtype=numpy.uint8)

        outer_canvas_reader = NumpyImageReader(background_image)
        inner_canvas_reader = NumpyImageReader(canvas_image)
        self.set_image_reader(outer_canvas_reader)
        self.inner_canvas.set_image_reader(inner_canvas_reader)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    @property
    def update_outer_canvas_on_resize(self):
        return self.variables.update_outer_canvas_on_resize

    @update_outer_canvas_on_resize.setter
    def update_outer_canvas_on_resize(self, value):
        self.variables.update_outer_canvas_on_resize = value

    @property
    def resizeable(self):
        return self.variables.resizeable

    @resizeable.setter
    def resizeable(self, value):
        self.variables.resizeable = value
        if self.resizeable:
            self.on_resize(self.callback_resize)
        else:
            self.on_resize(self.do_nothing)

    def callback_resize(self, event):
        width = event.width
        height = event.height
        self._resize(width, height)

    def _resize(self, width, height):
        inner_rect_width = int(width) - self.left_margin_pixels - self.right_margin_pixels
        inner_rect_height = int(height) - self.top_margin_pixels - self.bottom_margin_pixels
        self.inner_canvas.set_canvas_size(inner_rect_width, inner_rect_height)
        self.inner_canvas.config(width=inner_rect_width, height=inner_rect_height)
        self.create_window(self.left_margin_pixels, self.top_margin_pixels, anchor=tkinter.NW, window=self.inner_canvas)
        image_dims = self.inner_canvas.variables.canvas_image_object.display_image.shape
        canvas_rect = [0, 0, image_dims[1], image_dims[0]]
        if self.update_outer_canvas_on_resize:
            background_image = Image.fromarray(self.variables.canvas_image_object.image_reader[:])
            background_image.resize((width, height))
            self.set_image_from_numpy_array(numpy.asarray(background_image))
        self.inner_canvas.zoom_to_canvas_selection(canvas_rect)

    def zoom_to_canvas_selection(self, canvas_rect, animate=False):
        pass

    @property
    def top_margin_pixels(self):
        return self.variables.top_margin

    @top_margin_pixels.setter
    def top_margin_pixels(self, value):
        self.variables.top_margin = value

    @property
    def left_margin_pixels(self):
        return self.variables.left_margin

    @left_margin_pixels.setter
    def left_margin_pixels(self, value):
        self.variables.left_margin = value

    @property
    def bottom_margin_pixels(self):
        return self.variables.bottom_margin

    @bottom_margin_pixels.setter
    def bottom_margin_pixels(self, value):
        self.variables.bottom_margin = value

    @property
    def right_margin_pixels(self):
        return self.variables.right_margin

    @right_margin_pixels.setter
    def right_margin_pixels(self, value):
        self.variables.right_margin = value

    @property
    def title(self):
        return self.variables.title

    @title.setter
    def title(self, value):
        self.variables.title = value

    @property
    def x_label(self):
        return self.variables.x_label

    @x_label.setter
    def x_label(self, value):
        self.variables.x_label = value

    @property
    def y_label(self):
        return self.variables.y_label

    @y_label.setter
    def y_label(self, value):
        self.variables.y_label = " " + value

    @property
    def image_x_min_val(self):
        return self.variables.image_x_start

    @image_x_min_val.setter
    def image_x_min_val(self, value):
        self.variables.image_x_start = value

    @property
    def image_x_max_val(self):
        return self.variables.image_x_end

    @image_x_max_val.setter
    def image_x_max_val(self, value):
        self.variables.image_x_end = value

    @property
    def image_y_min_val(self):
        return self.variables.image_y_start

    @image_y_min_val.setter
    def image_y_min_val(self, value):
        self.variables.image_y_start = value

    @property
    def image_y_max_val(self):
        return self.variables.image_y_end

    @image_y_max_val.setter
    def image_y_max_val(self, value):
        self.variables.image_y_end = value

    def _update_title(self):
        display_image = self.inner_canvas.variables.canvas_image_object.display_image
        display_image_dims = numpy.shape(display_image)
        if len(display_image_dims) == 2:
            image_height, image_width = display_image_dims
        else:
            image_height, image_width = display_image_dims[0], display_image_dims[1]
        left_pixel_index = self.left_margin_pixels + 2
        right_pixel_index = self.left_margin_pixels + image_width
        label_y_index = self.top_margin_pixels - 30

        self.create_new_text(((left_pixel_index + right_pixel_index) / 2, label_y_index),
                         text=self.title,
                         fill="black",
                         anchor="n")

    def _update_x_axis(self):
        display_image = self.inner_canvas.variables.canvas_image_object.display_image
        display_image_dims = numpy.shape(display_image)
        if len(display_image_dims) == 2:
            image_height, image_width = display_image_dims
        else:
            image_height, image_width = display_image_dims[0], display_image_dims[1]
        left_pixel_index = self.left_margin_pixels + 2
        right_pixel_index = self.left_margin_pixels + image_width
        bottom_pixel_index = self.top_margin_pixels + self.inner_canvas.variables.canvas_height + 30
        label_y_index = bottom_pixel_index + 30

        x_axis_positions = numpy.linspace(left_pixel_index, right_pixel_index, self.variables.n_x_axis_ticks)

        tick_positions = []
        for x in x_axis_positions:
            tick_positions.append((x, bottom_pixel_index))

        if self.variables.image_x_start is not None and self.variables.image_x_end is not None:
            m = (self.variables.image_x_end - self.variables.image_x_start) / self.inner_canvas.variables.canvas_image_object.image_reader.full_image_nx
            b = self.variables.image_x_start

            display_image_coords = self.inner_canvas.variables.canvas_image_object.canvas_coords_to_full_image_yx(
                (0, 0, image_width, image_height))
            tick_vals = numpy.linspace(display_image_coords[1], display_image_coords[3], self.variables.n_x_axis_ticks)
            tick_vals = m * tick_vals + b

            for xy, tick_val in zip(tick_positions, tick_vals):
                self.create_new_text(xy, text="{:.2f}".format(tick_val), fill="black", anchor="n")

            self.create_new_text((x_axis_positions[int(self.variables.n_x_axis_ticks / 2)], label_y_index),
                             text=self.x_label,
                             fill="black",
                             anchor="n")

    def _update_x_label(self):
        display_image = self.inner_canvas.variables.canvas_image_object.display_image
        display_image_dims = numpy.shape(display_image)
        if len(display_image_dims) == 2:
            image_height, image_width = display_image_dims
        else:
            image_height, image_width = display_image_dims[0], display_image_dims[1]
        left_pixel_index = self.left_margin_pixels + 2
        right_pixel_index = self.left_margin_pixels + image_width
        bottom_pixel_index = self.top_margin_pixels + self.inner_canvas.variables.canvas_height + 30
        label_y_index = bottom_pixel_index + 30

        x_axis_positions = numpy.linspace(left_pixel_index, right_pixel_index, self.variables.n_x_axis_ticks)

        self.create_new_text((x_axis_positions[int(self.variables.n_x_axis_ticks / 2)], label_y_index),
                         text=self.x_label,
                         fill="black",
                         anchor="n")

    def _update_y_axis(self):
        left_pixel_index = self.left_margin_pixels - 40
        display_image = self.inner_canvas.variables.canvas_image_object.display_image
        display_image_dims = numpy.shape(display_image)
        if len(display_image_dims) == 2:
            image_height, image_width = display_image_dims
        else:
            image_height, image_width = display_image_dims[0], display_image_dims[1]
        top_pixel_index = self.top_margin_pixels
        bottom_pixel_index = self.top_margin_pixels + image_height

        y_axis_positions = numpy.linspace(top_pixel_index, bottom_pixel_index, self.variables.n_y_axis_ticks)

        tick_positions = []
        for y in y_axis_positions:
            tick_positions.append((left_pixel_index, y))

        if self.variables.image_y_start and self.variables.image_y_end:
            m = (
                            self.variables.image_y_end - self.variables.image_y_start) / self.inner_canvas.variables.canvas_image_object.image_reader.full_image_ny
            b = self.variables.image_y_start

            display_image_coords = self.inner_canvas.variables.canvas_image_object.canvas_coords_to_full_image_yx(
                (0, 0, image_width, image_height))
            tick_vals = numpy.linspace(display_image_coords[0], display_image_coords[2], self.variables.n_y_axis_ticks)
            tick_vals = m * tick_vals + b

            for xy, tick_val in zip(tick_positions, tick_vals):
                self.create_new_text(xy, text="{:.2f}".format(tick_val), fill="black", anchor="n")

    def _update_y_label(self):
        left_pixel_index = self.left_margin_pixels - 40
        display_image = self.inner_canvas.variables.canvas_image_object.display_image
        display_image_dims = numpy.shape(display_image)
        if len(display_image_dims) == 2:
            image_height, image_width = display_image_dims
        else:
            image_height, image_width = display_image_dims[0], display_image_dims[1]
        top_pixel_index = self.top_margin_pixels
        bottom_pixel_index = self.top_margin_pixels + image_height

        y_axis_positions = numpy.linspace(top_pixel_index, bottom_pixel_index, self.variables.n_y_axis_ticks)

        label_x_index = left_pixel_index - 30

        self.create_new_text((label_x_index, y_axis_positions[int(self.variables.n_y_axis_ticks / 2)]),
                         text=self.variables.y_label,
                         fill="black",
                         anchor="s",
                         angle=90,
                         justify="right")
