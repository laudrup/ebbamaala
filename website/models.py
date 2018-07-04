import os
import sys
from datetime import datetime
from io import BytesIO

import piexif
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from markdownx.models import MarkdownxField
from PIL import Image


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
                                null=True,
                                verbose_name=_('Photo Date'))
    gallery = models.ForeignKey('Gallery', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')

    def save(self, *args, **kwargs):
        img = Image.open(self.photo)
        if 'exif' in img.info:
            exif_dict = piexif.load(img.info['exif'])

            # Read and save original timestamp of picture if available
            if piexif.ExifIFD.DateTimeOriginal in exif_dict['Exif']:
                exif_date = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal].decode()
                self.date = datetime.strptime(exif_date, '%Y:%m:%d %H:%M:%S')

            # Rotate image and remove rotation field if required
            if piexif.ImageIFD.Orientation in exif_dict['0th']:
                orientation = exif_dict['0th'].pop(piexif.ImageIFD.Orientation)
                exif_bytes = piexif.dump(exif_dict)
                output = BytesIO()
                if orientation == 2:
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    img = img.rotate(180)
                elif orientation == 4:
                    img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 5:
                    img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 6:
                    img = img.rotate(-90, expand=True)
                elif orientation == 7:
                    img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)

                img.save(output, format='JPEG', quality=100, exif=exif_bytes)
                output.seek(0)

                self.photo = InMemoryUploadedFile(output,
                                                  'ImageField',
                                                  '{}.jpg'.format(self.photo.name.split('.')[0]),
                                                  'image/jpeg',
                                                  sys.getsizeof(output),
                                                  None)
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
