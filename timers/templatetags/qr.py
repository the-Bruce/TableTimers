import segno

from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def qr_code(text, scale=3):
    qrcode = segno.make(text)
    return qrcode.svg_inline(scale=scale)

@register.simple_tag(takes_context=True)
def qrl(context, url_path, *url_args, code=None, **url_kwargs):
    url = reverse(url_path, args=url_args, kwargs=url_kwargs)
    if code:
        url = f"{url}?code={code}"
    url = context.request.build_absolute_uri(url)
    qrcode = segno.make(url)
    return mark_safe(qrcode.svg_inline(scale=3, omitsize=True))
