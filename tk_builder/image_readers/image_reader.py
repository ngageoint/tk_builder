
__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class ImageReader:
    """
    Abstract image reader class
    This is the image reader class that provides imagery to Image Canvas Objects.  Specific image readers
    that will provide imagery to an image canvas should be a subclass of ImageReader.  The subclasses of ImagReader
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
    # TODO: use descriptors here
    fname = ''  # type: str
    full_image_nx = 0   # type: int
    full_image_ny = 0   # type: int

    def __getitem__(self, key):
        raise NotImplementedError
