from tk_builder.image_readers.image_reader import ImageReader
import numpy


class NumpyImageReader(ImageReader):
    fname = None
    full_image_nx = int
    full_image_ny = int
    numpy_image_data = None     # type: numpy.ndarray

    def __init__(self, numpy_image_data):
        """
        This is an sublass and implementation of ImageReader.  When initializing, numpy_image_data should be an
        array of dimensions:
        [ny, nx] - for a grayscale image
        [ny, nx, 3] - for a 3 color RGB image
        [ny, nx, 4] - for a 4 channel RGBA image (3 color RGB with alpha layer)

        Parameters
        ----------
        numpy_image_data : numpy.ndarray
        """

        self.numpy_image_data = numpy_image_data
        self.full_image_ny, self.full_image_nx = numpy_image_data.shape

    def __getitem__(self, key):
        return self.numpy_image_data[key]
