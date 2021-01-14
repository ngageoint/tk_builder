import tkinter
import numpy

from tk_builder.panel_builder import WidgetPanel
from tk_builder.panels.image_panel import ImagePanel
from tk_builder.image_readers.numpy_image_reader import NumpyImageReader
from tk_builder.widgets import widget_descriptors
from tk_builder.widgets.image_canvas import ToolConstants, ShapeTypeConstants
from tk_builder.widgets.basic_widgets import Button, CheckButton


class Buttons(WidgetPanel):
    _widget_list = (
        "draw_point", "draw_line", "draw_arrow", "draw_rect", "draw_ellipse", "draw_polygon",
        "resizeable")
    draw_point = widget_descriptors.ButtonDescriptor("draw_point", default_text="point")  # type: Button
    draw_line = widget_descriptors.ButtonDescriptor("draw_line", default_text="line")  # type: Button
    draw_arrow = widget_descriptors.ButtonDescriptor("draw_arrow", default_text="arrow")  # type: Button
    draw_rect = widget_descriptors.ButtonDescriptor("draw_rect", default_text="rect")  # type: Button
    draw_ellipse = widget_descriptors.ButtonDescriptor("draw_ellipse", default_text="ellipse")  # type: Button
    draw_polygon = widget_descriptors.ButtonDescriptor("draw_polygon", default_text="polygon")  # type: Button
    resizeable = widget_descriptors.CheckButtonDescriptor("resizeable", default_text="resizeable")  # type: CheckButton

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

        self.image_panel.resizeable = False

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

        self.image_panel.current_tool = ToolConstants.PAN_TOOL

        self.image_panel.axes_canvas.image_x_min_val = 500
        self.image_panel.axes_canvas.image_x_max_val = 1200

        self.image_panel.axes_canvas.image_y_min_val = 5000
        self.image_panel.axes_canvas.image_y_max_val = 2000

        self.image_panel.set_min_canvas_size(100, 100)

        primary_frame.pack(fill=tkinter.BOTH, expand=tkinter.YES)

        self.button_panel.draw_rect.config(command=self.callback_draw_rect)
        self.button_panel.draw_line.config(command=self.callback_draw_line)
        self.button_panel.draw_arrow.config(command=self.callback_draw_arrow)
        self.button_panel.draw_point.config(command=self.callback_draw_point)
        self.button_panel.draw_ellipse.config(command=self.callback_draw_ellipse)
        self.button_panel.draw_polygon.config(command=self.callback_draw_polygon)
        self.button_panel.resizeable.config(command=self.toggle_resizeable)
        self.image_panel.canvas.on_left_mouse_click(self.callback_on_left_mouse_click)
        self.image_panel.canvas.on_left_mouse_release(self.callback_on_left_mouse_release)

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

    def toggle_resizeable(self):
        value = self.button_panel.resizeable.is_selected()
        self.image_panel.resizeable = value

    def callback_on_left_mouse_click(self, event):
        self.image_panel.canvas.callback_handle_left_mouse_click(event)
        self._set_the_ids()

    def callback_on_left_mouse_release(self, event):
        self.image_panel.canvas.callback_handle_left_mouse_release(event)
        self._set_the_ids()

    def _set_the_ids(self):
        """
        Keep our tracking for the shapes.

        Returns
        -------
        None
        """

        def set_drag_limits():
            vector_obj.image_drag_limits = (
                self.drag_ylim_1, self.drag_xlim_1, self.drag_ylim_2, self.drag_xlim_2)

        vector_obj = self.image_panel.canvas.get_current_vector_object()
        if vector_obj is None:
            # no current shape id, so nothing to be done
            return
        if vector_obj.uid in self.image_panel.canvas.get_tool_shape_ids():
            # this is a tool, so ignore
            return

        print(self._shape_ids)

        set_drag_limits()  # what if this polygon is already outside the drag limits? This will be dumb...

        # see what we are tracking for this shape
        old_shape_id = self._shape_ids.get(vector_obj.type, None)
        if vector_obj.uid == old_shape_id:
            # we are already tracking this shape as our given type, nothing more to do
            return

        # delete the old shape of that type, if applicable
        # this shouldn't happen...
        if old_shape_id is not None:
            self.image_panel.canvas.delete_shape(old_shape_id)
        self._shape_ids[vector_obj.type] = vector_obj.uid

        print(self._shape_ids)


    def exit(self):
        self.quit()


if __name__ == '__main__':
    root = tkinter.Tk()
    app = CanvasResize(root)
    root.mainloop()
