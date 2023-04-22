from datetime import datetime
from unittest import mock

from django.template import Context, Template
from django.template.exceptions import TemplateDoesNotExist
from django.test import TestCase


class TemplateRevisionFilterTests(TestCase):
    @mock.patch('os.path.getmtime')
    def test_template_revision(self, getmtime):
        template_to_render = Template(
            '{% load template_revision %}'
            '{% with template_name="website/"|add:name|add:".html" %}'
            '{{template_name|template_revision|date:"U" }}'
            '{% endwith %}'
        )
        timestamp = int(datetime.fromisoformat('2019-01-06').timestamp())
        getmtime.return_value = timestamp
        self.assertEqual(f'{timestamp}', template_to_render.render(Context({'name': 'base'})))
        with self.assertRaises(TemplateDoesNotExist):
            template_to_render.render(Context({'name': 'non-existing-template'}))
