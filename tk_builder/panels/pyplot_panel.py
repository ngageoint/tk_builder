
import logging
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    logging.error('Failed importing FigureCanvasTkAgg from matplotlib. This is likely '
                  'because the matplotlib in your environment was not built with tkinter '
                  'backend support enabled. No functionality for the pyplot panel '
                  'will be functional.')
    FigureCanvasTkAgg = None

from matplotlib.collections import LineCollection
import time
import numpy

from tk_builder.widgets import basic_widgets
from tk_builder.panels.pyplot_panel_utils.plot_style_utils import PlotStyleUtils
from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets.pyplot_canvas import PyplotCanvas

SCALE_Y_AXIS_PER_FRAME_TRUE = "scale y axis per frame"
SCALE_Y_AXIS_PER_FRAME_FALSE = "don't scale y axis per frame"

PYPLOT_UTILS = PlotStyleUtils()


class PyplotControlPanel(WidgetPanel):
    _widget_list = ("color_palette_label",
                    "color_palette",
                    "n_colors_label",
                    "n_colors",
                    "scale",
                    "rescale_y_axis_per_frame",
                    "fps_label",
                    "fps_entry",
                    "animate")
    color_palette_label = widget_descriptors.LabelDescriptor("color_palette_label")  # type: basic_widgets.Label
    color_palette = widget_descriptors.ComboboxDescriptor("color_palette")                     # type: basic_widgets.Combobox
    n_colors_label = widget_descriptors.LabelDescriptor("n_colors_label")                        # type: basic_widgets.Label
    n_colors = widget_descriptors.SpinboxDescriptor("n_colors")                            # type: basic_widgets.Spinbox
    scale = widget_descriptors.ScaleDescriptor("scale")                                 # type: basic_widgets.Scale
    rescale_y_axis_per_frame = widget_descriptors.ComboboxDescriptor("rescale_y_axis_per_frame")          # type: basic_widgets.Combobox
    animate = widget_descriptors.ButtonDescriptor("animate")                             # type: basic_widgets.Button
    fps_label = widget_descriptors.LabelDescriptor("fps_label")                             # type: basic_widgets.Label
    fps_entry = widget_descriptors.EntryDescriptor("fps_entry")                            # type: basic_widgets.Entry

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)

        self.init_w_basic_widget_list(4, [4, 1, 1, 3])
        self.color_palette.update_combobox_values(PYPLOT_UTILS.get_all_palettes_list())
        self.n_colors.config(from_=0)
        self.n_colors.config(to=10)
        self.scale.set(0)
        self.rescale_y_axis_per_frame.update_combobox_values([SCALE_Y_AXIS_PER_FRAME_TRUE, SCALE_Y_AXIS_PER_FRAME_FALSE])
        self.fps_label.set_text("fps")
        self.fps_entry.set_text("30")


class AppVariables():
    def __init__(self):
        self.title = None       # type: str
        self.x_label = None     # type: str
        self.y_label = None     # type: str
        self.x_axis = None  # type: np.ndarray
        self.plot_data = None  # type: np.ndarray

        self.xmin = None  # type: float
        self.xmax = None  # type: float
        self.ymin = None  # type: float
        self.ymax = None  # type: float

        self.y_margin = 0.05
        self.set_y_margins_per_frame = False
        self.n_frames = 1

        self.segments = None  # type: np.ndarray

        self.animation_related_controls = []
        self.animation_index = 0


class PyplotPanel(WidgetPanel):
    _widget_list = ("pyplot_canvas", "control_panel", )
    pyplot_canvas = widget_descriptors.PyplotCanvasDescriptor("pyplot_canvas")           # type: PyplotCanvas
    control_panel = widget_descriptors.PanelDescriptor("control_panel", PyplotControlPanel)  # type: PyplotControlPanel

    def __init__(self, primary):
        WidgetPanel.__init__(self, primary)

        self.variables = AppVariables()
        self.pyplot_utils = PlotStyleUtils()
        self.init_w_vertical_layout()

        canvas_size_pixels = self.pyplot_canvas.canvas.figure.get_size_inches() * self.pyplot_canvas.canvas.figure.dpi

        self.control_panel.scale.config(length=canvas_size_pixels[0] * 0.75)
        self.variables.animation_related_controls = [self.control_panel.scale,
                                                     self.control_panel.rescale_y_axis_per_frame,
                                                     self.control_panel.animate,
                                                     self.control_panel.fps_entry,
                                                     self.control_panel.fps_label]

        self.control_panel.n_colors_label.set_text("n colors")
        self.control_panel.n_colors.set_text(self.pyplot_utils.n_color_bins)

        # set listeners
        self.control_panel.scale.on_left_mouse_motion(self.callback_update_from_slider)
        self.control_panel.rescale_y_axis_per_frame.on_selection(self.callback_set_y_rescale)
        self.control_panel.animate.config(command=self.animate)
        self.control_panel.color_palette.on_selection(self.callback_update_plot_colors)
        self.control_panel.n_colors.on_enter_or_return_key(self.callback_update_n_colors)
        self.control_panel.n_colors.config(command=self.update_n_colors)

        # self.hide_animation_related_controls()
        self.hide_control_panel()

    @property
    def title(self):
        return self.variables.title

    @title.setter
    def title(self, val):
        self.variables.title = val
        self.pyplot_canvas.axes.set_title(val)
        self.update_plot()

    @property
    def y_label(self):
        return self.variables.y_label

    @y_label.setter
    def y_label(self, val):
        self.variables.y_label = val
        self.pyplot_canvas.axes.set_ylabel(val)
        self.update_plot()

    @property
    def x_label(self):
        return self.variables.y_label

    @x_label.setter
    def x_label(self, val):
        self.variables.x_label = val
        self.pyplot_canvas.axes.set_xlabel(val)
        self.update_plot()

    def hide_control_panel(self):
        self.control_panel.pack_forget()

    def show_control_panel(self):
        self.control_panel.pack()

    def hide_animation_related_controls(self):
        for widget in self.variables.animation_related_controls:
            widget.pack_forget()

    def show_animation_related_controls(self):
        for widget in self.variables.animation_related_controls:
            widget.pack()

    def set_y_margin_percent(self,
                             percent_0_to_100=5          # type: float
                             ):
        self.variables.y_margin = percent_0_to_100 * 0.01

    def set_data(self, plot_data, x_axis=None):
        """


        Parameters
        ----------
        plot_data : numpy.ndarray
        x_axis : numpy.ndarray

        Returns
        -------

        """
        x = x_axis
        n_frames = 1
        if len(plot_data.shape) == 1:
            self.hide_animation_related_controls()
            nx = len(plot_data)
            segments = numpy.zeros((1, nx, 2))
            segments[0, :, 1] = plot_data
        elif len(plot_data.shape) == 2:
            self.hide_animation_related_controls()
            nx = len(plot_data[:, 0])
            n_overplots = len(plot_data[0])
            segments = numpy.zeros((n_overplots, nx, 2))
            for i in range(n_overplots):
                segments[i, :, 1] = plot_data[:, i]
        elif len(plot_data.shape) == 3:
            self.show_animation_related_controls()
            nx = numpy.shape(plot_data)[0]
            n_overplots = numpy.shape(plot_data)[1]
            n_frames = numpy.shape(plot_data)[2]
            segments = numpy.zeros((n_overplots, nx, 2))
            for i in range(n_overplots):
                segments[i, :, 1] = plot_data[:, i, 0]
        if x is None:
            x = numpy.arange(nx)
        segments[:, :, 0] = x

        self.variables.xmin = x.min()
        self.variables.xmax = x.max()

        y_range = plot_data.max() - plot_data.min()

        self.variables.ymin = plot_data.min() - y_range * self.variables.y_margin
        self.variables.ymax = plot_data.max() + y_range * self.variables.y_margin

        self.variables.x_axis = x
        self.variables.plot_data = plot_data
        self.variables.segments = segments
        self.variables.n_frames = n_frames

        self.control_panel.scale.config(to=n_frames-1)

        if len(plot_data.shape) == 3:
            self.update_plot_animation(0)

        else:
            self.pyplot_canvas.axes.clear()
            self.pyplot_canvas.axes.plot(self.variables.plot_data)
            self.pyplot_canvas.axes.set_ylim(self.variables.ymin, self.variables.ymax)
            self.pyplot_canvas.canvas.draw()

    def update_plot_animation(self, animation_index):
        self.update_animation_index(animation_index)
        self.update_plot()

    def update_animation_index(self, animation_index):
        self.control_panel.scale.set(animation_index)
        self.variables.animation_index = animation_index

    def callback_update_from_slider(self, event):
        self.variables.animation_index = int(numpy.round(self.control_panel.scale.get()))
        self.update_plot()

    # define custom callbacks here
    def callback_set_y_rescale(self, event):
        selection = self.control_panel.rescale_y_axis_per_frame.get()
        if selection == SCALE_Y_AXIS_PER_FRAME_TRUE:
            self.variables.set_y_margins_per_frame = True
        else:
            self.variables.set_y_margins_per_frame = False
            y_range = self.variables.plot_data.max() - self.variables.plot_data.min()
            self.variables.ymin = self.variables.plot_data.min() - y_range * self.variables.y_margin
            self.variables.ymax = self.variables.plot_data.max() + y_range * self.variables.y_margin
        self.update_plot()

    def animate(self):
        start_frame = 0
        stop_frame = self.variables.n_frames
        fps = float(self.control_panel.fps_entry.get())

        time_between_frames = 1 / fps

        for i in range(start_frame, stop_frame):
            tic = time.time()
            self.update_animation_index(i)
            self.update_plot()
            toc = time.time()
            time_to_update_plot = toc - tic
            if time_between_frames > time_to_update_plot:
                time.sleep(time_between_frames - time_to_update_plot)
            else:
                pass

    def callback_update_plot_colors(self, event):
        color_palette_text = self.control_panel.color_palette.get()
        self.pyplot_utils.set_palette_by_name(color_palette_text)
        self.update_plot()

    def callback_update_n_colors(self, event):
        n_colors = int(self.control_panel.n_colors.get())
        self.pyplot_utils.set_n_colors(n_colors)
        self.update_plot()

    def update_n_colors(self):
        n_colors = int(self.control_panel.n_colors.get())
        self.pyplot_utils.set_n_colors(n_colors)
        self.update_plot()

    def update_plot(self):
        if len(self.variables.plot_data.shape) < 3:
            self.pyplot_canvas.canvas.draw()
        elif self.variables.plot_data is not None:
            n_overplots = numpy.shape(self.variables.segments)[0]
            animation_index = int(self.control_panel.scale.get())

            for i in range(n_overplots):
                self.variables.segments[i, :, 1] = self.variables.plot_data[:, i, animation_index]

            self.pyplot_canvas.axes.clear()

            self.pyplot_canvas.axes.set_xlim(self.variables.xmin, self.variables.xmax)
            line_segments = LineCollection(self.variables.segments,
                                           self.pyplot_utils.linewidths,
                                           linestyle=self.pyplot_utils.linestyle)
            line_segments.set_color(self.pyplot_utils.rgb_array_full_palette)
            if self.variables.set_y_margins_per_frame:
                plot_data = self.variables.segments[:, :, 1]
                y_range = plot_data.max() - plot_data.min()
                self.variables.ymin = plot_data.min() - y_range * self.variables.y_margin
                self.variables.ymax = plot_data.max() + y_range * self.variables.y_margin
            self.pyplot_canvas.axes.set_ylim(self.variables.ymin, self.variables.ymax)

            self.pyplot_canvas.axes.add_collection(line_segments)
            self.pyplot_canvas.canvas.draw()
        else:
            pass
