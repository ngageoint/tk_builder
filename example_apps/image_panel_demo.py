import tkinter
from tkinter import ttk

import numpy

from tk_builder.panel_builder import WidgetPanel
from tk_builder.panels.image_panel import ImagePanel
from tk_builder.image_reader import NumpyImageReader
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets.image_canvas import ToolConstants, ShapeTypeConstants
from tk_builder.widgets.basic_widgets import Button


class Buttons(WidgetPanel):
    _widget_list = (
        "draw_point", "draw_line", "draw_arrow", "draw_rect", "draw_ellipse", "draw_polygon")
    draw_point = widget_descriptors.ButtonDescriptor("draw_point", default_text="point")  # type: Button
    draw_line = widget_descriptors.ButtonDescriptor("draw_line", default_text="line")  # type: Button
    draw_arrow = widget_descriptors.ButtonDescriptor("draw_arrow", default_text="arrow")  # type: Button
    draw_rect = widget_descriptors.ButtonDescriptor("draw_rect", default_text="rect")  # type: Button
    draw_ellipse = widget_descriptors.ButtonDescriptor("draw_ellipse", default_text="ellipse")  # type: Button
    draw_polygon = widget_descriptors.ButtonDescriptor("draw_polygon", default_text="polygon")  # type: Button

    def __init__(self, primary):
        self.primary = primary
        WidgetPanel.__init__(self, primary)
        self.init_w_vertical_layout()


class CanvasResize(WidgetPanel):
    _widget_list = ("image_panel", "button_panel")

    image_panel = widget_descriptors.ImagePanelDescriptor("image_panel")         # type: ImagePanel
    button_panel = widget_descriptors.PanelDescriptor("button_panel", Buttons)  # type: Buttons

    def __init__(self, primary):
        self._shape_ids = {}

        self.primary = primary

        primary_frame = tkinter.Frame(primary)
        WidgetPanel.__init__(self, primary_frame)

        self.init_w_horizontal_layout()

        image_npix_x = 2000
        image_npix_y = 1500

        self.image_panel.set_max_canvas_size(image_npix_x, image_npix_y)

        image_data = numpy.linspace(0, 255, image_npix_x*image_npix_y)
        image_data = numpy.reshape(image_data, (image_npix_y, image_npix_x))
        image_reader = NumpyImageReader(image_data)
        self.image_panel.set_image_reader(image_reader)

        self.drag_xlim_1 = image_npix_x * 0.1
        self.drag_xlim_2 = image_npix_x * 0.9
        self.drag_ylim_1 = image_npix_y * 0.1
        self.drag_ylim_2 = image_npix_y * 0.9

        self.image_panel.current_tool = ToolConstants.PAN

        self.image_panel.set_min_canvas_size(100, 100)

        primary_frame.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.button_panel.draw_rect.config(command=self.callback_draw_rect)
        self.button_panel.draw_line.config(command=self.callback_draw_line)
        self.button_panel.draw_arrow.config(command=self.callback_draw_arrow)
        self.button_panel.draw_point.config(command=self.callback_draw_point)
        self.button_panel.draw_ellipse.config(command=self.callback_draw_ellipse)
        self.button_panel.draw_polygon.config(command=self.callback_draw_polygon)

        # handle the image creation event
        self.image_panel.canvas.bind('<<ShapeCreate>>', self.handle_new_shape)

    @property
    def point_id(self):
        """
        None|int: The point id.
        """

        return self._shape_ids.get(ShapeTypeConstants.POINT, None)

    @property
    def line_id(self):
        """
        None|int: The line id.
        """

        return self._shape_ids.get(ShapeTypeConstants.LINE, None)

    @property
    def arrow_id(self):
        """
        None|int: The arrow id.
        """

        return self._shape_ids.get(ShapeTypeConstants.ARROW, None)

    @property
    def rect_id(self):
        """
        None|int: The rectangle id.
        """

        return self._shape_ids.get(ShapeTypeConstants.RECT, None)

    @property
    def ellipse_id(self):
        """
        None|int: The ellipse id.
        """

        return self._shape_ids.get(ShapeTypeConstants.ELLIPSE, None)

    @property
    def polygon_id(self):
        """
        None|int: polygon id.
        """

        return self._shape_ids.get(ShapeTypeConstants.POLYGON, None)

    def callback_draw_point(self):
        self.image_panel.canvas.set_current_tool_to_draw_point(self.point_id)

    def callback_draw_line(self):
        self.image_panel.canvas.set_current_tool_to_draw_line(self.line_id)

    def callback_draw_arrow(self):
        self.image_panel.canvas.set_current_tool_to_draw_arrow(self.arrow_id)

    def callback_draw_rect(self):
        self.image_panel.canvas.set_current_tool_to_draw_rect(self.rect_id)

    def callback_draw_ellipse(self):
        self.image_panel.canvas.set_current_tool_to_draw_ellipse(self.ellipse_id)

    def callback_draw_polygon(self):
        self.image_panel.canvas.set_current_tool_to_draw_polygon(self.polygon_id)

    def handle_new_shape(self, event):
        """
        Handle the creation of a new shape.

        Parameters
        ----------
        event
        """

        # we'll be tracking the most recently created
        self._shape_ids[event.y] = event.x

    def exit(self):
        self.quit()


def main():
    root = tkinter.Tk()
    # use the theme, must be after the root element is created
    the_style = ttk.Style()
    the_style.theme_use('clam')

    app = CanvasResize(root)
    root.mainloop()


if __name__ == '__main__':
    main()
