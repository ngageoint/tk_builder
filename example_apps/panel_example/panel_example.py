import tkinter
from tk_builder.panel_builder import WidgetPanel
import tk_builder.widgets.basic_widgets as basic_widgets
from tk_builder.widgets import widget_descriptors
from example_apps.panel_example.sub_panel_1 import Panel1


class PrimaryPanel(WidgetPanel):
    _widget_list = ('button_1', 'panel_1')
    button_1 = widget_descriptors.ButtonDescriptor("button_1", default_text="asdf")  # type: basic_widgets.Button
    button_2 = widget_descriptors.ButtonDescriptor("button_2")   # type: basic_widgets.Button
    panel_1 = widget_descriptors.PanelDescriptor("panel_1", Panel1)     # type: Panel1

    def __init__(self, primary):
        primary_frame = tkinter.Frame(primary)
        WidgetPanel.__init__(self, primary_frame)

        self.init_w_horizontal_layout()

        primary_frame.pack()
        self.panel_1.press_all_buttons()
        self.panel_1.unpress_all_buttons()


def main():
    root = tkinter.Tk()
    app = PrimaryPanel(root)
    root.mainloop()


if __name__ == '__main__':
    main()
