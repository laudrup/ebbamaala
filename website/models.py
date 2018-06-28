from django.db import models
from markdownx.models import MarkdownxField
from django.utils.translation import gettext as _


class Frontpage(models.Model):
    pub_date = models.DateTimeField(editable=False, auto_now=True)
    content = MarkdownxField(verbose_name=_('Content'))

    class Meta:
        verbose_name = _('Frontpage')
        verbose_name_plural = _('Frontpages')


class HeaderImage(models.Model):
    photo = models.ImageField(upload_to='headers', verbose_name=_('Photo'))

    class Meta:
        verbose_name = _('HeaderImage')
        verbose_name_plural = _('HeaderImages')
