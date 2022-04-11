from matplotlib import pyplot
import tkinter

from tk_builder.widgets.basic_widgets import Frame

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

__classification__ = "UNCLASSIFIED"
__author__ = "Thomas McCullough"


class PyplotFrame(Frame):
    """
    Simply allows for the creation of tkinter Frame containing the pyplot Figure
    instance provided. It is expected that all other object support will be
    handled external to this class.
    """

    def __init__(self, parent, fig, navigation=True, **kwargs):
        """

        Parameters
        ----------
        parent
        fig : pyplot.Figure
        """

        Frame.__init__(self, parent, **kwargs)
        self.fig = fig
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)
        if navigation:
            self.toolbar = NavigationToolbar2Tk(self.canvas, parent)
            self.toolbar.update()
            self.canvas.get_tk_widget().pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)
        else:
            self.toolbar = None
        self.pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.canvas.draw()

    def destroy(self):
        pyplot.close(self.fig)
        Frame.destroy(self)
