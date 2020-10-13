import logging
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    logging.error('Failed importing FigureCanvasTkAgg from matplotlib. This is likely '
                  'because the matplotlib in your environment was not built with tkinter '
                  'backend support enabled. No functionality for the pyplot panel '
                  'will be functional.')
    FigureCanvasTkAgg = None

import matplotlib.pyplot as plt
import numpy
from numpy import ndarray
import tkinter


class PyplotImagePanel(tkinter.LabelFrame):
    """
    Pyplot Image Panel class.  This essentially provides a widget that allows users to embed pyplot images into
    an application.
    """
    def __init__(self, parent, canvas_width=600, canvas_height=400):
        tkinter.LabelFrame.__init__(self, parent)
        self.config(highlightbackground="black")
        self.config(highlightthickness=1)
        self.config(borderwidth=5)

        # this is a dummy placeholder for now
        self.image_data = numpy.zeros((canvas_height, canvas_width))

        # default dpi is 100, so npix will be 100 times the numbers passed to figsize
        # fig = plt.figure(figsize=(canvas_width/100, canvas_height/100))
        fig = plt.figure()

        plt.imshow(self.image_data)
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.update_image(self.image_data)
        self.pack(expand=tkinter.YES, fill=tkinter.BOTH)

    def update_image(self, image_data):
        """
        Updates the displayed image.  Image data should be an ndarray of dimensions: [ny, nx] for a grayscale image
        or [ny, nx, 3] for a 3 color RGB image.

        Parameters
        ----------
        image_data: ndarray

        Returns
        -------
        str
        """
        self.image_data = image_data
        plt.imshow(self.image_data)
        self.canvas.draw()
