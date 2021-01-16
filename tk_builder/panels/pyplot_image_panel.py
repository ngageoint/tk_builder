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
__author__ = "Jason Casey"


DEFAULT_CMAP = 'bone'


class PyplotImagePanel(basic_widgets.LabelFrame):
    """
    Provides a widget that allows users to embed pyplot images into an application.
    """

    def __init__(self, parent, canvas_width=600, canvas_height=400, cmap_name=DEFAULT_CMAP):
        self._cmap_name = DEFAULT_CMAP
        basic_widgets.LabelFrame.__init__(self, parent)
        self.config(borderwidth=5)

        # this is a dummy placeholder for now
        self.image_data = numpy.zeros((canvas_height, canvas_width), dtype='uint8')
        self.cmap_name = cmap_name
        # default dpi is 100, so npix will be 100 times the numbers passed to figsize
        # fig = plt.figure(figsize=(canvas_width/100, canvas_height/100))
        self.fig, self.ax = pyplot.subplots(nrows=1, ncols=1)
        self.ax.imshow(self.image_data, cmap=self.cmap_name)
        self.ax.set_ylabel('row')
        self.ax.set_xlabel('column')
        self.ax.grid(False)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.update_image(self.image_data)
        self.pack(expand=tkinter.YES, fill=tkinter.BOTH)

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

    def destroy(self):
        pyplot.close(self.fig)
        super(PyplotImagePanel, self).destroy()
