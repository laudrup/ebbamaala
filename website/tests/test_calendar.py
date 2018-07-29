import datetime
from unittest import mock

from bs4 import BeautifulSoup
from django.conf import settings
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


class CalendarTagTests(TestCase):

    @mock.patch('salling_group_holidays.v1')
    def test_holiday_api_key(self, mock_holidays_api):
        self._render_template()
        mock_holidays_api.assert_called_with(settings.DS_API_KEY)

    @mock.patch('salling_group_holidays.v1.holidays')
    def test_holidays(self, mock_holidays):
        mock_holidays.return_value = {datetime.date(2018, 1, 17):
                                      {'name': 'Robanukah',
                                       'holiday': True}}

        soup = BeautifulSoup(self._render_template(), 'lxml')
        mock_holidays.assert_called_with(datetime.date(2018, 1, 1),
                                         datetime.date(2018, 1, 31))

        days = soup.findAll('div', {'class': ['current-month']})
        self.assertEqual(31, len(days))

        holiday = days[16].find('div', {'class': 'd-xl-block'})
        self.assertIsNotNone(holiday)
        self.assertEqual(1, len(holiday.contents))
        self.assertHTMLEqual('Robanukah', holiday.contents[0])

    def _render_template(self):
        context = Context(
            {'year': 2018,
             'month': 1,
             'bookings': []}
        )
        template_to_render = Template(
            '{% load calendar %}'
            '{% calendar year month bookings %}'
        )
        return template_to_render.render(context)
