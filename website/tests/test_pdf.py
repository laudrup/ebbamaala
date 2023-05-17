from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.conf import settings

import website.views


class PdfViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('bobby', 'littlebobby@gmail.com', 'tables')
        self.client.login(username='bobby', password='tables')

    @override_settings(WEASYPRINT_BASEURL=settings.BASE_DIR)
    def test_non_existing_pdf(self):
        response = self.client.get('/foo.pdf')
        self.assertEqual(404, response.status_code)

    @override_settings(WEASYPRINT_BASEURL=settings.BASE_DIR)
    def test_existing_pdf(self):
        for name in website.views.InfoView.sections:
            response = self.client.get(f'/{name}.pdf')
            self.assertEqual(200, response.status_code)
            self.assertEqual('application/pdf', response['Content-Type'])
