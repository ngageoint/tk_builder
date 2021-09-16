"""
Basically defining an interface for convenience of binding GUI events using a clear
common naming scheme.

Note that most widgets only emit a limited number of events, so this permits nonsensical
binding for events that never happen, but is completely harmless.
"""

import platform
import tkinter

__classification__ = "UNCLASSIFIED"
__author__ = ("Jason Casey", "Thomas McCullough")


class WidgetEvents(tkinter.Misc):
    """
    A base class intended for simplifying the association of callback functions with
    the possible GUI events.
    """

    def event_binding(self, event_string, callback, *args, **kwargs):
        """
        Register the given callback string with the given callback function. This
        is largely intended to permit a reusable pattern for callbacks with additional
        arguments.

        Parameters
        ----------
        event_string : str
            The tkinter event string.
        callback : callable
            The callback function.
        args
            Optional args (after event) for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        if len(args) > 0 or len(kwargs) > 0:
            self.bind(event_string, lambda event: callback(event, *args, **kwargs))
        else:
            self.bind(event_string, callback)

    def on_left_mouse_click(self, callback, *args, **kwargs):
        """
        The left mouse click event callback registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        self.event_binding('<Button-1>', callback, *args, **kwargs)

    def on_right_mouse_click(self, callback, *args, **kwargs):
        """
        The right mouse click event callback registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        if platform.system() == "Darwin":
            self.event_binding('<Button-2>', callback, *args, **kwargs)  # if using a mac mouse
            self.event_binding('<Button-3>', callback, *args, **kwargs)  # if using a different mouse
        else:
            self.event_binding('<Button-3>', callback, *args, **kwargs)

    def on_left_mouse_double_click(self, callback, *args, **kwargs):
        """
        The left mouse double click event callback registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        self.event_binding('<Double-Button-1>', callback, *args, **kwargs)

    def on_right_mouse_double_click(self, callback, *args, **kwargs):
        """
        The right mouse double click event callback registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """
        if platform.system() == "Darwin":
            self.event_binding('<Double-Button-2>', callback, *args, **kwargs)  # if using a mac mouse
            self.event_binding('<Double-Button-3>', callback, *args, **kwargs)  # if using a different mouse
        else:
            self.event_binding('<Double-Button-3>', callback, *args, **kwargs)

    def on_left_mouse_release(self, callback, *args, **kwargs):
        """
        The left mouse release event callback registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        self.event_binding('<ButtonRelease-1>', callback, *args, **kwargs)

    def on_right_mouse_release(self, callback, *args, **kwargs):
        """
        The right mouse release event callback registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        if platform.system() == "Darwin":
            self.event_binding('<ButtonRelease-2>', callback, *args, **kwargs)  # if using a mac mouse
            self.event_binding('<ButtonRelease-3>', callback, *args, **kwargs)  # if using a different mouse
        else:
            self.event_binding('<ButtonRelease-3>', callback, *args, **kwargs)

    def on_mouse_motion(self, callback, *args, **kwargs):
        """
        The mouse motion event callback registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        self.event_binding('<Motion>', callback, *args, **kwargs)

    def on_left_mouse_motion(self, callback, *args, **kwargs):
        """
        The mouse motion with left button held down event callback registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        self.event_binding('<B1-Motion>', callback, *args, **kwargs)

    def on_right_mouse_motion(self, callback, *args, **kwargs):
        """
        The mouse motion with right button held down event callback registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        if platform.system() == "Darwin":
            self.event_binding('<B2-Motion>', callback, *args, **kwargs)  # if using a mac mouse
            self.event_binding('<B3-Motion>', callback, *args, **kwargs)  # if using a different mouse
        else:
            self.event_binding('<B3-Motion>', callback, *args, **kwargs)

    def on_mouse_wheel(self, callback, *args, **kwargs):
        """
        The mouse wheel event callback registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        if platform.system() == "Linux":
            self.event_binding('<Button-4>', callback, *args, **kwargs)
            self.event_binding('<Button-5>', callback, *args, **kwargs)
        else:
            self.event_binding('<MouseWheel>', callback, *args, **kwargs)

    def on_shift_mouse_wheel(self, callback, *args, **kwargs):
        """
        The shift mouse wheel event callback registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        if platform.system() == "Linux":
            pass
        else:
            self.event_binding('<Shift-MouseWheel>', callback, *args, **kwargs)

    def on_mouse_enter(self, callback, *args, **kwargs):
        """
        The mouse entered the widget (or a child) event registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        self.event_binding('<Enter>', callback, *args, **kwargs)

    def on_mouse_leave(self, callback, *args, **kwargs):
        """
        The mouse left the widget event registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        self.event_binding('<Leave>', callback, *args, **kwargs)

    def on_focus_in(self, callback, *args, **kwargs):
        """
        The keyboard entered the widget (or a child) event registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        self.event_binding('<FocusIn>', callback, *args, **kwargs)

    def on_focus_out(self, callback, *args, **kwargs):
        """
        The keyboard left the widget (or a child) event registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        self.event_binding('<FocusOut>', callback, *args, **kwargs)

    def on_enter_or_return_key(self, callback, *args, **kwargs):
        """
        The enter/return key press event callback registration.

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        self.event_binding('<Return>', callback, *args, **kwargs)

    def on_up_arrow_key(self, callback, *args, **kwargs):
        """

        Parameters
        ----------
        callback
        args
        kwargs

        Returns
        -------
        None
        """
        self.event_binding('<Up>', callback, *args, **kwargs)

    def on_down_arrow_key(self, callback, *args, **kwargs):
        """

        Parameters
        ----------
        callback
        args
        kwargs

        Returns
        -------
        None
        """
        self.event_binding('<Down>', callback, *args, **kwargs)

    def on_left_arrow_key(self, callback, *args, **kwargs):
        """

        Parameters
        ----------
        callback
        args
        kwargs

        Returns
        -------
        None
        """
        self.event_binding('<Left>', callback, *args, **kwargs)

    def on_right_arrow_key(self, callback, *args, **kwargs):
        """

        Parameters
        ----------
        callback
        args
        kwargs

        Returns
        -------
        None
        """
        self.event_binding('<Right>', callback, *args, **kwargs)

    def on_resize(self, callback, *args, **kwargs):
        """
        The resize event callback registration

        Parameters
        ----------
        callback : callable
            The event callback function.
        args
            Optional args for the callback function.
        kwargs
            Optional keyword arguments for the callback function.

        Returns
        -------
        None
        """

        self.event_binding("<Configure>", callback)
