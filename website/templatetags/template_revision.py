import os
from datetime import datetime

from django import template

register = template.Library()


@register.filter()
def template_revision(name):
    file_path = str(template.loader.get_template(name).template.origin)
    mtime = os.path.getmtime(file_path)
    return datetime.fromtimestamp(mtime)
