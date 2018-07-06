from django.utils.translation import get_language
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

LANG_TO_FLAG = {
    'da': 'flag-icon-dk',
    'en': 'flag-icon-gb',
    'pl': 'flag-icon-pl',
}


@register.simple_tag
def language_flag(lang=None):
    if not lang:
        lang = get_language()
    lang_flag = LANG_TO_FLAG[lang]
    return mark_safe('<span class="flag-icon {}"></span>'.format(lang_flag))
