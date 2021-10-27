"""
A coolection of basic color utils
"""

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"

import numpy

from matplotlib import colors

SEABORN_PALETTES = {
    'deep': ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3", "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD"],
    'deep6': ["#4C72B0", "#55A868", "#C44E52", "#8172B3", "#CCB974", "#64B5CD"],
    'muted': ["#4878D0", "#EE854A", "#6ACC64", "#D65F5F", "#956CB4", "#8C613C", "#DC7EC0", "#797979", "#D5BB67", "#82C6E2"],
    'muted6': ["#4878D0", "#6ACC64", "#D65F5F", "#956CB4", "#D5BB67", "#82C6E2"],
    'pastel': ["#A1C9F4", "#FFB482", "#8DE5A1", "#FF9F9B", "#D0BBFF", "#DEBB9B", "#FAB0E4", "#CFCFCF", "#FFFEA3", "#B9F2F0"],
    'pastel6': ["#A1C9F4", "#8DE5A1", "#FF9F9B", "#D0BBFF", "#FFFEA3", "#B9F2F0"],
    'bright': ["#023EFF", "#FF7C00", "#1AC938", "#E8000B", "#8B2BE2", "#9F4800", "#F14CC1", "#A3A3A3", "#FFC400", "#00D7FF"],
    'bright6': ["#023EFF", "#1AC938", "#E8000B", "#8B2BE2", "#FFC400", "#00D7FF"],
    'dark': ["#001C7F", "#B1400D", "#12711C", "#8C0800", "#591E71", "#592F0D", "#A23582", "#3C3C3C", "#B8850A", "#006374"],
    'dark6': ["#001C7F", "#12711C", "#8C0800", "#591E71", "#B8850A", "#006374"],
    'colorblind': ["#0173B2", "#DE8F05", "#029E73", "#D55E00", "#CC78BC", "#CA9161", "#FBAFE4", "#949494", "#ECE133", "#56B4E9"],
    'colorblind6': ["#0173B2", "#029E73", "#D55E00", "#CC78BC", "#ECE133", "#56B4E9"],
    'blues': ['#dbe9f6', '#bad6eb', '#89bedc', '#539ecd', '#2b7bba', '#0b559f']}


##############
# utility conversion functions

def hex_to_rgb(hex_color_value):
    """
    Convert hexidecimal color to matplotlib color.

    Parameters
    ----------
    hex_color_value : str

    Returns
    -------
    Tuple[float, float, float]
    """

    return colors.to_rgb(hex_color_value)


def rgb_to_hex(rgb_color_value):
    """
    Converts matplotlib color to hexidecimal color.

    Parameters
    ----------
    rgb_color_value : tuple

    Returns
    -------
    str
    """

    return colors.to_hex(rgb_color_value)


def hex_list_to_rgb_list(hex_list):
    """
    Convert list of hexidecimal colors to list of matplotlib colors.

    Parameters
    ----------
    hex_list : List[str]

    Returns
    -------
    List[Tuple[float, float, float]]
    """

    return [hex_to_rgb(hex_value) for hex_value in hex_list]


def rgb_list_to_hex_list(rgb_list):
    """
    Convert list of rgb colors to list of hexidecimal colors.

    Parameters
    ----------
    rgb_list

    Returns
    -------
    List[str]
    """

    return [rgb_to_hex(rgb_value) for rgb_value in rgb_list]


#######
# palette functions

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

    rgb_palette = hex_list_to_rgb_list(hex_palette)
    rgb_full = get_full_rgb_palette(rgb_palette, n_colors)
    hex_full = rgb_list_to_hex_list(rgb_full)
    return hex_full


class ColorCycler(object):
    def __init__(self, n_colors, hex_color_palette=SEABORN_PALETTES['deep']):
        """

        Parameters
        ----------
        n_colors : int
        hex_color_palette : list
        """
        self._n_colors = n_colors
        self._color_counter = 0
        self._color_list = get_full_hex_palette(hex_color_palette, n_colors)

    @property
    def next_color(self):
        next_color = self._color_list[self._color_counter]
        self._color_counter = ((self._color_counter + 1) % self._n_colors)
        return next_color
