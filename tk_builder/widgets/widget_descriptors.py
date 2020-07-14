from tkinter import Widget

from tk_builder.base_elements import TypedDescriptor
from tk_builder.widgets import basic_widgets


class BaseWidgetDescriptor(TypedDescriptor):
    """
    A descriptor for a base gui widget type.
    """

    def __init__(self, name, the_type, default_text=None, docstring=None):
        if default_text is None:
            self.default_text = name
        else:
            self.default_text = default_text
        if not issubclass(the_type, Widget):
            raise TypeError(
                'GUI widget descriptor type input must be a subclass of tkinter.Widget. '
                'Got type {}'.format(the_type))
        super(BaseWidgetDescriptor, self).__init__(name, the_type, docstring=docstring)


class ButtonDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a button type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(ButtonDescriptor, self).__init__(name,
                                               basic_widgets.Button,
                                               default_text=default_text,
                                               docstring=docstring)


class CanvasDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a canvas type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(CanvasDescriptor, self).__init__(name,
                                               basic_widgets.Canvas,
                                               default_text=default_text,
                                               docstring=docstring)


class ComboboxDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a combobox type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(ComboboxDescriptor, self).__init__(name,
                                                 basic_widgets.Combobox,
                                                 default_text=default_text,
                                                 docstring=docstring)


class ScaleDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a scale type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(ScaleDescriptor, self).__init__(name,
                                              basic_widgets.Scale,
                                              default_text=default_text,
                                              docstring=docstring)


class LabelDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a label type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(LabelDescriptor, self).__init__(name,
                                              basic_widgets.Label,
                                              default_text=default_text,
                                              docstring=docstring)


class LabelFrameDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a label frame type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(LabelFrameDescriptor, self).__init__(name,
                                                   basic_widgets.LabelFrame,
                                                   default_text=default_text,
                                                   docstring=docstring)


class PanelDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a panel type.
    """

    def __init__(self, name, the_type, default_text=None, docstring=None):
        super(PanelDescriptor, self).__init__(name,
                                              the_type=the_type,
                                              default_text=default_text,
                                              docstring=docstring)


class EntryDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a entry type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(EntryDescriptor, self).__init__(name,
                                              basic_widgets.Entry,
                                              default_text=default_text,
                                              docstring=docstring)


class TextDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a text type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(TextDescriptor, self).__init__(name,
                                                basic_widgets.Text,
                                                default_text=default_text,
                                                docstring=docstring)


class SpinboxDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a spinbox type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(SpinboxDescriptor, self).__init__(name,
                                               basic_widgets.Spinbox,
                                               default_text=default_text,
                                               docstring=docstring)


class RadioButtonDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a radiobutton type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(RadioButtonDescriptor, self).__init__(name,
                                                    basic_widgets.RadioButton,
                                                    default_text=default_text,
                                                    docstring=docstring)


class CheckButtonDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a check button type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(CheckButtonDescriptor, self).__init__(name,
                                                    basic_widgets.CheckButton,
                                                    default_text=default_text,
                                                    docstring=docstring)


class ImageCanvasPanelDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a image canvas panel type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        from tk_builder.panels.image_canvas_panel.image_canvas_panel import ImageCanvasPanel
        super(ImageCanvasPanelDescriptor, self).__init__(name,
                                                         ImageCanvasPanel,
                                                         default_text=default_text,
                                                         docstring=docstring)


class PyplotPanelDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a image canvas panel type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        from tk_builder.panels.pyplot_panel.pyplot_panel import PyplotPanel
        super(PyplotPanelDescriptor, self).__init__(name,
                                                    PyplotPanel,
                                                    default_text=default_text,
                                                    docstring=docstring)


class TreeviewDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a tree view type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(TreeviewDescriptor, self).__init__(name,
                                                 basic_widgets.Treeview,
                                                 default_text=default_text,
                                                 docstring=docstring)


class PyplotCanvasDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a tree view type.
    """

    def __init__(self, name, default_text=None, docstring=None):
        super(PyplotCanvasDescriptor, self).__init__(name,
                                                     basic_widgets.PyplotCanvas,
                                                     default_text=default_text,
                                                     docstring=docstring)
