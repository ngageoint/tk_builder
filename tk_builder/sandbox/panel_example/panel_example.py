import tkinter
from tk_builder.panels.widget_panel.widget_panel_2 import AbstractWidgetPanel
import tk_builder.widgets.basic_widgets as basic_widgets
from tk_builder.widgets.widget_elements import widget_descriptors
from tk_builder.sandbox.panel_example.sub_panel_1.sub_panel_1 import Panel1
from tk_builder.sandbox.panel_example.sub_panel_2.sub_panel_2 import Panel2


class MainPanelButtons:
    button_1 = widget_descriptors.ButtonDescriptor("button1")  # type: basic_widgets.Button
    button_2 = widget_descriptors.ButtonDescriptor("button2")   # type: basic_widgets.Button
    panel_1 = widget_descriptors.PanelDescriptor("inner_panel", Panel1)
    panel_2 = widget_descriptors.PanelDescriptor("panel 2", Panel2)


class OuterPanel(AbstractWidgetPanel):
    def __init__(self, master):
        master_frame = tkinter.Frame(master)
        AbstractWidgetPanel.__init__(self, master_frame)

        self.panel_1 = MainPanelButtons.panel_1
        self.panel_2 = widget_descriptors.PanelDescriptor("panel 2", Panel2)
        self.button = MainPanelButtons.button_1
        self.button2 = MainPanelButtons.button_2

        widget_list = [self.button, self.panel_1]
        self.init_w_vertical_layout(widget_list)

        master_frame.pack()
        self.pack()
        # self.button.set_text("stuff")


def main():
    root = tkinter.Tk()
    app = OuterPanel(root)
    root.mainloop()


if __name__ == '__main__':
    main()
