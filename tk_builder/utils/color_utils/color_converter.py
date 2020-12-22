"""
Color conversion utilities.
"""

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


from matplotlib import colors


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
