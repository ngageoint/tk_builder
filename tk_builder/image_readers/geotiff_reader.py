from tk_builder.image_readers.image_reader import ImageReader
import numpy
from PIL import Image
from typing import Union, List

try:
    import gdal
except ImportError:
    gdal = None

__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


_gdal_to_numpy_data_types = {
    "Byte": numpy.uint8,
    "UInt16": numpy.uint16,
    "Int16": numpy.int16,
    "UInt32": numpy.uint32,
    "Int32": numpy.int32,
    "Float32": numpy.float32,
    "Float64": numpy.float64,
    "CInt16": numpy.complex64,
    "CInt32": numpy.complex64,
    "CFloat32": numpy.complex64,
    "CFloat64": numpy.complex128}


class GeotiffImageReader(ImageReader):
    """
    Prototype geotiff reader.  If the geotiff is a single channel image the
    "red" band will be used for display
    """

    def __init__(self, fname):
        """

        Parameters
        ----------
        fname : str
        """

        if gdal is None:
            raise ImportError('Importing gdal failed, this functionality is not viable.')

        self.all_image_data = None  # type: Union[None, numpy.ndarray]
        self.display_bands = [0, 1, 2, 3]  # type: List[int]
        self._dset = gdal.Open(fname, gdal.GA_ReadOnly)
        self._data_size = (self._dset.RasterYSize, self._dset.RasterXSize)
        if self.n_bands == 1:
            self.max_dynamic_range_clip = 255.0
            self.min_dynamic_range_clip = 0.0
        else:
            self.max_dynamic_range_clip = (255.0, 255.0, 255.0)
            self.min_dynamic_range_clip = (0.0, 0.0, 0.0)
        if self.n_bands == 1:
            self.display_bands = [0, ]

        self.n_overviews = self._dset.GetRasterBand(1).GetOverviewCount()

    @property
    def n_bands(self):
        """
        int: The number of bands in the image.
        """

        return self._dset.RasterCount

    @property
    def max_dynamic_range_clip(self):
        # type: () -> Union[float, (float, float, float)]
        """
        float|(float, float, float): The maximum to clip the range.
        """

        return self._max_dynamic_range_clip

    @max_dynamic_range_clip.setter
    def max_dynamic_range_clip(self, value):
        if self.n_bands == 1:
            if not isinstance(value, (int, float, numpy.number)):
                raise TypeError(
                    'The image has one image band, which requires a numeric value '
                    'for max_dynamic_range_clip')
            self._max_dynamic_range_clip = float(value)
        else:
            if len(value) != 3:
                raise ValueError(
                    'The image has {} image bands, which requires three element '
                    'max_dynamic_range_clip'.format(self.n_bands))
            self._max_dynamic_range_clip = (float(value[0]), float(value[1]), float(value[2]))

    @property
    def min_dynamic_range_clip(self):
        # type: () -> Union[float, (float, float, float)]
        """
        float|(float, float, float): The minimum to clip the range.
        """

        return self._min_dynamic_range_clip

    @min_dynamic_range_clip.setter
    def min_dynamic_range_clip(self, value):
        if self.n_bands == 1:
            if not isinstance(value, (int, float, numpy.number)):
                raise TypeError(
                    'The image has one image band, which requires a numeric value '
                    'for min_dynamic_range_clip')
            self._min_dynamic_range_clip = float(value)
        else:
            if len(value) != 3:
                raise ValueError(
                    'The image has {} image bands, which requires three element '
                    'min_dynamic_range_clip'.format(self.n_bands))
            self._min_dynamic_range_clip = (float(value[0]), float(value[1]), float(value[2]))

    @property
    def numpy_data_type(self):
        """
        Get dataset type mapped to a numpy type.

        Returns
        -------
        numpy.dtype
        """

        gdal_data_type = gdal.GetDataTypeName(self._dset.GetRasterBand(1).DataType)
        return _gdal_to_numpy_data_types[gdal_data_type]

    def read_full_image_data_from_disk(self):
        """
        Reads the full array for the dataset.

        Returns
        -------
        numpy.ndarray
        """

        bands = list(range(self.n_bands))
        return self.read_full_display_image_data_from_disk(bands)

    def read_full_display_image_data_from_disk(self, bands):
        """
        Read the data corresponding to the given bands for the dataset.

        Parameters
        ----------
        bands : List[int]

        Returns
        -------
        numpy.ndarray
        """

        n_bands = len(bands)
        image_data = numpy.zeros((self.full_image_ny, self.full_image_nx, n_bands),
                                  dtype=self.numpy_data_type)
        for i in range(n_bands):
            image_data[:, :, i] = self._dset.GetRasterBand(bands[i] + 1).ReadAsArray()
        if image_data.shape[2] == 1:
            image_data = numpy.squeeze(image_data)
        return image_data

    def __getitem__(self, key):
        if self.n_bands > 1:
            red_band_range = self._max_dynamic_range_clip[0] - self._min_dynamic_range_clip[0]
            green_band_range = self._max_dynamic_range_clip[1] - self._min_dynamic_range_clip[1]
            blue_band_range = self._max_dynamic_range_clip[2] - self._min_dynamic_range_clip[2]
        else:
            red_band_range = self._max_dynamic_range_clip - self._min_dynamic_range_clip
        if self.n_overviews == 0:
            if self.all_image_data is None:
                self.all_image_data = self.read_full_display_image_data_from_disk(range(self.n_bands))

            if self.n_bands > 1:
                image_data = self.all_image_data[key][:, :, self.display_bands]
                image_data = numpy.array(image_data, dtype=float)

                image_data[:, :, 0] = ((image_data[:, :, 0] - self._min_dynamic_range_clip[0]) / red_band_range) * 255
                image_data[:, :, 1] = ((image_data[:, :, 1] - self._min_dynamic_range_clip[1]) / green_band_range) * 255
                image_data[:, :, 2] = ((image_data[:, :, 2] - self._min_dynamic_range_clip[2]) / blue_band_range) * 255
                image_data[numpy.where(image_data < 0)] = 0
                image_data[numpy.where(image_data > 255)] = 255
                image_data = numpy.asarray(image_data, dtype=numpy.uint8)
                return image_data
            else:
                image_data = self.all_image_data[key]
                image_data = numpy.array(image_data, dtype=numpy.float)

                image_data = ((image_data - self._min_dynamic_range_clip) / red_band_range) * 255
                image_data[numpy.where(image_data < 0)] = 0
                image_data[numpy.where(image_data > 255)] = 255
                image_data = numpy.asarray(image_data, dtype=numpy.uint8)
                return image_data
        else:
            full_image_step_y = key[0].step
            full_image_step_x = key[1].step

            min_step = min(full_image_step_y, full_image_step_x)

            full_image_start_y = key[0].start
            full_image_stop_y = key[0].stop
            full_image_start_x = key[1].start
            full_image_stop_x = key[1].stop

            overview_level = int(numpy.log2(min_step)) - 1
            overview_decimation_factor = numpy.power(2, overview_level + 1)

            overview_start_y = int(full_image_start_y / overview_decimation_factor)
            overview_stop_y = int(full_image_stop_y / overview_decimation_factor)
            overview_start_x = int(full_image_start_x / overview_decimation_factor)
            overview_stop_x = int(full_image_stop_x / overview_decimation_factor)

            overview_x_size = overview_stop_x - overview_start_x - 1
            overview_y_size = overview_stop_y - overview_start_y - 1

            n_display_bands = 3
            if self.n_bands > 3:
                n_display_bands = 4
            if self.n_bands == 1:
                n_display_bands = 1
            d = numpy.zeros((overview_y_size, overview_x_size, n_display_bands), dtype=self.numpy_data_type)
            if overview_level >= 0:
                for i in range(len(self.display_bands)):
                    d[:, :, i] = self._dset.GetRasterBand(self.display_bands[i] + 1).\
                        GetOverview(overview_level).ReadAsArray(overview_start_x,
                                                                overview_start_y,
                                                                overview_x_size,
                                                                overview_y_size)
            else:
                full_image_x_size = full_image_stop_x - full_image_start_x - 1
                full_image_y_size = full_image_stop_y - full_image_start_y - 1
                for i in range(n_display_bands):
                    d[:, :, i] = self._dset.GetRasterBand(self.display_bands[i] + 1).\
                        ReadAsArray(full_image_start_x,
                                    full_image_start_y,
                                    full_image_x_size,
                                    full_image_y_size)
            y_resize = int(numpy.ceil((full_image_stop_y - full_image_start_y) / full_image_step_y))
            x_resize = int(numpy.ceil((full_image_stop_x - full_image_start_x) / full_image_step_x))

            image_data = numpy.array(d, dtype=float)
            if len(self.display_bands) == 3:
                image_data = image_data[:, :, 0:3]

            if self.n_bands > 1:
                image_data[:, :, 0] = ((image_data[:, :, 0] - self._min_dynamic_range_clip[0]) / red_band_range) * 255
                image_data[:, :, 1] = ((image_data[:, :, 1] - self._min_dynamic_range_clip[1]) / green_band_range) * 255
                image_data[:, :, 2] = ((image_data[:, :, 2] - self._min_dynamic_range_clip[2]) / blue_band_range) * 255
                image_data[numpy.where(image_data < 0)] = 0
                image_data[numpy.where(image_data > 255)] = 255
                image_data = numpy.asarray(image_data, dtype=numpy.uint8)

                pil_image = Image.fromarray(image_data)
                resized_pil_image = Image.Image.resize(pil_image, (x_resize, y_resize))
                image_data = numpy.array(resized_pil_image)

                return image_data
            else:
                image_data = ((image_data - self._min_dynamic_range_clip) / red_band_range) * 255
                image_data[numpy.where(image_data < 0)] = 0
                image_data[numpy.where(image_data > 255)] = 255
                image_data = numpy.asarray(image_data, dtype=numpy.uint8)
                image_data = numpy.squeeze(image_data)

                pil_image = Image.fromarray(image_data)
                resized_pil_image = Image.Image.resize(pil_image, (x_resize, y_resize))
                image_data = numpy.array(resized_pil_image)

                return image_data
