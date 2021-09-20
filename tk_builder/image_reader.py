"""
Sets out the main interface for something which provides image data.
"""

__classification__ = "UNCLASSIFIED"
__author__ = ("Jason Casey", "Thomas McCullough")

import numpy
from typing import Tuple, Union, Callable


class CanvasImageReader(object):
    """
    An abstract image reader class, intended to layout the basic elements for
    providing image data to Image Canvas Objects.

    Any subclasses must implement `__getitem__` to support 2 element slice parsing
    (i.e. :code:`data = CanvasImageReader[start_0:end_0:step_0, start1:end1:step1]`)

    It is assumed that `__getitem__` will return a numpy array of some real dtype of
    one of these shapes:
        * (ny, nx) - monochromatic image
        * (ny, nx, 3) - RGB image
        * (ny, nx, 4) - RGBA image, may be strange plotting results if not dtype uint8

    Note that RGB or RGBA images of dtype other than `uint8` may result in unexpected
    plotting results.
    """

    __slots__ = ('_data_size', )

    @property
    def data_size(self):
        # type: () -> Tuple[int, int]
        """
        (int, int): This defines the row, column bounds for the underlying image.
        """

        return self._data_size

    @property
    def full_image_ny(self):
        """
        int: The size of the first image index - called row by SICD convention.
        """

        return self.data_size[0]

    @property
    def full_image_nx(self):
        """
        int: The size of the second image index - called column by SICD convention.
        """

        return self.data_size[1]

    @property
    def file_name(self):
        # type: () -> Union[None, str, Tuple[str]]
        """
        None|str|Tuple[str]: The filename(s) for the given images.
        """

        raise NotImplementedError

    @property
    def remapable(self):
        """
        bool: Does this support any remap operations?
        """

        raise NotImplementedError

    @property
    def remap_function(self):
        # type: () -> Union[None, Callable]
        """
        None|Callable: The current remap function. This will be `None`, if `remapable` is False.
        """

        raise NotImplementedError

    @property
    def image_count(self):
        """
        int: The number of image segments.
        """

        raise NotImplementedError

    @property
    def index(self):
        """
        int: The index of the selected image segment.
        """

        raise NotImplementedError

    @index.setter
    def index(self, value):
        raise NotImplementedError

    def __getitem__(self, item):
        """
        This is expected to accompany a basic two element slice, with bounds
        given by the `data_size` property.

        Parameters
        ----------
        item
            Automatically parsed from two element slice usage :code:`reader[start0:end0:step0, start1:end1:step1]

        Returns
        -------
        numpy.ndarray
            The interpretation of the output is 8-bit imagery expected to be one of the following:
            array[ny, nx] - intended to be shown at grey-scale
            array[ny, nx, 3] - intended to be shown as RGB
            array[ny, nx, 4] - intended to be shown as RGBA
        """

        raise NotImplementedError

    def set_remap_type(self, remap_type):
        """
        Sets a remap function, for mapping the raw underlying data to an 8-bit image.
        This only applies to the situation in which the data is not already 8-bit.

        Parameters
        ----------
        remap_type : str|Callable

        Returns
        -------
        None
        """

        pass


class NumpyCanvasImageReader(CanvasImageReader):
    """
    CanvasImageReader for numpy array data. This requires a two or
    three dimensional array of one of the basic real dtypes. If three dimensional,
    the final dimension must have size 3 or 4.
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

        self.numpy_image_data = numpy_image_data
        self._data_size = numpy_image_data.shape[:2]

    @property
    def file_name(self):
        return None

    def __getitem__(self, key):
        return self.numpy_image_data[key]

    @property
    def remapable(self):
        return False

    @property
    def remap_function(self):
        return None

    @property
    def image_count(self):
        return 1

    @property
    def index(self):
        return 0
