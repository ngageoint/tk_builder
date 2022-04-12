"""
Basic pass-through functionality for matplotlib/pyplot
"""

import logging
from matplotlib import pyplot
import tkinter

import numpy

from tk_builder.widgets.image_canvas import ImageCanvas
from tk_builder.widgets.basic_widgets import Frame

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2Tk


__classification__ = "UNCLASSIFIED"
__author__ = "Thomas McCullough"


DEFAULT_CMAP = 'bone'
logger = logging.getLogger(__name__)


class PyplotFrame(Frame):
    """
    Simply allows for the creation of tkinter Frame containing the pyplot Figure
    instance provided. It is expected that all other object support will be
    handled external to this class.
    """

    def __init__(self, parent, fig, navigation=True, **kwargs):
        """

        Parameters
        ----------
        parent
        fig : pyplot.Figure
        navigation : bool
        kwargs
        """

        Frame.__init__(self, parent, **kwargs)
        self.fig = fig
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)
        if navigation:
            self.toolbar = NavigationToolbar2Tk(self.canvas, parent)
            self.toolbar.update()
            self.canvas.get_tk_widget().pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)
        else:
            self.toolbar = None
        self.pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.canvas.draw()

    def draw(self):
        """
        Pass-through draw method.
        """

        self.canvas.draw()

    def destroy(self):
        pyplot.close(self.fig)
        Frame.destroy(self)


class PyplotFigure(PyplotFrame):
    """
    Provides a widget that allows users to embed a simple one axis figure
    in an application
    """

    def __init__(self, parent, navigation=False):
        """

        Parameters
        ----------
        parent
        navigation : bool
        """

        self.x_label = ''
        self.y_label = ''
        self.title = ''
        fig, self.ax = pyplot.subplots(dpi=100, nrows=1, ncols=1)
        PyplotFrame.__init__(self, parent, fig, navigation=navigation)
        self.clear()

    def clear(self):
        """
        Clear the axes contents.
        """

        self.ax.cla()
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.grid(True)
        self.ax.set_axisbelow(True)
        self.draw()

    def set_xlabel(self, the_label):
        """
        Sets the displayed x label.

        Parameters
        ----------
        the_label : str
        """
        self.x_label = the_label
        self.ax.set_xlabel(the_label)

    def set_ylabel(self, the_label):
        """
        Sets the displayed y label.

        Parameters
        ----------
        the_label : str
        """

        self.y_label = the_label
        self.ax.set_ylabel(the_label)

    def set_title(self, the_title):
        """
        Sets the displayed figure title.

        Parameters
        ----------
        the_title : str
        """

        self.title = the_title
        self.ax.set_title(the_title)


class PyplotImagePanel(PyplotFigure):
    """
    Provides a widget that allows users to embed pyplot images into an application.
    """

    def __init__(self, parent, cmap_name=DEFAULT_CMAP, navigation=False):
        """

        Parameters
        ----------
        parent
        cmap_name : str
        navigation : bool
        """

        self._cmap_name = DEFAULT_CMAP
        PyplotFigure.__init__(self, parent, navigation=navigation)
        self.cmap_name = cmap_name
        self.set_title('Detailed View')
        self.set_xlabel('Column [pixel]')
        self.set_ylabel('Row [pixel]')
        self.make_blank()

    @property
    def cmap_name(self):
        """
        str: The matplotlib colormap to apply, in the case of monochromatic image data
        """

        return self._cmap_name

    @cmap_name.setter
    def cmap_name(self, value):
        if value in pyplot.colormaps():
            self._cmap_name = value
        else:
            self._cmap_name = DEFAULT_CMAP
            logger.error(
                'cmap_name {} is not in the pyplot list of registered colormaps. '
                'Using the default.'.format(value))

    def make_blank(self):
        """
        Clear the contents of the image panel, and make it blank placeholder.
        """

        image_data = numpy.zeros((600, 400), dtype='uint8')
        self.update_image(image_data)

    def clear(self):
        """
        Clear the axes contents.
        """

        self.ax.cla()
        self.ax.grid(False)
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.set_aspect('auto')  # this is for safety, because it gets implicitly set with imshow

    def update_image(self, image_data, **kwargs):
        """
        Updates the displayed image.

        Parameters
        ----------
        image_data: numpy.ndarray
            An array of dimensions (ny, nx) or (ny, nx, 3)
        kwargs
            Optional key word arguments for :func:`imshow`
        """

        if image_data.ndim != 3 and 'cmap' not in kwargs:
            kwargs['cmap'] = self.cmap_name
        self.clear()
        self.ax.imshow(image_data, **kwargs)
        self.draw()

    def update_pcolormesh(self, x_array, y_array, image_data, **kwargs):
        """
        Updates the display using pcolormesh.

        Parameters
        ----------
        x_array : numpy.ndarray
            An array of dimensions (nx, )
        y_array : numpy.ndarray
            An array of dimensions (ny, )
        image_data : numpy.ndarray
            An array of dimensions (ny, nx)
        kwargs
            Optional key word arguments for :func:`pcolormesh`
        """

        if 'cmap' not in kwargs:
            kwargs['cmap'] = self.cmap_name
        self.clear()
        self.ax.pcolormesh(x_array, y_array, image_data, **kwargs)
        self.draw()


class ImagePanelDetail(object):
    """
    Standard popup detail pane for image canvas.

    .. warning::
        This functionality requires binding to the <<SelectionChanged>>,
        <<SelectionFinalized>>, and <<RemapChanged>> events of the image canvas.
    """

    def __init__(self,
                 master,
                 image_canvas,
                 on_selection_changed=False,
                 on_selection_finalized=True,
                 fetch_full_resolution=False):
        """

        Parameters
        ----------
        master : tkinter.Tk|tkinter.Toplevel
        image_canvas : ImageCanvas
            The associated image canvas
        on_selection_changed : bool
            Trigger popup when selection has changed?
        on_selection_finalized : bool
            Trigger popup when selection has finalized?
        fetch_full_resolution : bool
            Fetch the selection data at full resolution?
        """

        self.detail_popup = tkinter.Toplevel(master)
        self.detail_popup.geometry('700x500')
        self.pyplot_panel = PyplotImagePanel(self.detail_popup, navigation=True)  # type: PyplotImagePanel
        self.pyplot_panel.set_title('Detail View')
        self.detail_popup.protocol("WM_DELETE_WINDOW", self.detail_popup.withdraw)
        self.detail_popup.withdraw()

        self.image_canvas = image_canvas
        self.on_selection_changed = on_selection_changed
        self.on_selection_finalized = on_selection_finalized
        self.fetch_full_resolution = fetch_full_resolution

        self.image_canvas.bind('<<SelectionChanged>>', self.handle_detail_selection_change, '+')
        self.image_canvas.bind('<<SelectionFinalized>>', self.handle_detail_selection_finalized, '+')
        self.image_canvas.bind('<<RemapChanged>>', self.handle_detail_remap_change, '+')

    def make_blank(self):
        self.pyplot_panel.make_blank()

    def set_focus_on_detail_popup(self):
        self.detail_popup.deiconify()
        self.detail_popup.focus_set()
        self.detail_popup.lift()

    def detail_popup_callback(self):
        self.detail_popup.deiconify()

    def display_canvas_rect_selection_in_pyplot_frame(self):
        def get_extent(coords):
            left = min(coords[1::2])
            right = max(coords[1::2])
            top = max(coords[0::2])
            bottom = min(coords[0::2])
            return left, right, top, bottom

        threshold = self.image_canvas.variables.config.select_size_threshold

        try:
            select_id = self.image_canvas.variables.get_tool_shape_id_by_name('SELECT')
            if select_id is None:
                return
        except KeyError:
            return

        rect_coords = self.image_canvas.get_shape_image_coords(select_id)
        extent = get_extent(rect_coords)

        if abs(extent[1] - extent[0]) < threshold or abs(extent[2] - extent[3]) < threshold:
            self.pyplot_panel.make_blank()
        else:
            image_data = self.image_canvas.get_image_data_in_canvas_rect_by_id(
                select_id, decimation=1 if self.fetch_full_resolution else None)
            if image_data is not None:
                self.pyplot_panel.update_image(image_data, extent=extent)
            else:
                self.pyplot_panel.make_blank()

    # noinspection PyUnusedLocal
    def handle_detail_selection_change(self, event):
        """
        Handle a change in the selection area.

        Parameters
        ----------
        event
        """

        if self.image_canvas.image_reader is None or \
                not self.on_selection_changed:
            return

        self.display_canvas_rect_selection_in_pyplot_frame()
        self.detail_popup_callback()

    # noinspection PyUnusedLocal
    def handle_detail_selection_finalized(self, event):
        """
        Handle the finalization of the selection area.

        Parameters
        ----------
        event
        """

        if self.image_canvas.image_reader is None or \
                not self.on_selection_finalized:
            return

        self.display_canvas_rect_selection_in_pyplot_frame()
        self.set_focus_on_detail_popup()

    # noinspection PyUnusedLocal
    def handle_detail_remap_change(self, event):
        """
        Handle that the remap for the image canvas has changed.

        Parameters
        ----------
        event
        """

        if self.image_canvas.image_reader is not None:
            self.display_canvas_rect_selection_in_pyplot_frame()
