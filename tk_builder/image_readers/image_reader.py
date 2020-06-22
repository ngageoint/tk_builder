import numpy


class ImageReader:
    """
    Abstract image reader class
    """

    fname = str
    full_image_nx = int
    full_image_ny = int

    def __getitem__(self, key):
        raise NotImplementedError
