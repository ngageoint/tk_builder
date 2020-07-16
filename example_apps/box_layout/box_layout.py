import tkinter
from tk_builder.panel_builder import WidgetPanel
from tk_builder.widgets import basic_widgets
from tk_builder.widgets import widget_descriptors


class PrimaryPanel(WidgetPanel):
    _widget_list = ("nx_label", "nx", "ny_label", "ny")
    nx_label = widget_descriptors.LabelDescriptor("nx_label")          # type: basic_widgets.Label
    nx = widget_descriptors.EntryDescriptor("nx")                # type: basic_widgets.Entry
    ny_label = widget_descriptors.LabelDescriptor("ny_label")          # type: basic_widgets.Label
    ny = widget_descriptors.EntryDescriptor("ny")                # type: basic_widgets.Entry

    def __init__(self, parent):
        WidgetPanel.__init__(self, parent)
        # TODO: changed to init_w_box_layout once that is refactored
        self.init_w_box_layout(n_columns=2)
        self.nx.config(state="disabled")
        self.ny.config(state="disabled")

        self.nx_label.set_text("nx: ")
        self.ny_label.set_text("ny: ")


def main():
    root = tkinter.Tk()
    app = PrimaryPanel(root)
    root.mainloop()


if __name__ == '__main__':
    main()
