import os
import tkinter
from tkinter import Menu
from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets.axes_image_canvas import AxesImageCanvas

from tk_builder.image_readers.geotiff_reader import GeotiffImageReader
from tk_builder.widgets import widget_descriptors
from tkinter import filedialog
from example_apps.geotiff_viewer.panels.band_selection import BandSelection
from example_apps.geotiff_viewer.panels.controls import Controls
from tk_builder.image_readers.numpy_image_reader import NumpyImageReader


class GeotiffViewer(WidgetPanel):
    """
    A geotiff viewer prototype.
    """
    _widget_list = ("band_selection_panel", "controls_panel", "geotiff_image_panel", "zoom_image_panel")
    geotiff_image_panel = widget_descriptors.ImageCanvasPanelDescriptor("geotiff_image_panel")  # type: AxesImageCanvas
    zoom_image_panel = widget_descriptors.ImageCanvasPanelDescriptor("zoom_image_panel")  # type: AxesImageCanvas
    band_selection_panel = widget_descriptors.PanelDescriptor("band_selection_panel", BandSelection)  # type: BandSelection
    controls_panel = widget_descriptors.PanelDescriptor("controls_panel", Controls)  # type: Controls
    image_reader = None  # type: GeotiffImageReader

    def __init__(self, primary):
        """

        Parameters
        ----------
        primary
            The primary widget.
        """

        self.primary = primary

        primary_frame = tkinter.Frame(primary)
        WidgetPanel.__init__(self, primary_frame)

        self.init_w_horizontal_layout()

        self.geotiff_image_panel.set_canvas_size(800, 1080)
        self.geotiff_image_panel.canvas.set_current_tool_to_pan()

        menubar = Menu()

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.select_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit)

        # create more pulldown menus
        popups_menu = Menu(menubar, tearoff=0)
        popups_menu.add_command(label="Main Controls", command=self.exit)

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Popups", menu=popups_menu)

        primary.config(menu=menubar)

        primary_frame.pack()

        self.band_selection_panel.red_selection.on_selection(self.callback_update_red_band)
        self.band_selection_panel.green_selection.on_selection(self.callback_update_green_band)
        self.band_selection_panel.blue_selection.on_selection(self.callback_update_blue_band)
        self.band_selection_panel.alpha_selection.on_selection(self.callback_update_alpha_band)

        self.controls_panel.pan.on_left_mouse_click(self.callback_set_to_pan)
        self.controls_panel.select.on_left_mouse_click(self.callback_set_to_select)
        self.geotiff_image_panel.canvas.on_left_mouse_release(self.callback_select)

    def exit(self):
        """
        Exits/destroys the widget.

        Returns
        -------
        None
        """

        self.quit()

    def select_file(self, fname=None):
        """
        File selector action. Will open a file selector dialog if `None`.

        Parameters
        ----------
        fname : str|None

        Returns
        -------
        None
        """

        if fname is None:
            fname = filedialog.askopenfilename(initialdir=os.path.expanduser("~"),
                                               title="Select file",
                                               filetypes=(("tiff files", ("*.tif", "*.tiff", "*.TIF", "*.TIFF")),
                                                          ("all files", "*.*"))
                                               )
        self.image_reader = GeotiffImageReader(fname)
        self.geotiff_image_panel.set_image_reader(self.image_reader)
        self.populate_band_selections()

    def populate_band_selections(self):
        """
        Helper method for populating the band selection.

        Returns
        -------
        None
        """

        bands = self.image_reader.n_bands
        band_selections = [str(band) for band in range(bands)]
        band_selections.append("None")
        self.band_selection_panel.red_selection.update_combobox_values(band_selections)
        self.band_selection_panel.green_selection.update_combobox_values(band_selections)
        self.band_selection_panel.blue_selection.update_combobox_values(band_selections)
        self.band_selection_panel.alpha_selection.update_combobox_values(band_selections)

        self.band_selection_panel.red_selection.set(str(self.image_reader.display_bands[0]))
        self.band_selection_panel.green_selection.set(str(self.image_reader.display_bands[1]))
        self.band_selection_panel.blue_selection.set(str(self.image_reader.display_bands[2]))
        if len(self.image_reader.display_bands) > 3:
            self.band_selection_panel.alpha_selection.set(str(self.image_reader.display_bands[3]))
        else:
            self.band_selection_panel.alpha_selection.set("None")

    def callback_update_red_band(self, event):
        """
        Update the read band.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        red_band = self.band_selection_panel.red_selection.get()
        band_num = 0
        if red_band == "None":
            if band_num not in self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands:
                self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands.append(band_num)
        else:
            if band_num in self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands:
                self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands.remove(band_num)
            self.image_reader.display_bands[band_num] = int(red_band)
        self.geotiff_image_panel.canvas.update_current_image()

    def callback_update_green_band(self, event):
        """
        Update the green band.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        green_band = self.band_selection_panel.green_selection.get()
        band_num = 1
        if green_band == "None":
            if band_num not in self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands:
                self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands.append(1)
        else:
            if band_num in self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands:
                self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands.remove(1)
            self.image_reader.display_bands[1] = int(green_band)
        self.geotiff_image_panel.canvas.update_current_image()

    def callback_update_blue_band(self, event):
        """
        Update the blue band.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        band_num = 2
        blue_band = self.band_selection_panel.blue_selection.get()
        if blue_band == "None":
            if band_num not in self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands:
                self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands.append(band_num)
        else:
            if band_num in self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands:
                self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands.remove(band_num)
            self.image_reader.display_bands[band_num] = int(blue_band)
        self.geotiff_image_panel.canvas.update_current_image()

    def callback_update_alpha_band(self, event):
        """
        Update the alpha channel.

        Parameters
        ----------
        event

        Returns
        -------
        None
        """

        alpha_band = self.band_selection_panel.alpha_selection.get()
        band_num = 3
        if len(self.image_reader.display_bands) == 3:
            self.image_reader.display_bands.append(band_num)
        if alpha_band == "None":
            self.image_reader.display_bands = self.image_reader.display_bands[0:3]
        else:
            if band_num in self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands:
                self.geotiff_image_panel.canvas.variables.canvas_image_object.drop_bands.remove(band_num)
            self.image_reader.display_bands[band_num] = int(alpha_band)
        self.geotiff_image_panel.canvas.update_current_image()

    def callback_set_to_pan(self, event):
        self.geotiff_image_panel.canvas.set_current_tool_to_pan()

    def callback_set_to_select(self, event):
        self.geotiff_image_panel.canvas.set_current_tool_to_selection_tool()

    def callback_select(self, event):
        data = self.geotiff_image_panel.canvas.get_image_data_in_canvas_rect_by_id(self.geotiff_image_panel.canvas.variables.select_rect_id, decimation=1)
        data = data[:, :, 0]
        reader = NumpyImageReader(data)
        self.zoom_image_panel.set_image_reader(reader)
        self.zoom_image_panel.canvas.update_current_image()


if __name__ == '__main__':
    root = tkinter.Tk()
    app = GeotiffViewer(root)
    root.mainloop()
