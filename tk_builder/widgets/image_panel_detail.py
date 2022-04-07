"""
A general use class for provided a detail popup functionality to an image panel.
"""

__author__ = "Thomas McCullough"
__classification__ = "UNCLASSIFIED"

import tkinter

from tk_builder.widgets.image_canvas import ImageCanvas
from tk_builder.panels.pyplot_image_panel import PyplotImagePanel


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
