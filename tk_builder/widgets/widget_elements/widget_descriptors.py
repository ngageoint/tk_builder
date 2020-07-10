from tk_builder.base_elements import TypedDescriptor
from tk_builder.widgets import basic_widgets


class ButtonDescriptor(TypedDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_value=None, docstring=None):
        self.the_type = basic_widgets.Button
        self._default_value = default_value
        super(TypedDescriptor, self).__init__(name, docstring=docstring)


class CanvasDescriptor(TypedDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_value=None, docstring=None):
        self.the_type = basic_widgets.Canvas
        self._default_value = default_value
        super(TypedDescriptor, self).__init__(name, docstring=docstring)


class ComboboxDescriptor(TypedDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_value=None, docstring=None):
        self.the_type = basic_widgets.Combobox
        self._default_value = default_value
        super(TypedDescriptor, self).__init__(name, docstring=docstring)


class ScaleDescriptor(TypedDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_value=None, docstring=None):
        self.the_type = basic_widgets.Scale
        self._default_value = default_value
        super(TypedDescriptor, self).__init__(name, docstring=docstring)


class LabelDesctriptor(TypedDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_value=None, docstring=None):
        self.the_type = basic_widgets.Label
        self._default_value = default_value
        super(TypedDescriptor, self).__init__(name, docstring=docstring)


class LabelFrameDescriptor(TypedDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_value=None, docstring=None):
        self.the_type = basic_widgets.LabelFrame
        self._default_value = default_value
        super(TypedDescriptor, self).__init__(name, docstring=docstring)


class EntryDescriptor(TypedDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_value=None, docstring=None):
        self.the_type = basic_widgets.Entry
        self._default_value = default_value
        super(TypedDescriptor, self).__init__(name, docstring=docstring)


class TextDescriptor(TypedDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_value=None, docstring=None):
        self.the_type = basic_widgets.Text
        self._default_value = default_value
        super(TypedDescriptor, self).__init__(name, docstring=docstring)


class SpinboxDescriptor(TypedDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_value=None, docstring=None):
        self.the_type = basic_widgets.Spinbox
        self._default_value = default_value
        super(TypedDescriptor, self).__init__(name, docstring=docstring)


class RadioButtonDescriptor(TypedDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_value=None, docstring=None):
        self.the_type = basic_widgets.RadioButton
        self._default_value = default_value
        super(TypedDescriptor, self).__init__(name, docstring=docstring)


class CheckButtonDescriptor(TypedDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, default_value=None, docstring=None):
        self.the_type = basic_widgets.CheckButton
        self._default_value = default_value
        super(TypedDescriptor, self).__init__(name, docstring=docstring)
