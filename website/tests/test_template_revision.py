from datetime import datetime
from unittest import mock

from django.template import Context, Template
from django.template.exceptions import TemplateDoesNotExist
from django.test import TestCase


class TemplateRevisionFilterTests(TestCase):
    @mock.patch('subprocess.check_output')
    def test_template_revision(self, check_output):
        template_to_render = Template(
            '{% load template_revision %}'
            '{% with template_name="website/"|add:name|add:".html" %}'
            '{{template_name|template_revision|date:"U" }}'
            '{% endwith %}'
        )
        timestamp = 123456789
        check_output.return_value = datetime.utcfromtimestamp(timestamp).isoformat().encode()
        self.assertEqual(f'{timestamp}', template_to_render.render(Context({'name': 'base'})))
        with self.assertRaises(TemplateDoesNotExist):
            template_to_render.render(Context({'name': 'non-existing-template'}))
