import re
import copy
import json

from wtforms.validators import (
    Length,
    NumberRange,
    Email,
    EqualTo,
    IPAddress,
    Regexp,
    URL,
    AnyOf,
    Optional,
    InputRequired,
    MacAddress,
    UUID,
    NoneOf,
    DataRequired,
)

from wtforms.widgets import (
    TextInput as _TextInput,
    PasswordInput as _PasswordInput,
    CheckboxInput as _CheckboxInput,
    Select as _Select,
    TextArea as _TextArea,
    ListWidget as _ListWidget,
    HiddenInput as _HiddenInput,
    RadioInput as _RadioInput,
    FileInput as _FileInput,
    Input,
)

from wtforms.fields import (
    StringField as _StringField,
    BooleanField as _BooleanField,
    DecimalField as _DecimalField,
    IntegerField as _IntegerField,
    FloatField as _FloatField,
    PasswordField as _PasswordField,
    SelectField as _SelectField,
    TextAreaField as _TextAreaField,
    RadioField as _RadioField,
    DateField as _DateField,
    DateTimeField as _DateTimeField,
    FileField as _FileField,
    SelectMultipleField as _SelectMultipleField,
    URLField as _URLField,
    EmailField as _EmailField,
    DecimalRangeField as _DecimalRangeField,
    SearchField as _SearchField,
    TelField as _TelField,
    IntegerRangeField as _IntegerRangeField,
)

from wtforms.widgets import (
    ColorInput as _ColorInput,
    DateInput as _DateInput,
    DateTimeInput as _DateTimeInput,
    EmailInput as _EmailInput,
    RangeInput as _RangeInput,
    TelInput as _TelInput,
    URLInput as _UrlInput,
    NumberInput as _NumberInput,
    SearchInput as _SearchInput,
    TimeInput as _TimeInput,
    WeekInput as _WeekInput,
)


def parsley_kwargs(field, kwargs):
    """
    Return new *kwargs* for *widget*.

    Generate *kwargs* from the validators present for the widget.

    Note that the regex validation relies on the regex pattern being compatible with
    both ECMA script and Python. The regex is not converted in any way.
    It's possible to simply supply your own "parsley-regexp" keyword to the field
    to explicitly provide the ECMA script regex.
    See http://flask.pocoo.org/docs/patterns/wtforms/#forms-in-templates

    Note that the WTForms url vaidator probably is a bit more liberal than the parsley
    one. Do check if the behaviour suits your needs.
    """
    new_kwargs = copy.deepcopy(kwargs)

    if isinstance(field, DateField) or isinstance(field, DateTimeField):
        _date_kwargs(new_kwargs, field)
    if isinstance(field, IntegerField):
        _integer_kwargs(new_kwargs)
    if isinstance(field, DecimalField) or isinstance(field, FloatField):
        _number_kwargs(new_kwargs)
    if not "data_trigger" in new_kwargs:
        _trigger_kwargs(new_kwargs)

    for vali in field.validators:
        if isinstance(vali, Email):
            _email_kwargs(new_kwargs)
        if isinstance(vali, EqualTo):
            _equal_to_kwargs(new_kwargs, vali)
        if isinstance(vali, IPAddress):
            _ip_address_kwargs(new_kwargs)
        if isinstance(vali, Length):
            _length_kwargs(new_kwargs, vali)
        if isinstance(vali, NumberRange):
            _number_range_kwargs(new_kwargs, vali)
        if isinstance(vali, DataRequired) or isinstance(vali, InputRequired):
            _input_required_kwargs(new_kwargs)
            _trigger_kwargs(new_kwargs, "key")
        if isinstance(vali, Regexp) and not "data_regexp" in new_kwargs:
            _regexp_kwargs(new_kwargs, vali)
        if isinstance(vali, URL):
            _url_kwargs(new_kwargs)
        if isinstance(vali, AnyOf):
            _anyof_kwargs(new_kwargs, vali)
        if isinstance(vali, MacAddress):
            _mac_address_kwargs(new_kwargs)
        if isinstance(vali, UUID):
            _uuid_kwargs(new_kwargs)
        if isinstance(vali, NoneOf):
            _none_of_kwargs(new_kwargs, vali)
        if isinstance(vali, Optional):
            pass

        if (
            not "parsley-error-message" in new_kwargs
            and not isinstance(vali, Optional)
            and vali.message is not None
        ):
            _message_kwargs(new_kwargs, message=vali.message)

    return new_kwargs


def _email_kwargs(kwargs):
    kwargs["data-parsley-type"] = "email"


def _equal_to_kwargs(kwargs, vali):
    kwargs["data-parsley-equalto"] = "#" + vali.fieldname


def _ip_address_kwargs(kwargs):
    # Regexp from http://stackoverflow.com/a/4460645
    kwargs["data-parsley-pattern"] = (
        r"^\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
        r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b$"
    )


def _length_kwargs(kwargs, vali):
    default_number = -1

    if vali.max != default_number and vali.min != default_number:
        kwargs["data-parsley-length"] = "[" + str(vali.min) + "," + str(vali.max) + "]"
    else:
        if vali.max == default_number:
            kwargs["data-parsley-minlength"] = str(vali.min)
        if vali.min == default_number:
            kwargs["data-parsley-maxlength"] = str(vali.max)


def _number_range_kwargs(kwargs, vali):
    kwargs["data-parsley-range"] = "[" + str(vali.min) + "," + str(vali.max) + "]"


def _input_required_kwargs(kwargs):
    kwargs["data-parsley-required"] = "true"


def _regexp_kwargs(kwargs, vali):
    # Apparently, this is the best way to check for RegexObject Type
    # It's needed because WTForms allows compiled regexps to be passed to the validator
    RegexObject = type(re.compile(""))
    if isinstance(vali.regex, RegexObject):
        regex_string = vali.regex.pattern
    else:
        regex_string = vali.regex
    kwargs["data-parsley-pattern"] = regex_string


def _url_kwargs(kwargs):
    kwargs["data-parsley-type"] = "url"


def _anyof_kwargs(kwargs, vali):
    # The inlist validator is no longer available in Parsley 2.x, so a custom anyof validator is used.
    kwargs["data-parsley-anyof"] = json.dumps(vali.values)


def _mac_address_kwargs(kwargs):
    kwargs["data-parsley-pattern"] = "^(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$"


def _uuid_kwargs(kwargs):
    kwargs["data-parsley-pattern"] = (
        "^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$"
    )


def _none_of_kwargs(kwargs, vali):
    # data-parsley-noneof is a custom validator, it can be found in scripts/parsley-noneof.js
    kwargs["data-parsley-noneof"] = json.dumps(vali.values)


def _trigger_kwargs(kwargs, trigger="change"):
    kwargs["data-parsley-trigger"] = trigger


def _message_kwargs(kwargs, message):
    kwargs["data-parsley-error-message"] = message


def _date_kwargs(kwargs, field):
    kwargs["data-parsley-datefield"] = field.format


def _integer_kwargs(kwargs):
    kwargs["data-parsley-type"] = "integer"


def _number_kwargs(kwargs):
    kwargs["data-parsley-type"] = "number"


class ParsleyInputMixin(Input):
    def __call__(self, field, **kwargs):
        kwargs = parsley_kwargs(field, kwargs)
        return super(ParsleyInputMixin, self).__call__(field, **kwargs)


class TextInput(_TextInput, ParsleyInputMixin):
    pass


class PasswordInput(_PasswordInput, ParsleyInputMixin):
    pass


class HiddenInput(_HiddenInput, ParsleyInputMixin):
    pass


class TextArea(_TextArea):
    def __call__(self, field, **kwargs):
        kwargs = parsley_kwargs(field, kwargs)
        return super(TextArea, self).__call__(field, **kwargs)


class CheckboxInput(_CheckboxInput, ParsleyInputMixin):
    pass


class ColorInput(_ColorInput, ParsleyInputMixin):
    pass


class DateInput(_DateInput, ParsleyInputMixin):
    pass


class DateTimeInput(_DateTimeInput, ParsleyInputMixin):
    pass


class EmailInput(_EmailInput, ParsleyInputMixin):
    pass


class RangeInput(_RangeInput, ParsleyInputMixin):
    pass


class TelInput(_TelInput, ParsleyInputMixin):
    pass


class URLInput(_UrlInput, ParsleyInputMixin):
    pass


class NumberInput(_NumberInput, ParsleyInputMixin):
    pass


class TimeInput(_TimeInput, ParsleyInputMixin):
    pass


class WeekInput(_WeekInput, ParsleyInputMixin):
    pass


class SearchInput(_SearchInput, ParsleyInputMixin):
    pass


class RadioInput(_RadioInput):
    def __init__(self, parsley_options):
        self.parsley_options = parsley_options

    def __call__(self, field, **kwargs):
        kwargs.update(self.parsley_options)
        return super(RadioInput, self).__call__(field, **kwargs)


class Select(_Select):
    def __call__(self, field, **kwargs):
        kwargs = parsley_kwargs(field, kwargs)
        return super(Select, self).__call__(field, **kwargs)


class ListWidget(_ListWidget):
    def __call__(self, field, **kwargs):
        kwargs = parsley_kwargs(field, kwargs)
        return super(ListWidget, self).__call__(field, **kwargs)


class FileInput(_FileInput):
    def __call__(self, field, **kwargs):
        kwargs = parsley_kwargs(field, kwargs)
        return super(FileInput, self).__call__(field, **kwargs)


class StringField(_StringField):
    def __init__(self, *args, **kwargs):
        super(StringField, self).__init__(widget=TextInput(), *args, **kwargs)


class IntegerField(_IntegerField):
    widget = TextInput()

    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)


class RadioField(_RadioField):
    widget = _ListWidget()

    def __init__(self, *args, **kwargs):
        super(RadioField, self).__init__(*args, **kwargs)
        widget_kwargs = parsley_kwargs(self, {})
        self.option_widget = RadioInput(widget_kwargs)


class BooleanField(_BooleanField):
    widget = CheckboxInput()

    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)


class DecimalField(_DecimalField):
    widget = TextInput()

    def __init__(self, *args, **kwargs):
        super(DecimalField, self).__init__(*args, **kwargs)


class FloatField(_FloatField):
    widget = TextInput()

    def __init__(self, *args, **kwargs):
        super(FloatField, self).__init__(*args, **kwargs)


class PasswordField(_PasswordField):
    widget = PasswordInput()

    def __init__(self, *args, **kwargs):
        super(PasswordField, self).__init__(*args, **kwargs)


class HiddenField(_PasswordField):
    widget = HiddenInput()

    def __init__(self, *args, **kwargs):
        super(HiddenField, self).__init__(*args, **kwargs)


class TextAreaField(_TextAreaField):
    widget = TextArea()

    def __init__(self, *args, **kwargs):
        super(TextAreaField, self).__init__(*args, **kwargs)


class SelectField(_SelectField):
    widget = Select()

    def __init__(self, *args, **kwargs):
        super(SelectField, self).__init__(*args, **kwargs)


class DateTimeField(_DateTimeField):
    widget = TextInput()

    def __init__(self, *args, **kwargs):
        super(DateTimeField, self).__init__(*args, **kwargs)


class DateField(_DateField):
    widget = TextInput()

    def __init__(self, *args, **kwargs):
        super(DateField, self).__init__(*args, **kwargs)


class FileField(_FileField):
    widget = FileInput()

    def __init__(self, *args, **kwargs):
        super(FileField, self).__init__(*args, **kwargs)


class SelectMultipleField(_SelectMultipleField):
    widget = Select(multiple=True)

    def __init__(self, *args, **kwargs):
        super(SelectMultipleField, self).__init__(*args, **kwargs)


class URLField(_URLField):
    widget = URLInput()

    def __init__(self, *args, **kwargs):
        super(URLField, self).__init__(*args, **kwargs)


class TelField(_TelField):
    widget = TelInput()

    def __init__(self, *args, **kwargs):
        super(TelField, self).__init__(*args, **kwargs)


class SearchField(_SearchField):
    widget = SearchInput()

    def __init__(self, *args, **kwargs):
        super(SearchField, self).__init__(*args, **kwargs)


class EmailField(_EmailField):
    widget = EmailInput()

    def __init__(self, *args, **kwargs):
        super(EmailField, self).__init__(*args, **kwargs)


class DecimalRangeField(_DecimalRangeField):
    widget = RangeInput()

    def __init__(self, *args, **kwargs):
        super(DecimalRangeField, self).__init__(*args, **kwargs)


class IntegerRangeField(_IntegerRangeField):
    widget = NumberInput()

    def __init__(self, *args, **kwargs):
        super(IntegerRangeField, self).__init__(*args, **kwargs)
