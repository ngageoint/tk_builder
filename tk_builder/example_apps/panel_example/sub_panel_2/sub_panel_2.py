from tk_builder.panel_builder.widget_panel import WidgetPanel
import tk_builder.widgets.basic_widgets as basic_widgets
from tk_builder.widgets import widget_descriptors


class Panel2(WidgetPanel):
    _widget_list = (
        'button', 'combobox', 'scale', 'label', 'label_frame', 'entry',
        # 'text',  # omit this one for now, because it's broken
        'spinbox', 'radio_button', 'check_button')
    button = widget_descriptors.ButtonDescriptor("button")  # type: basic_widgets.Button
    combobox = widget_descriptors.ComboboxDescriptor("combobox")  # type: basic_widgets.Combobox
    scale = widget_descriptors.ScaleDescriptor("scale")  # type: basic_widgets.Scale
    label = widget_descriptors.LabelDescriptor("label")  # type: basic_widgets.Label
    label_frame = widget_descriptors.LabelFrameDescriptor("label_frame")  # type: basic_widgets.LabelFrame
    entry = widget_descriptors.EntryDescriptor("entry")  # type: basic_widgets.Entry
    text = widget_descriptors.TextDescriptor("text")  # type: basic_widgets.Text
    spinbox = widget_descriptors.SpinboxDescriptor("spinbox")  # type: basic_widgets.Spinbox
    radio_button = widget_descriptors.RadioButtonDescriptor("radio_button")  # type: basic_widgets.RadioButton
    check_button = widget_descriptors.CheckButtonDescriptor("check_button")  # type: basic_widgets.CheckButton

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)
        self.parent = parent

        self.init_w_vertical_layout()

        # need to pack both master frame and self, since this is the main app window.
        self.pack()
