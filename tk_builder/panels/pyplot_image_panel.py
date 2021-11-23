import logging
from matplotlib import pyplot
import numpy
import tkinter

from tk_builder.widgets.basic_widgets import Frame

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
except ImportError:
    logging.error(
        'Failed importing FigureCanvasTkAgg from matplotlib. This is likely '
        'because the matplotlib in your environment was not built with tkinter '
        'backend support enabled. No functionality for the pyplot panel '
        'will be functional.')
    FigureCanvasTkAgg = None


__classification__ = "UNCLASSIFIED"
__author__ = ("Jason Casey", "Thomas McCullough")

DEFAULT_CMAP = 'bone'


class PyplotImagePanel(Frame):
    """
    Provides a widget that allows users to embed pyplot images into an application.
    """

    def __init__(self, parent, cmap_name=DEFAULT_CMAP, navigation=False):
        self._cmap_name = DEFAULT_CMAP
        Frame.__init__(self, parent)
        self.config(borderwidth=5)
        self.cmap_name = cmap_name
        self.x_label = None
        self.y_label = None
        self.title = None
        self.fig, self.ax = pyplot.subplots(dpi=100, nrows=1, ncols=1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)
        if navigation:
            self.toolbar = NavigationToolbar2Tk(self.canvas, parent)
            self.toolbar.update()
            self.canvas.get_tk_widget().pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)
        else:
            self.toolbar = None

        self.make_blank()
        self.set_title('detailed view')
        self.set_ylabel('row')
        self.set_xlabel('column')
        self.ax.grid(False)
        self.pack(expand=tkinter.YES, fill=tkinter.BOTH)

    def make_blank(self):
        image_data = numpy.zeros((600, 400), dtype='uint8')
        self.update_image(image_data)

    @property
    def cmap_name(self):
        """
        str: The matplotlib colormap to apply, in the case of monochromatic image data
        """

        return self._cmap_name

    @cmap_name.setter
    def cmap_name(self, value):
        if value in pyplot.colormaps():
            self._cmap_name = value
        else:
            self._cmap_name = DEFAULT_CMAP
            logging.error(
                'cmap_name {} is not in the pyplot list of registered colormaps. '
                'Using the default.'.format(value))

    def clear(self):
        """
        Clear the axes contents.
        """

        self.ax.cla()
        self.ax.grid(False)
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.set_aspect('auto')  # this is for safety, because it gets implicitly set with imshow

    def update_image(self, image_data, **kwargs):
        """
        Updates the displayed image.

        Parameters
        ----------
        image_data: numpy.ndarray
            An array of dimensions (ny, nx) or (ny, nx, 3)
        kwargs
            Optional key word arguments for :func:`imshow`
        """

        if image_data.ndim != 3 and 'cmap' not in kwargs:
            kwargs['cmap'] = self.cmap_name
        self.clear()
        self.ax.imshow(image_data, **kwargs)
        self.canvas.draw()

    def update_pcolormesh(self, x_array, y_array, image_data, **kwargs):
        """
        Updates the display using pcolormesh.

        Parameters
        ----------
        x_array : numpy.ndarray
            An array of dimensions (nx, )
        y_array : numpy.ndarray
            An array of dimensions (ny, )
        image_data : numpy.ndarray
            An array of dimensions (ny, nx)
        kwargs
            Optional key word arguments for :func:`pcolormesh`
        """

        if 'cmap' not in kwargs:
            kwargs['cmap'] = self.cmap_name
        self.clear()
        self.ax.pcolormesh(x_array, y_array, image_data, **kwargs)
        self.canvas.draw()

    def set_xlabel(self, the_label):
        """
        Sets the displayed x label.

        Parameters
        ----------
        the_label : str
        """
        self.x_label = the_label
        self.ax.set_xlabel(the_label)

    def set_ylabel(self, the_label):
        """
        Sets the displayed y label.

        Parameters
        ----------
        the_label : str
        """

        self.y_label = the_label
        self.ax.set_ylabel(the_label)

    def set_title(self, the_title):
        """
        Sets the displayed figure title.

        Parameters
        ----------
        the_title : str
        """

        self.title = the_title
        self.ax.set_title(the_title)

    def destroy(self):
        pyplot.close(self.fig)
        Frame.destroy(self)
