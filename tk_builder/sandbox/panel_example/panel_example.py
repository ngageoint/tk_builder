import tkinter
from tk_builder.panels.widget_panel.widget_panel_2 import AbstractWidgetPanel
import tk_builder.widgets.basic_widgets as basic_widgets
from tk_builder.widgets.widget_elements import widget_descriptors
from tk_builder.sandbox.panel_example.sub_panel_1.sub_panel_1 import Panel1
from tk_builder.sandbox.panel_example.sub_panel_2.sub_panel_2 import Panel2


class OuterPanel(AbstractWidgetPanel):
    _widget_list = ('button_1', 'button_2', 'panel_1', 'panel_2')
    button_1 = widget_descriptors.ButtonDescriptor(
        "button_1", default_text="this is a button!")  # type: basic_widgets.Button
    button_2 = widget_descriptors.ButtonDescriptor(
        "button_2")   # type: basic_widgets.Button
    panel_1 = widget_descriptors.PanelDescriptor(
        "panel_1", Panel1)     # type: Panel1
    panel_2 = widget_descriptors.PanelDescriptor(
        "panel_2", Panel2)     # type: Panel2

    def __init__(self, master):
        master_frame = tkinter.Frame(master)
        AbstractWidgetPanel.__init__(self, master_frame)

        self.init_w_vertical_layout()

        master_frame.pack()
        self.pack()

        self.panel_1.press_all_buttons()


def main():
    root = tkinter.Tk()
    app = OuterPanel(root)
    root.mainloop()


if __name__ == '__main__':
    main()
