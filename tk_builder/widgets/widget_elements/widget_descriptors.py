from tk_builder.base_elements import TypedDescriptor
from tk_builder.widgets import basic_widgets
from tk_builder.panels.image_canvas_panel.image_canvas_panel import ImageCanvasPanel


class BaseWidgetDescriptor(TypedDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, the_type, default_text=None, default_value=None, docstring=None):
        self._default_value = default_value
        self.default_text = default_text
        super(BaseWidgetDescriptor, self).__init__(name, the_type, docstring=docstring)


class ButtonDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(ButtonDescriptor, self).__init__(name,
                                               basic_widgets.Button,
                                               default_text=default_text,
                                               default_value=default_value,
                                               docstring=docstring)


class CanvasDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(CanvasDescriptor, self).__init__(name,
                                               basic_widgets.Canvas,
                                               default_text=default_text,
                                               default_value=default_value,
                                               docstring=docstring)


class ComboboxDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(ComboboxDescriptor, self).__init__(name,
                                                 basic_widgets.Combobox,
                                                 default_text=default_text,
                                                 default_value=default_value,
                                                 docstring=docstring)


class ScaleDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(ScaleDescriptor, self).__init__(name,
                                              basic_widgets.Scale,
                                              default_text=default_text,
                                              default_value=default_value,
                                              docstring=docstring)


class LabelDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(LabelDescriptor, self).__init__(name,
                                              basic_widgets.Label,
                                              default_text=default_text,
                                              default_value=default_value,
                                              docstring=docstring)


class LabelFrameDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(LabelFrameDescriptor, self).__init__(name,
                                                   basic_widgets.LabelFrame,
                                                   default_text=default_text,
                                                   default_value=default_value,
                                                   docstring=docstring)


class PanelDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, the_type, default_text=None, default_value=None, docstring=None):
        super(PanelDescriptor, self).__init__(name,
                                              the_type=the_type,
                                              default_text=default_text,
                                              default_value=default_value,
                                              docstring=docstring)


class EntryDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(EntryDescriptor, self).__init__(name,
                                              basic_widgets.Entry,
                                              default_text=default_text,
                                              default_value=default_value,
                                              docstring=docstring)


class TextDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(TextDescriptor, self).__init__(name,
                                                basic_widgets.Text,
                                                default_text=default_text,
                                                default_value=default_value,
                                                docstring=docstring)


class SpinboxDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(SpinboxDescriptor, self).__init__(name,
                                               basic_widgets.Spinbox,
                                               default_text=default_text,
                                               default_value=default_value,
                                               docstring=docstring)


class RadioButtonDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(RadioButtonDescriptor, self).__init__(name,
                                                    basic_widgets.RadioButton,
                                                    default_text=default_text,
                                                    default_value=default_value,
                                                    docstring=docstring)


class CheckButtonDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(CheckButtonDescriptor, self).__init__(name,
                                                    basic_widgets.CheckButton,
                                                    default_text=default_text,
                                                    default_value=default_value,
                                                    docstring=docstring)


class ImageCanvasPanelDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(ImageCanvasPanelDescriptor, self).__init__(name,
                                                         ImageCanvasPanel,
                                                         default_text=default_text,
                                                         default_value=default_value,
                                                         docstring=docstring)


class TreeviewDescriptor(BaseWidgetDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_text=None, default_value=None, docstring=None):
        super(TreeviewDescriptor, self).__init__(name,
                                                 basic_widgets.Treeview,
                                                 default_text=default_text,
                                                 default_value=default_value,
                                                 docstring=docstring)
