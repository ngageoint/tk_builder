from tk_builder.panel_builder import WidgetPanel
import tk_builder.widgets.basic_widgets as basic_widgets
from tk_builder.widgets import widget_descriptors
from example_apps.panel_example.radiobutton_panel import RadioPanel


class Panel1(WidgetPanel):
    _widget_list = (
        'button', 'combobox', 'scale', 'label', 'label_frame', 'entry',
        # 'text',  # omit this one for now, because it's broken
        'spinbox', 'radio_button_panel', 'update_radio_selection', 'check_button')
    button = widget_descriptors.ButtonDescriptor("button")  # type: basic_widgets.Button
    combobox = widget_descriptors.ComboboxDescriptor("combobox")  # type: basic_widgets.Combobox
    scale = widget_descriptors.ScaleDescriptor("scale")  # type: basic_widgets.Scale
    label = widget_descriptors.LabelDescriptor("label")  # type: basic_widgets.Label
    label_frame = widget_descriptors.LabelFrameDescriptor("label_frame")  # type: basic_widgets.LabelFrame
    entry = widget_descriptors.EntryDescriptor("entry", default_text="")  # type: basic_widgets.Entry
    text = widget_descriptors.TextDescriptor("text")  # type: basic_widgets.Text
    spinbox = widget_descriptors.SpinboxDescriptor("spinbox", default_text="")  # type: basic_widgets.Spinbox
    radio_button_panel = widget_descriptors.PanelDescriptor("radio_button_panel", RadioPanel)   # type: RadioPanel
    update_radio_selection = widget_descriptors.ButtonDescriptor("update_radio_selection")  # type: basic_widgets.Button
    check_button = widget_descriptors.CheckButtonDescriptor("check_button")  # type: basic_widgets.CheckButton

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)
        self.parent = parent
        self.init_w_vertical_layout()

        # callbacks
        self.update_radio_selection.on_left_mouse_click(self.callback_update_radio_selection)

    def callback_update_radio_selection(self, event):
        selection = self.radio_button_panel.selection()
        if selection == self.radio_button_panel.button_1:
            self.radio_button_panel.set_text("button 1")
        elif selection == self.radio_button_panel.button_2:
            self.radio_button_panel.set_text("button 2")
        elif selection == self.radio_button_panel.button_3:
            self.radio_button_panel.set_text("button 3")