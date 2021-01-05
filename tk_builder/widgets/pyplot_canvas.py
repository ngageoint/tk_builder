__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


import logging
import tkinter
from matplotlib import pyplot

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    logging.error('Failed importing FigureCanvasTkAgg from matplotlib. This is likely '
                  'because the matplotlib in your environment was not built with tkinter '
                  'backend support enabled. No functionality for the pyplot panel '
                  'will be functional.')
    FigureCanvasTkAgg = None




class PyplotCanvas(tkinter.Frame):
    def __init__(self, parent, canvas_width=600, canvas_height=400):
        tkinter.Frame.__init__(self, parent)

        # default dpi is 100, so npix will be 100 times the numbers passed to figsize
        self.fig = pyplot.figure(figsize=(canvas_width/100, canvas_height/100))
        pyplot.plot(0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill='both')
        toolbar = self.canvas.toolbar

    @property
    def axes(self):
        return self.fig.axes[0]
