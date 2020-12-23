
__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class ImageReader(object):
    """
    An abstract image reader class, intended to layout the basic elements for
    providing image data to Image Canvas Objects.

    The subclasses of ImagReader
    should implement __getitem__, which should return a numpy array in one of the following formats:
    array[ny, nx]
    array[ny, nx, 3]
    array[ny, nx, 4]
    Where ny is the number of rows for the image to be displayed, and nx is the number of columns.
    The image arrays should be of datatype numpy.uint8
    In the first case, the image to be displayed is a grayscale image
    In the second case, the image is a 3 color RGB image with no transparency
    In the third case, the image is a 4 channel RGBA image where the 4th channel is the transparency layer
    """

    __slots__ = ('_data_size', )

    @property
    def data_size(self):
        # type: () -> (int, int)
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
