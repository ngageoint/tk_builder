"""
GUI color utilities.
"""

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


import numpy
import tk_builder.utils.color_utils.color_converter as color_converter


def get_full_rgb_palette(rgb_palette, n_colors=None):
    """
    Gets full RGB color palette.

    Parameters
    ----------
    rgb_palette : List[List[float]]
    n_colors : int

    Returns
    -------
    List[List[float]]
    """

    if n_colors is None:
        n_colors = len(rgb_palette)
    color_array = []
    n_color_bins = len(rgb_palette)
    indices = numpy.linspace(0, n_colors, n_colors)
    for i in indices:
        index = i / n_colors * (n_color_bins - 1)
        low = int(index)
        high = int(numpy.ceil(index))
        interp_float = index - low
        color_array.append(
            list(numpy.array(rgb_palette[low]) * (1 - interp_float) + numpy.array(rgb_palette[high]) * interp_float))
    return color_array


def get_full_hex_palette(hex_palette, n_colors=None):
    """
    Gets full hexidecimal palette.

    Parameters
    ----------
    hex_palette : List[str]
    n_colors : int

    Returns
    -------
    List[str]
    """

    rgb_palette = color_converter.hex_list_to_rgb_list(hex_palette)
    rgb_full = get_full_rgb_palette(rgb_palette, n_colors)
    hex_full = color_converter.rgb_list_to_hex_list(rgb_full)
    return hex_full
