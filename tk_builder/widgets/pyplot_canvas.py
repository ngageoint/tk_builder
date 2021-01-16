__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


import logging
from matplotlib import pyplot

from tk_builder.widgets.basic_widgets import Frame

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    logging.error('Failed importing FigureCanvasTkAgg from matplotlib. This is likely '
                  'because the matplotlib in your environment was not built with tkinter '
                  'backend support enabled. No functionality for the pyplot panel '
                  'will be functional.')
    FigureCanvasTkAgg = None


class PyplotCanvas(Frame):
    def __init__(self, parent, canvas_width=600, canvas_height=400, **kwargs):
        Frame.__init__(self, parent, **kwargs)

        # default dpi is 100, so npix will be 100 times the numbers passed to figsize
        self.fig = pyplot.figure(dpi=100, figsize=(canvas_width/float(100), canvas_height/float(100)))
        pyplot.plot(0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill='both')

    @property
    def axes(self):
        return self.fig.axes[0]
