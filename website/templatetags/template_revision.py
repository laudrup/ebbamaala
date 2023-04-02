import subprocess
from datetime import datetime

from django import template

register = template.Library()


@register.filter()
def template_revision(name):
    file_path = str(template.loader.get_template(name).template.origin)
    file_revision = subprocess.check_output(['git', 'log', '-1', '--pretty=%cI', file_path])
    return datetime.fromisoformat(file_revision.decode('utf-8').strip())
