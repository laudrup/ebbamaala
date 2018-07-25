from django import template
from django.template.loader import render_to_string


register = template.Library()


@register.simple_tag
def form_errors(errors):
    return render_to_string('form_errors/form_errors.html', {'errors': errors})
