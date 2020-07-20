import tkinter
from tk_builder.widgets import basic_widgets
from tk_builder.widgets.axes_image_canvas import AxesImageCanvas


class ImageFrame(basic_widgets.Frame):
    def __init__(self,
                 parent,
                 ):
        ImageFrame.__init__(self, parent)
        self.image_canvas = AxesImageCanvas(self)
        self.image_canvas.pack()