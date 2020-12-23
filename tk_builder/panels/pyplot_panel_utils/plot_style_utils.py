import matplotlib.pyplot as plt
import math
import numpy
from tk_builder.utils.color_utils.hex_color_palettes import SeabornPaletteNames
from tk_builder.utils.color_utils.hex_color_palettes import SeabornHexPalettes
import tk_builder.utils.color_utils.color_converter as color_converter

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


class PlotStyleUtils:
    def __init__(self):
        self.n_color_bins = 3
        self.rgb_array_fixed_bin_palette = None           # type: [[float]]
        self.rgb_array_full_palette = None          # type: [[float]]
        self.set_palette_by_name(SeabornPaletteNames.muted)
        self.linewidths = (0.5)
        self.linestyle = 'solid'

    def set_palette_by_name(self, palette_name):
        hex_palette = SeabornHexPalettes.get_palette_by_name(palette_name)
        rgb_palette = color_converter.hex_list_to_rgb_list(hex_palette)
        self.rgb_array_fixed_bin_palette = rgb_palette
        full_palette = self.get_full_rgb_palette(rgb_palette, self.n_color_bins)
        self.rgb_array_full_palette = full_palette

    def set_n_colors(self, n_colors):
        self.n_color_bins = n_colors
        full_palette = self.get_full_rgb_palette(self.rgb_array_fixed_bin_palette, n_colors)
        self.rgb_array_full_palette = full_palette

    @staticmethod
    def get_full_rgb_palette(rgb_palette, n_colors=None):
        if n_colors is None:
            n_colors = len(rgb_palette)
        color_array = []
        n_color_bins = len(rgb_palette)
        indices = numpy.linspace(0, n_colors, n_colors)
        for i in indices:
            index = i / n_colors * (n_color_bins-1)
            low = int(index)
            high = int(math.ceil(index))
            interp_float = index - low
            color_array.append(list(numpy.array(rgb_palette[low]) * (1 - interp_float) + numpy.array(rgb_palette[high]) * interp_float))
        return color_array

    @staticmethod
    def get_available_matplotlib_styles():
        return ['default', 'classic'] + sorted(style for style in plt.style.available if style != 'classic')

    @staticmethod
    def get_all_palettes_list():
        return SeabornPaletteNames.get_seaborn_palette_names_list()
