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


class ImageCanvasPanel(LabelFrame):
    def __init__(self,
                 master,
                 ):
        LabelFrame.__init__(self, master)

        self.variables = AppVariables()
        self.outer_canvas = ImageCanvas(self)
        self.outer_canvas.variables.rescale_image_to_fit_canvas=False
        self.canvas = ImageCanvas(self.outer_canvas)
        # self.outer_canvas.set_canvas_size(200, 200)
        # self.outer_canvas.pack(expand=tkinter.Y, fill=tkinter.BOTH)
        self.outer_canvas.pack()
        self.canvas.pack()

    @property
    def x_margin(self):
        return self.outer_canvas.variables.canvas_width * self.variables.left_margin

    @property
    def y_margin(self):
        return self.outer_canvas.variables.canvas_height * self.variables.top_margin

    @property
    def left_margin_percent(self):
        return self.variables.left_margin

    @left_margin_percent.setter
    def left_margin_percent(self, value):
        self.variables.left_margin = value
        self.outer_canvas.create_window(self.x_margin, self.y_margin, anchor=tkinter.NW, window=self.canvas)

    def set_canvas_size(self, width_npix, height_npix):
        self.outer_canvas.set_canvas_size(self.canvas.variables.canvas_width * (1 + self.variables.left_margin + self.variables.right_margin),
                                          self.canvas.variables.canvas_height * (1 + self.variables.top_margin + self.variables.bottom_margin))
        self.canvas.set_canvas_size(width_npix, height_npix)

    def update_x_axis(self, start_val=-10, stop_val=10, label=None):
        n_ticks = 5
        display_image = self.canvas.variables.canvas_image_object.display_image
        image_width = numpy.shape(display_image)[1]
        left_pixel_index = self.x_margin + 2
        right_pixel_index = self.x_margin + image_width
        bottom_pixel_index = self.y_margin + self.canvas.variables.canvas_height + 20
        label_y_index = bottom_pixel_index + 30

        tick_vals = numpy.linspace(start_val, stop_val, n_ticks)
        x_axis_positions = numpy.linspace(left_pixel_index, right_pixel_index, n_ticks)

        tick_positions = []
        for x in x_axis_positions:
            tick_positions.append((x, bottom_pixel_index))

        self.outer_canvas.variables.foreground_color = "black"

        for xy, tick_val in zip(tick_positions, tick_vals):
            self.outer_canvas.create_text(xy, text=tick_val, fill="black", anchor="n")

        if label:
            self.outer_canvas.create_text((x_axis_positions[int(n_ticks/2)], label_y_index), text=label, fill="black", anchor="n")

    def update_y_axis(self, start_val, stop_val, label=None, n_ticks=5):
        # self.left_margin_percent = 0.15

        display_image = self.canvas.variables.canvas_image_object.display_image
        image_width = numpy.shape(display_image)[1]
        left_pixel_index = self.x_margin - 40
        right_pixel_index = self.x_margin + image_width
        top_pixel_index = self.y_margin
        bottom_pixel_index = self.y_margin + self.canvas.variables.canvas_height
        label_x_index = left_pixel_index - 30

        tick_vals = numpy.linspace(stop_val, start_val, n_ticks)
        y_axis_positions = numpy.linspace(top_pixel_index, bottom_pixel_index, n_ticks)

        tick_positions = []
        for y in y_axis_positions:
            tick_positions.append((left_pixel_index, y))

        self.canvas.variables.foreground_color = "black"

        for xy, tick_val in zip(tick_positions, tick_vals):
            self.canvas.create_text(xy, text=tick_val, fill="black", anchor="w")

        if label:
            self.canvas.create_text((label_x_index, y_axis_positions[int(n_ticks/2)]), text=label, fill="black", anchor="s", angle=90, justify="right")
