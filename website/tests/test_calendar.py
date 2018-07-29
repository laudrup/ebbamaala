from django.template import Context, Template
from django.test import TestCase
from django.utils import translation


class MonthNameTagTests(TestCase):

    def test_month_name(self):
        month_names = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'August',
            'September',
            'October',
            'November',
            'December',
        ]
        self._test_months(month_names)

    def test_danish_month_name(self):
        month_names = [
            'Januar',
            'Februar',
            'Marts',
            'April',
            'Maj',
            'Juni',
            'Juli',
            'August',
            'September',
            'Oktober',
            'November',
            'December',
        ]
        with translation.override('da'):
            self._test_months(month_names)

    def _test_months(self, month_names):
        for month, name in enumerate(month_names, start=1):
            context = Context({'month': month})
            template_to_render = Template(
                '{% load calendar %}'
                '{{ month|month_name }}'
            )
            self.assertEqual(name, template_to_render.render(context))
