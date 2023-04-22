from datetime import datetime
from io import BytesIO
from unittest import mock

import piexif
import os.path
import tzdata
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from bs4 import BeautifulSoup
from PIL import Image
from pyfakefs.fake_filesystem_unittest import Patcher
from website.models import Gallery, GalleryPhoto

utc_tz_data = b'''TZif2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00TZif2\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\
\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00UTC\x00\nUTC0\n'''


def create_jpeg_data(exif={}):
    byte_io = BytesIO()
    img = Image.new('RGB', (10, 10))
    if exif:
        img.save(byte_io, 'JPEG', exif=piexif.dump(exif))
    else:
        img.save(byte_io, 'JPEG')
    return byte_io.getvalue()


class GalleryPhotoModelTests(TestCase):
    def setUp(self):
        # Use pyfakefs for filesystem access
        self.fs_patcher = Patcher()
        self.fs_patcher.setUp()

        # Mock away things that pyfakefs doesn't handle
        self.flock_patcher = mock.patch('fcntl.flock')
        self.flock_patcher.start()
        self.fs_patcher.fs.create_file(str(os.path.join(tzdata.__path__[0], 'zoneinfo', 'UTC')), contents=utc_tz_data)

    def tearDown(self):
        self.fs_patcher.tearDown()
        self.flock_patcher.stop()

    def test_photo_upload(self):
        jpeg_data = create_jpeg_data()
        gallery = Gallery.objects.create(title='Test Gallery')
        GalleryPhoto.objects.create(photo=SimpleUploadedFile('test.jpg', jpeg_data),
                                    gallery=gallery)

        # There should be one photo
        gallery_photos = gallery.galleryphoto_set.all()
        self.assertEqual(1, len(gallery_photos))
        # Which is the one just uploaded
        photo = gallery_photos[0]
        self.assertEqual('test.jpg', str(photo))
        self.assertIsNone(photo.date)

    def test_photo_timestamp(self):
        # Create image with EXIF timestamp
        timestamp = timezone.make_aware(datetime(2015, 8, 15))
        exif = {'Exif': {piexif.ExifIFD.DateTimeOriginal:
                         timestamp.strftime('%Y:%m:%d %H:%M:%S')}}
        jpeg_data = create_jpeg_data(exif=exif)

        # Save image to gallery
        gallery = Gallery.objects.create(title='Test Gallery')
        photo = GalleryPhoto.objects.create(photo=SimpleUploadedFile('test.jpg', jpeg_data),
                                            gallery=gallery)
        self.assertEqual(timestamp, photo.date)

    @mock.patch('website.models.logger')
    def test_invalid_orientation_tag(self, mock_logger):
        gallery = Gallery.objects.create(title='Test Gallery')
        jpeg_data = create_jpeg_data(exif={'0th': {piexif.ImageIFD.Orientation:
                                                   666}})

        GalleryPhoto.objects.create(photo=SimpleUploadedFile('test.jpg', jpeg_data),
                                    gallery=gallery)
        # The photo should still be saved
        gallery_photos = gallery.galleryphoto_set.all()
        self.assertEqual(1, len(gallery_photos))
        mock_logger.warning.assert_called_with('Unexpected orientation: 666')

    def test_photo_rotation(self):
        gallery = Gallery.objects.create(title='Test Gallery')

        for rotation in range(1, 9):
            # Create image with EXIF rotation info
            jpeg_data = create_jpeg_data(exif={'0th': {piexif.ImageIFD.Orientation:
                                                       rotation}})

            # Save image to gallery
            photo = GalleryPhoto.objects.create(photo=SimpleUploadedFile('test.jpg', jpeg_data),
                                                gallery=gallery)

            # Read and verify uploaded photos orientation tag
            byte_io = BytesIO(photo.photo.read())
            img = Image.open(byte_io)
            exif_dict = piexif.load(img.info['exif'])

            self.assertIn(piexif.ImageIFD.Orientation, exif_dict['0th'])
            self.assertEqual(exif_dict['0th'][piexif.ImageIFD.Orientation], 1)


class GalleryPhotoViewTests(TestCase):
    def setUp(self):
        get_user_model().objects.create_user('bobby', 'littlebobby@gmail.com', 'tables')
        self.client.login(username='bobby', password='tables')

    def test_no_galleries(self):
        response = self.client.get('/gallery')
        self.assertEqual(200, response.status_code)

    def test_empty_gallery(self):
        gallery = Gallery.objects.create(title='Test Gallery')
        response = self.client.get(gallery.get_absolute_url())
        self.assertEqual(200, response.status_code)

    @mock.patch('django.core.files.storage.FileSystemStorage.save')
    def test_gallery_photo(self, mock_storage_save):
        gallery = Gallery.objects.create(title='Test Gallery')

        def photo_saver(path, contents, **kwargs):
            content_bytes = b''.join([b for b in contents.chunks()])
            expected_path = os.path.join('photos', gallery.slug, 'test.jpg')
            self.assertEqual(create_jpeg_data(), content_bytes)
            self.assertEqual(expected_path, path)
            return path

        mock_storage_save.side_effect = photo_saver
        photo = GalleryPhoto.objects.create(photo=SimpleUploadedFile('test.jpg', create_jpeg_data()),
                                            gallery=gallery)
        response = self.client.get(gallery.get_absolute_url())
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content, 'lxml')
        self.assertIn(photo.get_absolute_url(), [a['href'] for a in soup.find_all('a', href=True)])

        response = self.client.get(photo.get_absolute_url())
        self.assertEqual(200, response.status_code)
        self.assertIn('X-Accel-Redirect', response)
        self.assertEqual(f'/protected{photo.get_absolute_url()}', response['X-Accel-Redirect'])
