import PIL.Image
from typing import List

import numpy

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


def save_numpy_frame_sequence_to_animated_gif(frame_sequence, fname, fps=15, loop_animation=True):
    """
    Save a sequence of numpy arrays to an animated gif.

    Parameters
    ----------
    frame_sequence : List[numpy.ndarray]
        The sequence of numpy arrays.
    fname : str
        The path for the output file.
    fps : float|int
        The frames per second of the gif.
    loop_animation : bool
        Should the animation be looped?

    Returns
    -------
    None
    """

    duration = (1 / fps) * 1000
    pil_frame_sequence = [PIL.Image.fromarray(frame) for frame in frame_sequence]

    if loop_animation:
        pil_frame_sequence[0].save(fname,
                                   save_all=True,
                                   append_images=pil_frame_sequence[1:],
                                   optimize=True,
                                   duration=duration,
                                   loop=0)
    else:
        pil_frame_sequence[0].save(fname,
                                   save_all=True,
                                   append_images=pil_frame_sequence[1:],
                                   optimize=True,
                                   duration=duration)
