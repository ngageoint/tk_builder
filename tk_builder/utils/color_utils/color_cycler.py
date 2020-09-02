from tk_builder.utils.color_utils.hex_color_palettes import AllColorPalettes
from tk_builder.utils.color_utils import color_utils


class ColorCycler:
    def __init__(self, n_colors, hex_color_palette=AllColorPalettes.seaborn.deep):
        """

        Parameters
        ----------
        n_colors : int
        color_palette : list
        """
        self._n_colors = n_colors
        self._color_counter = 0
        self._color_list = color_utils.get_full_hex_palette(hex_color_palette, n_colors)

    @property
    def next_color(self):
        next_color = self._color_list[self._color_counter]
        self._color_counter += 1
        if self._color_counter >= self._n_colors:
            self._color_counter = 0
        return next_color
