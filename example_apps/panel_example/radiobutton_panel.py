from tk_builder.panel_builder import RadioButtonPanel
import tk_builder.widgets.basic_widgets as basic_widgets
from tk_builder.widgets import widget_descriptors


class RadioPanel(RadioButtonPanel):
    _widget_list = ("button_1", "button_2", "button_3", )
    button_1 = widget_descriptors.RadioButtonDescriptor("button_1")  # type: basic_widgets.RadioButton
    button_2 = widget_descriptors.RadioButtonDescriptor("button_2")  # type: basic_widgets.RadioButton
    button_3 = widget_descriptors.RadioButtonDescriptor("button_3")  # type: basic_widgets.RadioButton

    def __init__(self, parent):
        RadioButtonPanel.__init__(self, parent)
        self.parent = parent
        self.init_w_vertical_layout()
