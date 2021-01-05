__classification__ = "UNCLASSIFIED"
__author__ = "Jason Casey"


import logging
from weakref import WeakKeyDictionary

from sarpy.compliance import integer_types, int_func, string_types


def _verify_bool(val, default, name, instance):
    """
    Validate the boolean valued input.

    Parameters
    ----------
    val
        The prospective value.
    default : None|bool
        The default value.
    name : str
        The bound variable name.
    instance
        The instance to which the variable belongs.

    Returns
    -------
    None|bool
    """

    if val is None:
        return default
    else:
        try:
            return bool(val)
        except Exception:
            logging.error(
                'Tried to convert value {} to a boolean value for attribute {} '
                'of class {}'.format(val, name, instance.__class__.__name__))
            raise


def _verify_int(val, default, name, instance):
    """
    Validate the integer valued input.

    Parameters
    ----------
    val
        The prospective value.
    default : None|int
        The default value.
    name : str
        The bound variable name.
    instance
        The instance to which the variable belongs.

    Returns
    -------
    None|int
    """

    if val is None:
        return default
    else:
        try:
            return int_func(val)
        except Exception:
            logging.error(
                'Tried to convert value {} to an integer value for attribute {} '
                'of class {}'.format(val, name, instance.__class__.__name__))
            raise


def _verify_float(val, default, name, instance):
    """
    Validate the float valued input.

    Parameters
    ----------
    val
        The prospective value.
    default : None|float
        The default value.
    name : str
        The bound variable name.
    instance
        The instance to which the variable belongs.

    Returns
    -------
    None|float
    """

    if val is None:
        return default
    else:
        try:
            return float(val)
        except Exception:
            logging.error(
                'Tried to convert value {} to a float value for attribute {} '
                'of class {}'.format(val, name, instance.__class__.__name__))
            raise


def _verify_str(val, default, name, instance):
    """
    Validate the float valued input.

    Parameters
    ----------
    val
        The prospective value.
    default : None|str
        The default value.
    name : str
        The bound variable name.
    instance
        The instance to which the variable belongs.

    Returns
    -------
    None|str
    """

    if val is None:
        return default
    elif isinstance(val, string_types):
        return val
    else:
        try:
            return str(val)
        except Exception:
            logging.error(
                'Tried to convert value {} to a str value for attribute {} '
                'of class {}'.format(val, name, instance.__class__.__name__))
            raise


def _verify_type(val, default, the_type, name, instance):
    """
    Validate that the input is an instance of the provided type.

    Parameters
    ----------
    val
        The prospective value.
    default : None|float
        The default value.
    the_type : Type
        The desired type for the value.
    name : str
        The bound variable name.
    instance
        The instance to which the variable belongs.

    Returns
    -------

    """

    if val is None:
        return default
    elif isinstance(val, the_type):
        return val
    else:
        raise TypeError('The attribute {} of class {} is required to be an instance of type {}, '
                        'but we got type {}'.format(name, instance.__class__.__name__, the_type, type(val)))


def _validate_tuple_length(tup_length, length, name, instance):
    """
    Verify that a tuple length complies with the given length allowance.

    Parameters
    ----------
    tup_length : int
        The tuple length
    length : None|int|tuple|list
        The length bounds for the tuple.
        If `None`, then no limit. If length is an `int`, then that will be the
        required length. If length is `tuple`, then it must be a tuple of length 2
        with entries in increasing order, which describes inclusive (lower, upper)
        bounds for the length of the tuple. If length is `list`, then it will
        describe the enumeration of possible lengths.
    name : str
        The bound variable name.
    instance
        The instance to which the variable belongs.

    Returns
    -------
    bool
    """

    if length is None:
        return True
    elif isinstance(length, integer_types):
        if tup_length != length:
            logging.error(
                "The value for attribute {} of class {} must be a tuple of length {}, and we got "
                "length {}".format(name, instance.__class__.__name__, length, tup_length))
            return False
        return True
    elif isinstance(length, tuple):
        if len(length) != 2 or (length[0] >= length[1]):
            raise ValueError('Got unexpected length tuple {}'.format(length))

        if not (length[0] <= tup_length <= length[1]):
            logging.error(
                "The value for attribute {} of class {} must be a tuple of length between {} and {}, and we "
                "got length {}".format(name, instance.__class__.__name__, length[0], length[1], tup_length))
            return False
        return True
    elif isinstance(length, list):
        if tup_length not in length:
            logging.error(
                "The value for attribute {} of class {} must be a tuple of length one of {}, and we "
                "got length {}".format(name, instance.__class__.__name__, length, tup_length))
            return False
        return True
    else:
        raise TypeError('Got unexpected type {} for length value.'.format(type(length)))


def _verify_int_tuple(val, default, name, instance, length=None):
    """
    Convert and/or validate the input as a tuple of ints.
    This will make a copy of the input.

    Parameters
    ----------
    val
        The prospective value.
    default : None|tuple
    name : str
        The bound variable name.
    instance
        The instance to which the variable belongs.
    length : None|int|tuple|list
        See _validate_tuple_length for description.

    Returns
    -------
    Tuple
    """

    if val is None:
        return default
    try:
        temp = []
        for entry in val:
            temp.append(int_func(entry))
    except Exception:
        raise

    if not _validate_tuple_length(len(temp), length, name, instance):
        raise ValueError('The length of value cannot be validated appropriately')
    return tuple(temp)


def _verify_float_tuple(val, default, name, instance, length=None):
    """
    Convert and/or validate the input as a tuple of floats.
    This will make a copy of the input.

    Parameters
    ----------
    val
        The prospective value.
    default : None|tuple
    name : str
        The bound variable name.
    instance
        The instance to which the variable belongs.
    length : None|int|tuple|list
        See _validate_tuple_length for description.

    Returns
    -------
    Tuple
    """

    if val is None:
        return default
    try:
        temp = []
        for entry in val:
            temp.append(float(entry))
    except Exception:
        raise

    if not _validate_tuple_length(len(temp), length, name, instance):
        raise ValueError('The length of value cannot be validated appropriately')
    return tuple(temp)


def _verify_string_tuple(val, default, name, instance, length=None):
    """
    Convert and/or validate the input as a tuple of strings.
    This will make a copy of the input.

    Parameters
    ----------
    val
        The prospective value.
    default : None|tuple
    name : str
        The bound variable name.
    instance
        The instance to which the variable belongs.
    length : None|int|tuple|list
        See _validate_tuple_length for description.

    Returns
    -------
    Tuple
    """

    if val is None:
        return default
    try:
        temp = []
        for entry in val:
            temp.append(str(entry))
    except Exception:
        raise

    if not _validate_tuple_length(len(temp), length, name, instance):
        raise ValueError('The length of value cannot be validated appropriately')
    return tuple(temp)


def _verify_typed_tuple(val, default, name, instance, the_type, length=None):
    """
    Convert and/or validate the input as a tuple of strings.
    This will make a copy of the input.

    Parameters
    ----------
    val
        The prospective value.
    default : None|tuple
    name : str
        The bound variable name.
    instance
        The instance to which the variable belongs.
    the_type
        The type to validate for.
    length : None|int|tuple|list
        See _validate_tuple_length for description.

    Returns
    -------
    Tuple
    """

    if val is None:
        return default

    temp = []
    for i, entry in enumerate(val):
        if isinstance(entry, the_type):
            temp.append(entry)
        else:
            raise TypeError(
                'Attribute {} of class {} requires a tuple with all elements of type {}, '
                'but entry {} is of type {}'.format(name, instance.__class__, the_type, i, type(entry)))

    if not _validate_tuple_length(len(temp), length, name, instance):
        raise ValueError('The length of value cannot be validated appropriately')
    return tuple(temp)


class BasicDescriptor(object):
    """
    A descriptor object for reusable properties. Note that is is required that the calling
    instance is hashable.
    """

    _typ_string = None

    def __init__(self, name, docstring=''):
        """

        Parameters
        ----------
        name : str
            The attribute name.
        docstring : str
            The docstring.
        """
        self.data = WeakKeyDictionary()  # our instance reference dictionary
        # WeakDictionary use is subtle here. A reference to a particular class instance in this dictionary
        # should not be the thing keeping a particular class instance from being destroyed.
        self.name = name

        self.__doc__ = docstring
        self._format_docstring()

    def _format_docstring(self):
        docstring = self.__doc__
        if docstring is None:
            docstring = ''
        if (self._typ_string is not None) and (not docstring.startswith(self._typ_string)):
            docstring = '{} {}'.format(self._typ_string, docstring)

        suff = self._docstring_suffix()
        if suff is not None:
            docstring = '{} {}'.format(docstring, suff)
        self.__doc__ = docstring

    def _docstring_suffix(self):
        return None

    def _get_default(self, instance):
        return None

    def __get__(self, instance, owner):
        """The getter.

        Parameters
        ----------
        instance : object
            the calling class instance
        owner : object
            the type of the class - that is, the actual object to which this descriptor is assigned

        Returns
        -------
        object
            the return value
        """

        if instance is None:
            # this has been access on the class, so return the class
            return self

        return self.data.get(instance, self._get_default(instance))

    def __set__(self, instance, value):
        """The setter method.

        Parameters
        ----------
        instance : object
            the calling class instance
        value
            the value to use in setting - the type depends of the specific extension of this base class

        Returns
        -------
        bool
            this base class, and only this base class, handles the required compliance and None behavior and has
            a return. This returns True if this the setting value was None, and False otherwise.
        """

        # NOTE: This is intended to handle this case for every extension of this class. Hence the boolean return,
        # which extensions SHOULD NOT implement. This is merely to follow DRY principles.
        if value is None:
            self.data[instance] = self._get_default(instance)
            return True
        # note that the remainder must be implemented in each extension
        return False


class BooleanDescriptor(BasicDescriptor):
    """
    A descriptor for boolean type.
    """

    _typ_string = 'bool:'

    def __init__(self, name, default_value=None, docstring=None):
        self._default_value = default_value
        super(BooleanDescriptor, self).__init__(name, docstring=docstring)

    def _get_default(self, instance):
        return self._default_value

    def _docstring_suffix(self):
        if self._default_value is not None:
            return ' Default value is :code:`{}`.'.format(self._default_value)

    def __set__(self, instance, value):
        if super(BooleanDescriptor, self).__set__(instance, value):
            return

        iv = _verify_bool(value, self._default_value, self.name, instance)
        self.data[instance] = iv


class IntegerDescriptor(BasicDescriptor):
    """
    A descriptor for integer type.
    """

    _typ_string = 'int:'

    def __init__(self, name, default_value=None, docstring=None):
        self._default_value = default_value
        super(IntegerDescriptor, self).__init__(name, docstring=docstring)

    def _get_default(self, instance):
        return self._default_value

    def _docstring_suffix(self):
        if self._default_value is not None:
            return ' Default value is :code:`{}`.'.format(self._default_value)

    def __set__(self, instance, value):
        if super(IntegerDescriptor, self).__set__(instance, value):
            return

        iv = _verify_int(value, self._default_value, self.name, instance)
        self.data[instance] = iv


class FloatDescriptor(BasicDescriptor):
    """
    A descriptor for float type.
    """

    _typ_string = 'float:'

    def __init__(self, name, default_value=None, docstring=None):
        self._default_value = default_value
        super(FloatDescriptor, self).__init__(name, docstring=docstring)

    def _get_default(self, instance):
        return self._default_value

    def _docstring_suffix(self):
        if self._default_value is not None:
            return ' Default value is :code:`{}`.'.format(self._default_value)

    def __set__(self, instance, value):
        if super(FloatDescriptor, self).__set__(instance, value):
            return

        iv = _verify_float(value, self._default_value, self.name, instance)
        self.data[instance] = iv


class StringDescriptor(BasicDescriptor):
    """
    A descriptor for string type
    """
    _typ_string = 'str:'

    def __init__(self, name, default_value=None, docstring=None):
        self._default_value = default_value
        super(StringDescriptor, self).__init__(name, docstring=docstring)

    def _get_default(self, instance):
        return self._default_value

    def _docstring_suffix(self):
        if self._default_value is not None and len(self._default_value) > 0:
            return ' Default value is :code:`{}`.'.format(self._default_value)

    def __set__(self, instance, value):
        if super(StringDescriptor, self).__set__(instance, value):
            return
        self.data[instance] = _verify_str(value, self._default_value, self.name, instance)


class StringEnumDescriptor(BasicDescriptor):
    """
    A descriptor for enumerated (specified) string type. **The valid entries are
    case-sensitive and should be stripped of white space on each end.**
    """

    _typ_string = 'str:'

    def __init__(self, name, values, default_value=None, docstring=None):
        self.values = values
        self._default_value = default_value
        super(StringEnumDescriptor, self).__init__(name, docstring=docstring)
        if (self._default_value is not None) and (self._default_value not in self.values):
            self._default_value = None

    def _get_default(self, instance):
        return self._default_value

    def _docstring_suffix(self):
        suff = ' Takes values in :code:`{}`.'.format(self.values)
        if self._default_value is not None and len(self._default_value) > 0:
            suff += ' Default value is :code:`{}`.'.format(self._default_value)
        return suff

    def __set__(self, instance, value):
        if value is None:
            if self._default_value is not None:
                self.data[instance] = self._default_value
            else:
                super(StringEnumDescriptor, self).__set__(instance, value)
            return

        val = _verify_str(value, self._default_value, self.name, instance)

        if val in self.values:
            self.data[instance] = val
        elif self._default_value is not None:
            msg = 'Attribute {} of class {} received {}, but values ARE REQUIRED to be ' \
                  'one of {}. It has been set to the default ' \
                  'value.'.format(self.name, instance.__class__.__name__, value, self.values)
            logging.error(msg)
            self.data[instance] = self._default_value
        else:
            msg = 'Attribute {} of class {} received {}, but values ARE REQUIRED to be ' \
                  'one of {}. This should be resolved, or it may cause unexpected ' \
                  'issues.'.format(self.name, instance.__class__.__name__, value, self.values)
            logging.error(msg)
            self.data[instance] = val


class IntegerTupleDescriptor(BasicDescriptor):
    """
    A descriptor for a tuple of integer type.
    """

    _typ_string = 'Tuple[int, ...]:'

    def __init__(self, name, length=None, default_value=None, docstring=None):
        self._length = length
        self._default_value = default_value
        super(IntegerTupleDescriptor, self).__init__(name, docstring=docstring)

    def _get_default(self, instance):
        return self._default_value

    def _docstring_suffix(self):
        if self._default_value is not None:
            return ' Default value is :code:`{}`.'.format(self._default_value)

    def __set__(self, instance, value):
        if super(IntegerTupleDescriptor, self).__set__(instance, value):
            return

        iv = _verify_int_tuple(value, self._default_value, self.name, instance, length=self._length)
        self.data[instance] = iv


class FloatTupleDescriptor(BasicDescriptor):
    """
    A descriptor for a tuple of integer type.
    """

    _typ_string = 'tuple:'

    def __init__(self, name, length=None, default_value=None, docstring=None):
        self._length = length
        self._default_value = default_value
        super(FloatTupleDescriptor, self).__init__(name, docstring=docstring)

    def _get_default(self, instance):
        return self._default_value

    def _docstring_suffix(self):
        if self._default_value is not None:
            return ' Default value is :code:`{}`.'.format(self._default_value)

    def __set__(self, instance, value):
        if super(FloatTupleDescriptor, self).__set__(instance, value):
            return

        iv = _verify_float_tuple(value, self._default_value, self.name, instance, length=self._length)
        self.data[instance] = iv


class StringTupleDescriptor(BasicDescriptor):
    """
        A descriptor for a tuple of string type.
        """

    _typ_string = 'tuple:'

    def __init__(self, name, length=None, default_value=None, docstring=None):
        self._length = length
        self._default_value = default_value
        super(StringTupleDescriptor, self).__init__(name, docstring=docstring)

    def _get_default(self, instance):
        return self._default_value

    def _docstring_suffix(self):
        if self._default_value is not None:
            return ' Default value is :code:`{}`.'.format(self._default_value)

    def __set__(self, instance, value):
        if super(StringTupleDescriptor, self).__set__(instance, value):
            return

        iv = _verify_string_tuple(value, self._default_value, self.name, instance, length=self._length)
        self.data[instance] = iv


class TypedDescriptor(BasicDescriptor):
    """
    A descriptor for a specified type.
    """

    def __init__(self, name, the_type, default_value=None, docstring=None):
        self.the_type = the_type
        self._typ_string = str(the_type).strip().split('.')[-1][:-2] + ':'
        self._default_value = default_value
        super(TypedDescriptor, self).__init__(name, docstring=docstring)

    def _get_default(self, instance):
        return self._default_value

    def _docstring_suffix(self):
        if self._default_value is not None:
            return ' Default value is :code:`{}`.'.format(self._default_value)

    def __set__(self, instance, value):
        if super(TypedDescriptor, self).__set__(instance, value):
            return

        iv = _verify_type(value, self._default_value, self.the_type, self.name, instance)
        self.data[instance] = iv


class TypedTupleDescriptor(BasicDescriptor):
    """
    A descriptor for a specified type.
    """
    _typ_string = 'tuple:'

    def __init__(self, name, the_type, length=None, default_value=None, docstring=None):
        self.the_type = the_type
        self._length = length
        self._default_value = default_value
        super(TypedTupleDescriptor, self).__init__(name, docstring=docstring)

    def _get_default(self, instance):
        return self._default_value

    def _docstring_suffix(self):
        if self._default_value is not None:
            return ' Default value is :code:`{}`.'.format(self._default_value)

    def __set__(self, instance, value):
        if super(TypedTupleDescriptor, self).__set__(instance, value):
            return

        iv = _verify_typed_tuple(value, self._default_value, self.name, instance, the_type, length=self._length)
        self.data[instance] = iv
