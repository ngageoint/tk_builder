"""
Collection of convenience tkinter format file filter definitions
"""

__author__ = "Thomas McCullough"
__classification__ = "UNCLASSIFIED"


def _include_uppercase(filter_list):
    """
    Builds the list of all lower and all upper case expressions given an expression
    or list of expressions.

    Parameters
    ----------
    filter_list : str|List[str]

    Returns
    -------
    str|List[str]
    """

    def add_element(element):
        # type: (str) -> None
        l_vers = element.lower()
        u_vers = element.upper()
        if l_vers not in out:
            out.append(l_vers)
        if u_vers not in out:
            out.append(u_vers)

    if isinstance(filter_list, str):
        filter_list = filter_list.strip().split()

    out = []
    for entry in filter_list:
        add_element(entry)

    if len(out) == 1:
        return out[0]
    else:
        return out

all_files = ('ALL Files', '*')
json_files = ('JSON Files', _include_uppercase('.json'))
tiff_files = ('TIFF Files', _include_uppercase('.tiff .tif'))
jpeg_files = ('JPEG Files', _include_uppercase('.jpeg .jpg .jp2 .j2k'))
png_files = ('PNG Files', _include_uppercase('.png'))
nitf_files = ('NITF Files', _include_uppercase('.ntf .nitf'))
hdf5_files = ('HDF5 Files', _include_uppercase('.hdf .h5 .hdf5 .he5'))

basic_image_types = [
    ('Image Files', _include_uppercase('.png .jpeg .jpg .jp2 .j2k .tiff .tif')),
    all_files,
    png_files,
    jpeg_files,
    tiff_files]
