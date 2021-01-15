import tkinter
from tkinter import ttk
import numpy

from tk_builder.panels.pyplot_panel import PyplotPanel
from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets import basic_widgets


class ButtonPanel(WidgetPanel):
    """
    Basic button panel.
    """
    _widget_list = ("single_plot", "multi_plot", "animated_plot")
    single_plot = widget_descriptors.ButtonDescriptor("single_plot")  # type: basic_widgets.Button
    multi_plot = widget_descriptors.ButtonDescriptor("multi_plot")  # type: basic_widgets.Button
    animated_plot = widget_descriptors.ButtonDescriptor("animated_plot")  # type: basic_widgets.Button

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent
            The parent widget.
        """

        WidgetPanel.__init__(self, parent)
        self.init_w_horizontal_layout()


class PlotDemo(WidgetPanel):
    """
    Basic plot demo gui.
    """
    _widget_list = ("button_panel", "pyplot_panel")
    button_panel = widget_descriptors.PanelDescriptor(
        "button_panel", ButtonPanel, default_text="plot buttons")    # type: ButtonPanel
    pyplot_panel = widget_descriptors.PyplotPanelDescriptor("pyplot_panel")      # type: PyplotPanel

    def __init__(self, primary):
        """

        Parameters
        ----------
        primary
            The primary widget.
        """

        # set the primary frame
        primary_frame = tkinter.Frame(primary)
        WidgetPanel.__init__(self, primary_frame)
        self.init_w_vertical_layout()

        # need to pack both primary frame and self, since this is the main app window.
        primary_frame.pack()

        # set up event listeners
        self.button_panel.single_plot.config(command=self.single_plot)
        self.button_panel.multi_plot.config(command=self.multi_plot)
        self.button_panel.animated_plot.config(command=self.animated_plot)

        self.pyplot_panel.set_y_margin_percent(5)
        self.pyplot_panel.variables.set_y_margins_per_frame = True

        self.single_plot()

        self.pyplot_panel.show_control_panel()

    def single_plot(self):
        """
        A single plot callback.

        Returns
        -------
        None
        """

        plot_data = self.mockup_animation_data_1()
        self.pyplot_panel.set_data(plot_data)
        self.pyplot_panel.title = "single plot"

    def multi_plot(self):
        """
        A multiplot callback.

        Returns
        -------
        None
        """

        plot_data = self.mockup_animation_data_2()
        data_shape = numpy.shape(plot_data)
        x_axis_points = data_shape[0]
        n_overplots = data_shape[1]
        print("plot data has dimensions of: " + str(data_shape))
        print("with " + str(x_axis_points) + " data points along the x axis")
        print("and " + str(n_overplots) + " overplots")
        self.pyplot_panel.set_data(plot_data)

    def animated_plot(self):
        """
        Animated callback plot.

        Returns
        -------
        None
        """

        plot_data = self.mockup_animation_data_3()
        data_shape = numpy.shape(plot_data)
        x_axis_points = data_shape[0]
        n_overplots = data_shape[1]
        n_animation_frames = data_shape[2]
        print("plot data has dimensions of: " + str(data_shape))
        print("with " + str(x_axis_points) + " data points along the x axis")
        print("and " + str(n_overplots) + " overplots")
        print("and " + str(n_animation_frames) + " animation frames")
        self.pyplot_panel.set_data(plot_data)

    @staticmethod
    def mockup_animation_data_3():
        """
        Mock annimation.

        Returns
        -------
        numpy.ndarray
        """

        n_overplots = 10
        nx = 200
        n_times = 100

        x_axis = numpy.linspace(0, numpy.pi, nx)
        y_data_1 = numpy.sin(x_axis)
        y_data_2 = numpy.zeros((len(x_axis), n_overplots))
        y_data_3 = numpy.zeros((len(x_axis), n_overplots, n_times))

        scaling_factors = numpy.linspace(0.7, 1, n_overplots)

        for i in range(n_overplots):
            y_data_2[:, i] = y_data_1 * scaling_factors[i]

        x_over_time = numpy.zeros((nx, n_times))
        x_over_time_start = numpy.linspace(0, numpy.pi, n_times)
        for i in range(n_times):
            x_start = x_over_time_start[i]
            x = numpy.linspace(x_start, numpy.pi + x_start, nx)
            x_over_time[:, i] = x
            y = numpy.sin(x)
            for j in range(n_overplots):
                y_data_3[:, j, i] = y * scaling_factors[j]
        return y_data_3

    @staticmethod
    def mockup_animation_data_2():
        """
        Mock animation.

        Returns
        -------
        numpy.ndarray
        """

        n_overplots = 10
        nx = 200

        x_axis = numpy.linspace(0, 2 * numpy.pi, nx)
        y_data_1 = x_axis
        y_data_2 = numpy.zeros((len(x_axis), n_overplots))

        scaling_factors = numpy.linspace(0.7, 1, n_overplots)

        for i in range(n_overplots):
            y_data_2[:, i] = y_data_1 * scaling_factors[i]

        return y_data_2

    @staticmethod
    def mockup_animation_data_1():
        """
        Mock animation.

        Returns
        -------
        numpy.ndarray
        """

        x = numpy.linspace(-5, 5, 200)
        y = numpy.sinc(x)
        return y


def main():
    root = tkinter.Tk()

    the_style = ttk.Style()
    the_style.theme_use('clam')

    app = PlotDemo(root)
    root.mainloop()


if __name__ == '__main__':
    main()
