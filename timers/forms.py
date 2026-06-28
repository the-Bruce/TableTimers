import string
from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import Select, MultiWidget, Input
from django.utils.dateparse import parse_duration

from timers.models import Session, TableOffset, TableRanges


def get_time_factors(td: timedelta):
    """
    Get different time factor such as days, hours, minutes and seconds
    :param td: timedelta
    :return: tuple(days, hours, minutes, seconds)
    """
    return (
        int(td.total_seconds() // 60),  # returns number of minutes
        int(td.total_seconds() % 60),  # returns number of seconds
    )


class LabeledNumberInput(Input):
    input_type = "number"

    def __init__(self, label=None, attrs=None, type=None):
        self.widget_label = label
        self.type = type
        if attrs is not None:
            attrs = attrs.copy()
            self.input_type = attrs.pop("type", self.input_type)
        super(Input, self).__init__(attrs)

    # ---------------------------------------------------------------------------------------------------------------------
    def get_context(self, name, value, attrs):
        context = super(Input, self).get_context(name, value, attrs)
        context["widget"]["type"] = self.input_type
        context["widget"]["widget_label"] = self.widget_label
        return context


class TimeDurationWidget(MultiWidget):
    """
    Time duration selector widget
    """

    template_name = "widgets/duration_multiple_input.html"

    def get_context(self, name, value, attrs):
        context = super(TimeDurationWidget, self).get_context(name, value, attrs)
        return context

    # ---------------------------------------------------------------------------------------------------------------------
    def __init__(
        self,
        attrs=None,
    ):
        _widgets = [
            LabeledNumberInput("Minutes"),
            LabeledNumberInput("Seconds"),
        ]
        super().__init__(_widgets, attrs)

    # ---------------------------------------------------------------------------------------------------------------------
    def decompress(self, value):
        if value:
            parsed_value = parse_duration(value)
            minutes, seconds = get_time_factors(parsed_value)
            return_list = [minutes, seconds]
            return return_list
        else:
            return []

    # ---------------------------------------------------------------------------------------------------------------------
    def value_from_datadict(self, data, files, name):
        data_list = {
            i: widget.value_from_datadict(data, files, name + "_{0}".format(i))
            for i, widget in enumerate(self.widgets)
        }
        for key, val in data_list.items():
            try:
                data_list[key] = int(val)
            except ValueError:
                data_list[key] = 0

        minutes = data_list.get(0)
        seconds = data_list.get(1)

        if self.is_required and minutes == 0 and seconds == 0:
            return ""

        try:
            duration = timedelta(
                minutes=int(minutes),
                seconds=int(seconds),
            )
        except ValueError:
            return ""
        else:
            return str(duration)


class ShortCodeForm(forms.Form):
    short_code = forms.CharField(max_length=8, min_length=8)

    def clean_short_code(self):
        short_code = self.cleaned_data["short_code"]
        charset = string.digits + string.ascii_letters
        for i in short_code:
            if i not in charset:
                raise ValidationError(f"Invalid character in short code: {i}")
        if not Session.objects.filter(short_code=short_code).exists():
            raise ValidationError("Unknown or invalid short code")
        return short_code

class TableForm(forms.Form):
    table = forms.IntegerField(widget=Select(choices=[]))

    def __init__(self, *args, session, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
        self.fields["table"].widget = Select(
            choices=[(str(i), i) for i in self.session.available_tables]
        )

class TableOffestForm(forms.ModelForm):
    class Meta:
        model = TableOffset
        fields = ["table", "offset"]
        widgets = {"table": Select(choices=[]), "offset": TimeDurationWidget()}

    def __init__(self, *args, session, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)
        self.fields["table"].widget = Select(
            choices=[(str(i), i) for i in self.session.available_tables]
        )

    def clean_table(self):
        table = self.cleaned_data["table"]
        orig_table = self["table"].initial
        if table != orig_table:
            if TableOffset.objects.filter(session=self.session, table=table).exists():
                raise ValidationError(
                    "Table extension with that table number already exists"
                )
        return table


class TableRangeForm(forms.ModelForm):
    class Meta:
        model = TableRanges
        fields = ["start", "end"]

    def __init__(self, *args, session, **kwargs):
        self.session: Session = session
        super().__init__(*args, **kwargs)

    def clean_end(self):
        start = self.cleaned_data["start"]
        end = self.cleaned_data["end"]

        if end <= start:
            raise ValidationError("End must be bigger than start")
        return end

    def clean(self):
        validated_values = super().clean()

        start = validated_values["start"]
        end = validated_values["end"]

        table_ranges_qs = self.session.tableranges_set.all()
        if self.instance is not None:
            table_ranges_qs = table_ranges_qs.exclude(id=self.instance.id)
        for table_range in table_ranges_qs:
            if (start <= table_range.start <= end) or (start <= table_range.end <= end) or (table_range.start <= start <= end <= table_range.end) or (start <= table_range.start <= table_range.end <= end):
                raise ValidationError(f"Tables overlap with existing range ({table_range.start} - {table_range.end})")


class ConfirmForm(forms.Form):
    pass
