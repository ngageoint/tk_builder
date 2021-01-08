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


def create_filter_entry(title, filter_list):
    """
    Create a filter entry. Both all lowercase and all upper case versions of the
    provided file extensions will be included.

    Parameters
    ----------
    title : str
    filter_list : str|List[str]
        A space delimited string of or list of file extensions.

    Returns
    -------
    (str, str|List[str])
        The entry for a tkinter filetypes element.
    """

    return title, _include_uppercase(filter_list)


all_files = create_filter_entry('ALL Files', '*')
json_files = create_filter_entry('JSON Files', '.json')
tiff_files = create_filter_entry('TIFF Files', '.tiff .tif')
jpeg_files = create_filter_entry('JPEG Files', '.jpeg .jpg .jp2 .j2k')
png_files = create_filter_entry('PNG Files', '.png')
nitf_files = create_filter_entry('NITF Files', '.ntf .nitf')
hdf5_files = create_filter_entry('HDF5 Files', '.hdf .h5 .hdf5 .he5')

basic_image_collection = [
    create_filter_entry('Image Files', '.png .jpeg .jpg .jp2 .j2k .tiff .tif'),
    all_files,
    png_files,
    jpeg_files,
    tiff_files]
