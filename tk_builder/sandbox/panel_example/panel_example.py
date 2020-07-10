import tkinter
from tk_builder.panel_templates.widget_panel.widget_panel_2 import AbstractWidgetPanel
import tk_builder.widgets.basic_widgets as basic_widgets
from tk_builder.widgets.widget_elements import widget_descriptors


class PanelExample(AbstractWidgetPanel):

    button_1 = basic_widgets.Button

    def __init__(self, master):
        master_frame = tkinter.Frame(master)
        AbstractWidgetPanel.__init__(self, master_frame)

        self.button = widget_descriptors.ButtonDescriptor("button")            # type: basic_widgets.Button
        self.combobox = widget_descriptors.ComboboxDescriptor("combobox")      # type: basic_widgets.Combobox
        self.scale = widget_descriptors.ScaleDescriptor("scale")                # type: basic_widgets.Scale
        self.label = widget_descriptors.LabelDesctriptor("label")       # type: basic_widgets.Label
        self.label_frame = widget_descriptors.LabelFrameDescriptor("label_frame")   # type: basic_widgets.LabelFrame
        self.entry = widget_descriptors.EntryDescriptor("entry")
        self.text = widget_descriptors.TextDescriptor("text")
        self.spinbox = widget_descriptors.SpinboxDescriptor("spinbox")
        self.radio_button = widget_descriptors.RadioButtonDescriptor("radio_button")
        self.check_button = widget_descriptors.CheckButtonDescriptor("check_button")

        widget_list = ["label", self.button, self.combobox, self.scale, self.label, self.label_frame, self.label_frame, self.entry, self.spinbox, self.radio_button, self.check_button]
        self.init_w_vertical_layout(widget_list)

        # need to pack both master frame and self, since this is the main app window.
        master_frame.pack()
        self.pack()

        self.button.set_text("stuff")


def main():
    root = tkinter.Tk()
    app = PanelExample(root)
    root.mainloop()


if __name__ == '__main__':
    main()
