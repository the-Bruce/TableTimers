from datetime import timedelta

from django import template

register = template.Library()


@register.filter()
def invert(val):
    if val == 0:
        return 0
    else:
        return max(-1, min(0, val - 1))


@register.filter()
def progcol(prog):
    if prog > 0.5:
        return "green"
    elif prog > 0.2:
        return "blue"
    elif prog > 0:
        return "orange"
    else:
        return "red"


@register.filter()
def short_duration(duration: timedelta):
    if duration < timedelta(0):
        prefix = "-"
    else:
        prefix = ""
    if duration < timedelta(hours=1):
        mins, secs = divmod(duration.total_seconds(), 60)

        return f"{prefix}{int(mins):02d}:{int(secs):02d}"
    else:
        return str(duration)
