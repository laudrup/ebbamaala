from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from django.template import Context, Template
from django.test import TestCase
from website.models import HeaderImage


class HeaderImageTagTest(TestCase):

    def test_no_header(self):
        template_to_render = Template(
            '{% load header_image %}'
            '{% header_image %}'
        )
        self.assertEqual('', template_to_render.render(Context()))

    def test_with_header(self):
        byte_io = BytesIO()
        img = Image.new('RGB', (10, 10))
        img.save(byte_io, 'JPEG')
        byte_io.getvalue()
        header_image = HeaderImage.objects.create(photo=SimpleUploadedFile('header.jpg',
                                                                           byte_io.getvalue()))

        template_to_render = Template(
            '{% load header_image %}'
            '{% header_image %}'
        )
        self.assertEqual(header_image.photo.url, template_to_render.render(Context()))
