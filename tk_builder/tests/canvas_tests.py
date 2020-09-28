import unittest

from tk_builder.widgets.image_canvas import ImageCanvas
from tk_builder.widgets.image_canvas import CanvasImage
from tk_builder.image_readers.numpy_image_reader import NumpyImageReader
import numpy as np

# TODO: ERROR - this test looks broken?


class ImageCanvasTests(unittest.TestCase):
    canvas_nx = 2027
    canvas_ny = 1013

    image_nx = 2028
    image_ny = 1020

    def test_display_image_init_w_numpy_scaled_to_fit(self):
        image_data = np.zeros((self.image_ny, self.image_nx))
        numpy_reader = NumpyImageReader(image_data)
        image_canvas = ImageCanvas(None)
        image_canvas.set_canvas_size(self.canvas_nx, self.canvas_ny)
        canvas_image = CanvasImage(numpy_reader, self.canvas_nx, self.canvas_ny)
        image_canvas.variables.canvas_image_object = canvas_image

        display_image = image_canvas.variables.canvas_image_object.display_image
        display_ny, display_nx = np.shape(display_image)
        assert display_ny <= image_canvas.variables.canvas_height
        assert display_nx <= image_canvas.variables.canvas_width
        assert display_ny == image_canvas.variables.canvas_height or display_nx == image_canvas.variables.canvas_width
        print("")
        print("display image is smaller or equal to the canvas size")
        print("one of the x or y dimensions of the display image matches the canvas")
        print("test passed")


if __name__ == '__main__':
    unittest.main()
