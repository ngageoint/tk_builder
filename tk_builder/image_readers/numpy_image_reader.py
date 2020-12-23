from tk_builder.image_readers.image_reader import ImageReader
import numpy

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class NumpyImageReader(ImageReader):
    """
    Simple extension for ImageReader for numpy array data. This requires a two or
    three dimensional array of dtype uint8. If three diemnsional, the final dimension
    must have size 3 or 4.
    """

    def __init__(self, numpy_image_data):
        """

        Parameters
        ----------
        numpy_image_data : numpy.ndarray
        """

        if not isinstance(numpy_image_data, numpy.ndarray):
            raise TypeError('Expected numpy.ndarray, got type {}'.format(type(numpy_image_data)))
        if numpy_image_data.ndim not in [2, 3]:
            raise ValueError('Expected input to have dimension 2 or 3.')
        if numpy_image_data.ndim == 3 and numpy_image_data.shape[2] not in [3, 4]:
            raise ValueError('Input is 2-d, bu the final dimension is not size 3 or 4.')
        if numpy_image_data.dtype.name != 'uint8':
            raise ValueError('Input is of datatype {}, required to be uint8.'.format(numpy_image_data.dtype.name))

        self.numpy_image_data = numpy_image_data
        self._data_size = numpy_image_data.shape[:2]

    def __getitem__(self, key):
        return self.numpy_image_data[key]
