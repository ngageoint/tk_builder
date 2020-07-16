from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import basic_widgets
from tk_builder.widgets import widget_descriptors


class Controls(WidgetPanel):
    """
    Band selection tool for RGB display.
    """
    _widget_list = ("pan", "select")

    pan = widget_descriptors.ButtonDescriptor("pan")      # type: basic_widgets.Combobox
    select = widget_descriptors.ButtonDescriptor("select")    # type: basic_widgets.Combobox

    def __init__(self, parent):
        """

        Parameters
        ----------
        parent
            The parent widget.
        """
        WidgetPanel.__init__(self, parent)

        self.init_w_vertical_layout()
