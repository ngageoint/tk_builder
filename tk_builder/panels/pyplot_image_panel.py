import logging
from matplotlib import pyplot
import numpy
import tkinter

from tk_builder.widgets import basic_widgets

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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


class PyplotImagePanel(basic_widgets.LabelFrame):
    """
    Provides a widget that allows users to embed pyplot images into an application.
    """

    def __init__(self, parent, cmap_name=DEFAULT_CMAP):
        self._cmap_name = DEFAULT_CMAP
        basic_widgets.LabelFrame.__init__(self, parent)
        self.config(borderwidth=5)
        self.cmap_name = cmap_name
        self.fig, self.ax = pyplot.subplots(dpi=100, nrows=1, ncols=1)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.make_blank()
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

    def update_image(self, image_data, **kwargs):
        """
        Updates the displayed image.  Image data should be an numpy array of dimensions:
        [ny, nx] for a grayscale image or [ny, nx, 3] for a 3 color RGB image.

        Parameters
        ----------
        image_data: numpy.ndarray
        kwargs
            Optional key word arguments for `imshow`

        Returns
        -------
        str
        """

        self.image_data = image_data
        if image_data.ndim != 3 and 'cmap' not in kwargs:
            kwargs['cmap'] = self.cmap_name

        self.ax.imshow(self.image_data, **kwargs)
        self.canvas.draw()

    def set_xlabel(self, the_label):
        """
        Sets the displayed x label.

        Parameters
        ----------
        the_label : str
        """

        self.ax.set_xlabel(the_label)

    def set_ylabel(self, the_label):
        """
        Sets the displayed y label.

        Parameters
        ----------
        the_label : str
        """

        self.ax.set_ylabel(the_label)

    def set_title(self, the_title):
        """
        Sets the displayed figure title.

        Parameters
        ----------
        the_title : str
        """

        self.ax.set_title(the_title)

    def destroy(self):
        pyplot.close(self.fig)
        basic_widgets.LabelFrame.destroy(self)
