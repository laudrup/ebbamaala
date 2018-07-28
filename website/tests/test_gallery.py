from io import BytesIO
from unittest import mock
import piexif
from datetime import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from pyfakefs.fake_filesystem_unittest import Patcher
from website.models import Gallery, GalleryPhoto


class GalleryPhotoModelTests(TestCase):

    def setUp(self):
        # Use pyfakefs for filesystem access
        self.fs_patcher = Patcher()
        self.fs_patcher.setUp()

        # Mock away things that pyfakefs doesn't handle
        self.flock_patcher = mock.patch('fcntl.flock')
        self.flock_patcher.start()

    def tearDown(self):
        self.fs_patcher.tearDown()
        self.flock_patcher.stop()

    def test_photo_upload(self):
        # Create image
        img = Image.new('RGB', (10, 10))
        byte_io = BytesIO()
        img.save(byte_io, 'JPEG')

        # Save to gallery
        gallery = Gallery.objects.create(title='Test Gallery')
        GalleryPhoto.objects.create(photo=SimpleUploadedFile('test.jpg', byte_io.getvalue()),
                                    gallery=gallery)

        # There should be one photo
        gallery_photos = gallery.galleryphoto_set.all()
        self.assertEqual(1, len(gallery_photos))

        # Which is the one just uploaded
        photo = gallery_photos[0]
        self.assertEqual('test.jpg', str(photo))
        self.assertIsNone(photo.date)

    def test_photo_timestamp(self):
        # Create EXIF timestamp
        timestamp = datetime(2015, 8, 15)
        exif_dict = {'Exif': {piexif.ExifIFD.DateTimeOriginal:
                              timestamp.strftime('%Y:%m:%d %H:%M:%S')}}
        exif_bytes = piexif.dump(exif_dict)

        # Create image with EXIF timestamp
        byte_io = BytesIO()
        img = Image.new('RGB', (10, 10))
        img.save(byte_io, 'JPEG', exif=exif_bytes)

        # Save image to gallery
        gallery = Gallery.objects.create(title='Test Gallery')
        photo = GalleryPhoto.objects.create(photo=SimpleUploadedFile('test.jpg',
                                                                     byte_io.getvalue()),
                                            gallery=gallery)

        self.assertEqual(timestamp, photo.date)
