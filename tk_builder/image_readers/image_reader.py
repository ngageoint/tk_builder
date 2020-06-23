import numpy


class ImageReader:
    """
    Abstract image reader class
    """
    # TODO: use descriptors here
    fname = ''  # type: str
    full_image_nx = 0   # type: int
    full_image_ny = 0   # type: int

    def __getitem__(self, key):
        raise NotImplementedError
