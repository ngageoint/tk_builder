
__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class ImageReader(object):
    """
    An abstract image reader class, intended to layout the basic elements for
    providing image data to Image Canvas Objects.

    Any subclasses must implement `__getitem__` to support 2 element slice parsing
    (i.e. :code:`data = ImageReader[start_0:end_0:step_0, start1:end1:step1]`)

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

    def set_remap_type(self, remap_type):
        """
        Sets a remap function, for mapping the raw underlying data to an 8-bit image.
        This only applies to the situation in which the data is not already 8-bit.

        Parameters
        ----------
        remap_type : str|callable

        Returns
        -------
        None
        """

        pass
