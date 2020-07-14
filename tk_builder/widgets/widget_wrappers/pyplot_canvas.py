import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class PyplotCanvas(tkinter.LabelFrame):
    def __init__(self, primary):
        tkinter.LabelFrame.__init__(self, primary)
        fig = Figure()
        self.ax = fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(fig, primary)
        self.canvas.get_tk_widget().pack(fill='both')
