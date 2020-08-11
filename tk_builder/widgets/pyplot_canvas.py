import tkinter
import logging
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except ImportError:
    logging.error('Failed importing FigureCanvasTkAgg from matplotlib. This is likely '
                  'because the matplotlib in your environment was not built with tkinter '
                  'backend support enabled. No functionality for the pyplot panel '
                  'will be functional.')
    FigureCanvasTkAgg = None
from matplotlib.figure import Figure


class PyplotCanvas(tkinter.LabelFrame):
    def __init__(self, primary):
        tkinter.LabelFrame.__init__(self, primary)
        fig = Figure()
        self.ax = fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(fig, primary)
        self.canvas.get_tk_widget().pack(fill='both')
