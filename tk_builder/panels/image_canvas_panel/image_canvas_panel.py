import tkinter
from tk_builder.widgets.widget_wrappers.labelFrame import LabelFrame
from tk_builder.widgets.image_canvas import ImageCanvas
import numpy


class AppVariables:
    def __init__(self):
        self.x_label = None
        self.y_label = None
        self.title = None
        self.top_margin = 0
        self.bottom_margin = 0
        self.left_margin = 0
        self.right_margin = 0
        self.n_x_axis_ticks = 5
        self.n_y_axis_ticks = 5
        self.image_x_start = None
        self.image_x_end = None
        self.image_y_start = None
        self.image_y_end = None
        self.x_axis_n_decimals = 2
        self.canvas_width = None
        self.canvas_height = None
        self.tooltip = None


class ImageCanvasPanel(LabelFrame):
    def __init__(self,
                 master,
                 ):
        LabelFrame.__init__(self, master)

        self.variables = AppVariables()
        self.outer_canvas = ImageCanvas(self)
        self.canvas = ImageCanvas(self.outer_canvas)
        self.outer_canvas.pack()
        self.canvas.pack()

        self.canvas.on_mouse_wheel(self.callback_handle_mouse_wheel)
        self.canvas.on_left_mouse_release(self.callback_handle_left_mouse_release)

    def callback_handle_mouse_wheel(self, event):
        self.set_canvas_size(self.variables.canvas_width, self.variables.canvas_height)
        self.canvas.callback_mouse_zoom(event)
        self.update_outer_canvas()

    def callback_handle_left_mouse_release(self, event):
        self.canvas.callback_handle_left_mouse_release(event)
        self.update_outer_canvas()

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
        self.canvas.set_image_reader(image_reader)
        if self.variables.image_x_start is None:
            self.variables.image_x_start = 0
        if self.variables.image_y_start is None:
            self.variables.image_y_start = 0
        if self.variables.image_x_end is None:
            self.variables.image_x_end = self.canvas.variables.canvas_image_object.image_reader.full_image_nx
        if self.variables.image_y_end is None:
            self.variables.image_y_end = self.canvas.variables.canvas_image_object.image_reader.full_image_ny

    @property
    def top_margin_pixels(self):
        return self.variables.top_margin

    @top_margin_pixels.setter
    def top_margin_pixels(self, value):
        self.variables.top_margin = value
        self.outer_canvas.create_window(self.left_margin_pixels,
                                        self.top_margin_pixels,
                                        anchor=tkinter.NW,
                                        window=self.canvas)
        self._update_canvas_margins()
        self.update_outer_canvas()

    @property
    def left_margin_pixels(self):
        return self.variables.left_margin

    @left_margin_pixels.setter
    def left_margin_pixels(self, value):
        self.variables.left_margin = value
        self.outer_canvas.create_window(self.left_margin_pixels,
                                        self.top_margin_pixels,
                                        anchor=tkinter.NW,
                                        window=self.canvas)
        self._update_canvas_margins()
        self.update_outer_canvas()

    @property
    def bottom_margin_pixels(self):
        return self.variables.bottom_margin

    @bottom_margin_pixels.setter
    def bottom_margin_pixels(self, value):
        self.variables.bottom_margin = value
        self._update_canvas_margins()
        self.update_outer_canvas()

    @property
    def right_margin_pixels(self):
        return self.variables.right_margin

    @right_margin_pixels.setter
    def right_margin_pixels(self, value):
        self.variables.right_margin = value
        self._update_canvas_margins()
        self.update_outer_canvas()

    def set_canvas_size(self, width_npix, height_npix):
        self.outer_canvas.set_canvas_size(self.canvas.variables.canvas_width +
                                          self.variables.left_margin + self.variables.right_margin,
                                          self.canvas.variables.canvas_height +
                                          self.variables.top_margin + self.variables.bottom_margin)
        self.canvas.set_canvas_size(width_npix, height_npix)
        self.variables.canvas_width = width_npix
        self.variables.canvas_height = height_npix

    def _update_canvas_margins(self):
        self.outer_canvas.set_canvas_size(self.canvas.variables.canvas_width +
                                          self.variables.left_margin + self.variables.right_margin,
                                          self.canvas.variables.canvas_height +
                                          self.variables.top_margin + self.variables.bottom_margin)

    @property
    def title(self):
        return self.variables.title

    @title.setter
    def title(self, value):
        self.variables.title = value
        self.update_outer_canvas()

    @property
    def x_label(self):
        return self.variables.x_label

    @x_label.setter
    def x_label(self, value):
        self.variables.x_label = value
        self.update_outer_canvas()

    @property
    def y_label(self):
        return self.variables.y_label

    @y_label.setter
    def y_label(self, value):
        self.variables.y_label = value
        self.update_outer_canvas()

    @property
    def image_x_min_val(self):
        return self.variables.image_x_start

    @image_x_min_val.setter
    def image_x_min_val(self, value):
        self.variables.image_x_start = value
        self.update_outer_canvas()

    @property
    def image_x_max_val(self):
        return self.variables.image_x_end

    @image_x_max_val.setter
    def image_x_max_val(self, value):
        self.variables.image_x_end = value
        self.update_outer_canvas()

    @property
    def image_y_min_val(self):
        return self.variables.image_y_start

    @image_y_min_val.setter
    def image_y_min_val(self, value):
        self.variables.image_y_start = value
        self.update_outer_canvas()

    @property
    def image_y_max_val(self):
        return self.variables.image_y_end

    @image_y_max_val.setter
    def image_y_max_val(self, value):
        self.variables.image_y_end = value
        self.update_outer_canvas()

    def update_outer_canvas(self):
        self.outer_canvas.delete("all")
        self.set_canvas_size(self.variables.canvas_width, self.variables.canvas_height)
        self.canvas.update_current_image()
        display_image_size = numpy.shape(self.canvas.variables.canvas_image_object.display_image)
        if display_image_size[1] < self.variables.canvas_width or display_image_size[0] < self.variables.canvas_height:
            self.canvas.set_canvas_size(display_image_size[1], display_image_size[0])
        self._update_canvas_margins()
        self.outer_canvas.create_window(self.left_margin_pixels,
                                        self.top_margin_pixels,
                                        anchor=tkinter.NW,
                                        window=self.canvas)
        self._update_x_axis()
        self._update_y_axis()
        self._update_title()

    def _update_title(self):
        display_image = self.canvas.variables.canvas_image_object.display_image
        image_height, image_width = numpy.shape(display_image)
        left_pixel_index = self.left_margin_pixels + 2
        right_pixel_index = self.left_margin_pixels + image_width
        label_y_index = self.top_margin_pixels - 30

        self.outer_canvas.create_text(((left_pixel_index + right_pixel_index)/2, label_y_index),
                                      text=self.title,
                                      fill="black",
                                      anchor="n")

    def _update_x_axis(self):
        display_image = self.canvas.variables.canvas_image_object.display_image
        image_height, image_width = numpy.shape(display_image)
        left_pixel_index = self.left_margin_pixels + 2
        right_pixel_index = self.left_margin_pixels + image_width
        bottom_pixel_index = self.top_margin_pixels + self.canvas.variables.canvas_height + 30
        label_y_index = bottom_pixel_index + 30

        x_axis_positions = numpy.linspace(left_pixel_index, right_pixel_index, self.variables.n_x_axis_ticks)

        tick_positions = []
        for x in x_axis_positions:
            tick_positions.append((x, bottom_pixel_index))

        m = (self.variables.image_x_end - self.variables.image_x_start) / self.canvas.variables.canvas_image_object.image_reader.full_image_nx
        b = self.variables.image_x_start

        display_image_coords = self.canvas.variables.canvas_image_object.canvas_coords_to_full_image_yx((0, 0, image_width, image_height))
        tick_vals = numpy.linspace(display_image_coords[1], display_image_coords[3], self.variables.n_x_axis_ticks)
        tick_vals = m * tick_vals + b

        for xy, tick_val in zip(tick_positions, tick_vals):
            self.outer_canvas.create_text(xy, text="{:.2f}".format(tick_val), fill="black", anchor="n")

        self.outer_canvas.create_text((x_axis_positions[int(self.variables.n_x_axis_ticks/2)], label_y_index),
                                      text=self.x_label,
                                      fill="black",
                                      anchor="n")

    def _update_y_axis(self):
        left_pixel_index = self.left_margin_pixels - 40
        display_image = self.canvas.variables.canvas_image_object.display_image
        image_height, image_width = numpy.shape(display_image)
        top_pixel_index = self.top_margin_pixels
        bottom_pixel_index = self.top_margin_pixels + image_height
        label_x_index = left_pixel_index - 30

        y_axis_positions = numpy.linspace(top_pixel_index, bottom_pixel_index, self.variables.n_y_axis_ticks)

        tick_positions = []
        for y in y_axis_positions:
            tick_positions.append((left_pixel_index, y))

        m = (self.variables.image_y_end - self.variables.image_y_start) / self.canvas.variables.canvas_image_object.image_reader.full_image_ny
        b = self.variables.image_y_start

        display_image_coords = self.canvas.variables.canvas_image_object.canvas_coords_to_full_image_yx(
            (0, 0, image_width, image_height))
        tick_vals = numpy.linspace(display_image_coords[0], display_image_coords[2], self.variables.n_y_axis_ticks)
        tick_vals = m * tick_vals + b

        for xy, tick_val in zip(tick_positions, tick_vals):
            self.outer_canvas.create_text(xy, text="{:.2f}".format(tick_val), fill="black", anchor="n")

        self.outer_canvas.create_text((label_x_index, y_axis_positions[int(self.variables.n_y_axis_ticks/2)]),
                                text=self.variables.y_label,
                                fill="black",
                                anchor="s",
                                angle=90,
                                justify="right")
