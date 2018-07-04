import os
from datetime import datetime

import exifread
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from markdownx.models import MarkdownxField


class Frontpage(models.Model):
    pub_date = models.DateTimeField(editable=False, auto_now=True)
    content = MarkdownxField(verbose_name=_('Content'))

    class Meta:
        verbose_name = _('Frontpage')
        verbose_name_plural = _('Frontpages')

    def __str__(self):
        return "{} ({})".format(_('Frontpage'), self.id)


class PracticalInfo(models.Model):
    pub_date = models.DateTimeField(editable=False, auto_now=True)
    content = MarkdownxField(verbose_name=_('Content'))

    class Meta:
        verbose_name = _('Practical Info')
        verbose_name_plural = _('Practical Info')

    def __str__(self):
        return "{} ({})".format(_('Practical Info'), self.id)


class HeaderImage(models.Model):
    photo = models.ImageField(upload_to='headers', verbose_name=_('Photo'))
    thumbnail = ImageSpecField(source='photo', processors=[ResizeToFill(600, 180)])

    class Meta:
        verbose_name = _('HeaderImage')
        verbose_name_plural = _('HeaderImages')

    def __str__(self):
        return os.path.basename(self.photo.name)


def gallery_path(instance, filename):
    return os.path.join('photos', instance.gallery.slug, filename)


class GalleryPhoto(models.Model):
    photo = models.ImageField(upload_to=gallery_path, verbose_name=_('Photo'))
    description = models.CharField(max_length=500, blank=True, verbose_name=_('Description'))
    thumbnail = ImageSpecField(source='photo',
                               processors=[ResizeToFill(120, 80)])
    date = models.DateTimeField(editable=False,
                                blank=True,
                                verbose_name=_('Photo Date'))
    gallery = models.ForeignKey('Gallery', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')

    def save(self, *args, **kwargs):
        tags = exifread.process_file(self.photo)
        if 'EXIF DateTimeOriginal' in tags:
            exif_date = str(tags['EXIF DateTimeOriginal'])
            self.photo_date = datetime.strptime(exif_date, '%Y:%m:%d %H:%M:%S')
        else:
            self.photo_date = ""
        super().save(args, kwargs)

    def __str__(self):
        return os.path.basename(self.photo.name)


class Gallery(models.Model):
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    description = models.CharField(max_length=500, blank=True, verbose_name=_('Description'))
    pub_date = models.DateTimeField(editable=False, auto_now=True)
    slug = models.SlugField(unique=True, editable=False)

    class Meta:
        verbose_name = _('Photo Gallery')
        verbose_name_plural = _('Photo Galleries')

    def thumbnail(self):
        return self.galleryphoto_set.order_by('?')[0].thumbnail

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(args, kwargs)

    def __str__(self):
        return self.title
