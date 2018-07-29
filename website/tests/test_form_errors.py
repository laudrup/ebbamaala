from bs4 import BeautifulSoup
from django.template import Context, Template
from django.test import TestCase


class FormErrorsTagTests(TestCase):

    def test_form_errors(self):
        context = Context({'errors': ['Bad', 'Even worse']})
        template_to_render = Template(
            '{% load form_errors %}'
            '{% form_errors errors %}'
        )
        soup = BeautifulSoup(template_to_render.render(context), 'lxml')
        rows = soup.findAll('div', {'class': 'row'})
        self.assertEqual(2, len(rows))

        alert = rows[0].find(role='alert')
        self.assertIsNotNone(alert)
        self.assertHTMLEqual('Bad', alert.text)

        alert = rows[1].find(role='alert')
        self.assertIsNotNone(alert)
        self.assertHTMLEqual('Even worse', alert.text)
