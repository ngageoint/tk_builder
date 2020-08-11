from tk_builder.widgets.image_canvas import ImageCanvas
from tk_builder.widgets.axes_image_canvas import AxesImageCanvas


class ImageFrame(ImageCanvas):
    def __init__(self,
                 parent,
                 ):
        ImageCanvas.__init__(self, parent)
        self.parent = parent
        self.outer_canvas = AxesImageCanvas(self)
        self.outer_canvas.pack()
