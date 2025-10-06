from django import get_version, template

register = template.Library()


@register.simple_tag
def django_version():
    return get_version()
