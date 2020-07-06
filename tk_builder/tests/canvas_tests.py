import unittest

from tk_builder.widgets.image_canvas import ImageCanvas
from tk_builder.widgets.image_canvas import CanvasImage
from tk_builder.tests.test_utils import image_canvas_utils
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

    # TODO: there are some conflicting things to take care of with how either the image canvas or canvas image object
    # TODO: handle rescaling to fit the canvas or not.
    def test_display_image_init_w_numpy_not_scaled_to_fit(self):
        image_data = np.zeros((self.image_ny, self.image_nx))
        numpy_reader = NumpyImageReader(image_data)
        image_canvas = ImageCanvas(None)
        image_canvas.set_canvas_size(self.canvas_nx, self.canvas_ny)
        canvas_image = CanvasImage(numpy_reader, self.canvas_nx, self.canvas_ny)
        image_canvas.variables.canvas_image_object = canvas_image
        image_canvas.variables.canvas_image_object.scale_to_fit_canvas = False
        image_canvas.variables.rescale_image_to_fit_canvas = False

        display_image = image_canvas.variables.canvas_image_object.display_image
        display_ny, display_nx = np.shape(display_image)
        assert display_ny > image_canvas.variables.canvas_height or display_nx > image_canvas.variables.canvas_width
        print("")
        print("display image is larger or equal to the canvas size")
        print("test passed")


    #TODO: handle case for non integer values for canvas rect
    def test_image_in_rect_after_zoom(self):
        image_data = np.zeros((self.image_ny, self.image_nx))
        numpy_reader = NumpyImageReader(image_data)
        image_canvas = ImageCanvas(None)
        image_canvas.set_canvas_size(self.canvas_nx, self.canvas_ny)
        canvas_image = CanvasImage(numpy_reader, self.canvas_nx, self.canvas_ny)
        image_canvas.variables.canvas_image_object = canvas_image

        full_image_decimation = image_canvas.variables.canvas_image_object.decimation_factor
        image_canvas_utils.create_new_rect_on_image_canvas(image_canvas, 50, 50)
        rect_id = image_canvas.variables.current_shape_id
        image_canvas.modify_existing_shape_using_canvas_coords(rect_id, (50, 50, 300, 200), update_pixel_coords=True)
        before_zoom_image_in_rect = image_canvas.get_image_data_in_canvas_rect_by_id(rect_id)
        zoom_rect = (20, 20, 100, 100)
        image_canvas.zoom_to_selection(zoom_rect, animate=False)
        zoomed_image_decimation = image_canvas.variables.canvas_image_object.decimation_factor
        after_zoom_image_in_rect = image_canvas.get_image_data_in_canvas_rect_by_id(rect_id)
        assert (after_zoom_image_in_rect == before_zoom_image_in_rect).all()
        assert full_image_decimation != zoomed_image_decimation
        print("")
        print("decimation factors at zoomed out and zoomed in levels are different.")
        print("getting image data in rect is consistent at both zoomed out and zoomed in views")
        print("test passed.")


if __name__ == '__main__':
    unittest.main()
