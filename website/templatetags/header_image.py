from django import template

from website.models import HeaderImage

register = template.Library()


@register.simple_tag
def header_image():
    header_images = HeaderImage.objects.order_by('?')
    if len(header_images) > 0:
        return header_images[0].photo.url
    else:
        return ''
