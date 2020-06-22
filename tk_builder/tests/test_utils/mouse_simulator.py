import tkinter


def simulate_event_at_x_y_position(x, y):
    """
    Mouse simulator test.

    Parameters
    ----------
    x : int
    y : int

    Returns
    -------
    tkinter.Event
    """

    event = tkinter.Event.mro()[0]
    event.x = 50
    event.y = 50
    return event
