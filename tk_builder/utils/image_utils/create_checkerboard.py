import numpy

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


def create_checkerboard(square_size,  # type: int
                        n_squares_x,  # type: int
                        n_squares_y,  # type: int
                        ):
    ny = square_size * n_squares_y
    nx = square_size * n_squares_x
    checkerboard_array = numpy.zeros((ny, nx))
    pattern_1 = numpy.repeat(numpy.tile((1, 0), int(n_squares_x/2)), square_size)
    pattern_2 = numpy.repeat(numpy.tile((0, 1), int(n_squares_x/2)), square_size)
    for i in range(ny):
        checkerboard_array[i, :] = pattern_1
    for i in range(square_size):
        indices = numpy.arange(square_size + i, ny, square_size*2)
        for index in indices:
            checkerboard_array[index, :] = pattern_2
    return checkerboard_array
