from tk_builder.panels.widget_panel.widget_panel_2 import AbstractWidgetPanel
import tk_builder.widgets.basic_widgets as basic_widgets
from tk_builder.widgets.widget_elements import widget_descriptors


class PanelWidgets(object):
    button = widget_descriptors.ButtonDescriptor("button")  # type: basic_widgets.Button
    combobox = widget_descriptors.ComboboxDescriptor("combobox")  # type: basic_widgets.Combobox
    scale = widget_descriptors.ScaleDescriptor("scale")  # type: basic_widgets.Scale
    label = widget_descriptors.LabelDesctriptor("label")  # type: basic_widgets.Label
    label_frame = widget_descriptors.LabelFrameDescriptor("label_frame")  # type: basic_widgets.LabelFrame
    entry = widget_descriptors.EntryDescriptor("entry")  # type: basic_widgets.Entry
    text = widget_descriptors.TextDescriptor("text")
    spinbox = widget_descriptors.SpinboxDescriptor("spinbox")
    radio_button = widget_descriptors.RadioButtonDescriptor("radio_button")
    check_button = widget_descriptors.CheckButtonDescriptor("check_button")


class Panel2(AbstractWidgetPanel):
    def __init__(self, parent):
        AbstractWidgetPanel.__init__(self, parent)
        self.parent = parent

        self.button = PanelWidgets.button
        self.combobox = PanelWidgets.combobox
        self.scale = PanelWidgets.scale
        self.label = PanelWidgets.label
        self.label_frame = PanelWidgets.label_frame
        self.entry = PanelWidgets.entry
        self.spinbox = PanelWidgets.spinbox
        self.radio_button = PanelWidgets.radio_button
        self.check_button = PanelWidgets.check_button

        widget_list = ["label",
                       self.button,
                       self.combobox,
                       self.scale, self.label,
                       self.label_frame,
                       self.label_frame,
                       self.entry,
                       self.spinbox,
                       self.radio_button,
                       self.check_button]

        self.init_w_vertical_layout(widget_list)

        # need to pack both master frame and self, since this is the main app window.
        self.pack()
        #self.button.set_text("stuff")