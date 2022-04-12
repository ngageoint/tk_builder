"""
Basic pass-through functionality for matplotlib/pyplot
"""

import logging
from matplotlib import pyplot
import tkinter

import numpy

from tk_builder.widgets.basic_widgets import Frame

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2Tk


__classification__ = "UNCLASSIFIED"
__author__ = "Thomas McCullough"


DEFAULT_CMAP = 'bone'
logger = logging.getLogger(__name__)


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
        navigation : bool
        kwargs
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

    def draw(self):
        """
        Pass-through draw method.
        """

        self.canvas.draw()

    def destroy(self):
        pyplot.close(self.fig)
        Frame.destroy(self)


class PyplotImagePanel(PyplotFrame):
    """
    Provides a widget that allows users to embed pyplot images into an application.
    """

    def __init__(self, parent, cmap_name=DEFAULT_CMAP, navigation=False):
        """

        Parameters
        ----------
        parent
        cmap_name : str
        navigation : bool
        """

        self._cmap_name = DEFAULT_CMAP
        self.x_label = None
        self.y_label = None
        self.title = None
        fig, self.ax = pyplot.subplots(dpi=100, nrows=1, ncols=1)
        PyplotFrame.__init__(self, parent, fig, navigation=navigation)

        self.cmap_name = cmap_name
        self.make_blank()
        self.set_title('detailed view')
        self.set_ylabel('row')
        self.set_xlabel('column')
        self.ax.grid(False)

    def make_blank(self):
        """
        Clear the contents of the image panel, and make it blank placeholder.
        """

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
            logger.error(
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
        self.draw()

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
        self.draw()

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
