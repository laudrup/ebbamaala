import os

from django.db import models
from django.utils.translation import gettext as _
from markdownx.models import MarkdownxField


class Frontpage(models.Model):
    pub_date = models.DateTimeField(editable=False, auto_now=True)
    content = MarkdownxField(verbose_name=_('Content'))

    class Meta:
        verbose_name = _('Frontpage')
        verbose_name_plural = _('Frontpages')

    def __str__(self):
        return "{} ({})".format(_('Frontpage'), self.id)


class HeaderImage(models.Model):
    photo = models.ImageField(upload_to='headers', verbose_name=_('Photo'))

    class Meta:
        verbose_name = _('HeaderImage')
        verbose_name_plural = _('HeaderImages')

    def __str__(self):
        return os.path.basename(self.photo.name)
