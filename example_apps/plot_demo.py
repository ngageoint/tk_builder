import tkinter
from tk_builder.panels.pyplot_panel import PyplotPanel
from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets import basic_widgets
import numpy as np


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

        Parameters
        ----------
        event

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

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        plot_data = self.mockup_animation_data_2()
        data_shape = np.shape(plot_data)
        x_axis_points = data_shape[0]
        n_overplots = data_shape[1]
        print("plot data has dimensions of: " + str(data_shape))
        print("with " + str(x_axis_points) + " data points along the x axis")
        print("and " + str(n_overplots) + " overplots")
        self.pyplot_panel.set_data(plot_data)

    def animated_plot(self):
        """
        Animated callback plot.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        plot_data = self.mockup_animation_data_3()
        data_shape = np.shape(plot_data)
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
        np.ndarray
        """

        n_overplots = 10
        nx = 200
        n_times = 100

        x_axis = np.linspace(0, np.pi, nx)
        y_data_1 = np.sin(x_axis)
        y_data_2 = np.zeros((len(x_axis), n_overplots))
        y_data_3 = np.zeros((len(x_axis), n_overplots, n_times))

        scaling_factors = np.linspace(0.7, 1, n_overplots)

        for i in range(n_overplots):
            y_data_2[:, i] = y_data_1 * scaling_factors[i]

        x_over_time = np.zeros((nx, n_times))
        x_over_time_start = np.linspace(0, np.pi, n_times)
        for i in range(n_times):
            x_start = x_over_time_start[i]
            x = np.linspace(x_start, np.pi + x_start, nx)
            x_over_time[:, i] = x
            y = np.sin(x)
            for j in range(n_overplots):
                y_data_3[:, j, i] = y * scaling_factors[j]
        return y_data_3

    @staticmethod
    def mockup_animation_data_2():
        """
        Mock animation.

        Returns
        -------
        np.ndarray
        """

        n_overplots = 10
        nx = 200

        x_axis = np.linspace(0, 2 * np.pi, nx)
        y_data_1 = x_axis
        y_data_2 = np.zeros((len(x_axis), n_overplots))

        scaling_factors = np.linspace(0.7, 1, n_overplots)

        for i in range(n_overplots):
            y_data_2[:, i] = y_data_1 * scaling_factors[i]

        return y_data_2

    @staticmethod
    def mockup_animation_data_1():
        """
        Mock animation.

        Returns
        -------
        np.ndarray
        """

        x = np.linspace(-5, 5, 200)
        y = np.sinc(x)
        return y


if __name__ == '__main__':
    root = tkinter.Tk()
    app = PlotDemo(root)
    root.mainloop()
