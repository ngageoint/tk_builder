from tk_builder.widgets.image_canvas import ImageCanvas
from tk_builder.tests.test_utils import mouse_simulator


def create_new_rect_on_image_canvas(image_canvas, start_x, start_y):
    """
    Create a rectangle on an image canvas.

    Parameters
    ----------
    image_canvas : ImageCanvas
    start_x : int
    start_y : int

    Returns
    -------
    None
    """

    image_canvas.set_current_tool_to_draw_rect(None)
    click_event = mouse_simulator.simulate_event_at_x_y_position(start_x, start_y)
    image_canvas.callback_handle_left_mouse_click(click_event)
