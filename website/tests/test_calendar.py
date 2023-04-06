import datetime
from unittest import mock
from freezegun import freeze_time

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from website.models import Booking


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
    def setUp(self):
        self.context = Context(
            {'year': 2018,
             'month': 1,
             'bookings': []}
        )

    @mock.patch('salling_group_holidays.v1')
    def test_holiday_api_key(self, mock_holidays_api):
        self._render_template(self.context)
        mock_holidays_api.assert_called_with(settings.DS_API_KEY)

    @mock.patch('salling_group_holidays.v1.holidays')
    def test_holidays(self, mock_holidays):
        mock_holidays.return_value = {datetime.date(2018, 1, 17):
                                      {'name': 'Robanukah',
                                       'holiday': True}}

        soup = BeautifulSoup(self._render_template(self.context), 'lxml')
        mock_holidays.assert_called_with(datetime.date(2018, 1, 1),
                                         datetime.date(2018, 1, 31))

        days = soup.findAll('div', {'class': 'current-month'})
        self.assertEqual(31, len(days))

        holiday = days[16].find('div', {'class': 'd-xl-block'})
        self.assertIsNotNone(holiday)
        self.assertEqual(1, len(holiday.contents))
        self.assertHTMLEqual('Robanukah', holiday.contents[0])

    @freeze_time('2018-01-14')
    @mock.patch('salling_group_holidays.v1.holidays')
    def test_today(self, mock_holidays):
        soup = BeautifulSoup(self._render_template(self.context), 'lxml')
        days = soup.findAll('div', {'class': 'day-cell'})
        today = days[13]
        self.assertIsNotNone(today)
        self.assertIn('today', today['class'])

    @freeze_time('2018-01-14')
    @mock.patch('salling_group_holidays.v1.holidays')
    def test_booking(self, mock_holidays):
        user = get_user_model().objects.create_user('bobby', 'littlebobby@gmail.com', 'tables')
        self.client.login(username='bobby', password='tables')
        booking = Booking.objects.create(start_date=datetime.date(2018, 1, 14),
                                         end_date=datetime.date(2018, 1, 16),
                                         user=user,
                                         booker='Karl Smart',
                                         description='Brainstorming')
        booking_url = reverse("website:booking", kwargs={"id": booking.id})
        self.assertEqual(200, self.client.get(booking_url).status_code)

        context = self.context
        context['bookings'] = Booking.objects.all()
        soup = BeautifulSoup(self._render_template(context), 'lxml')
        days = soup.find_all('div', {'class': 'day-cell'})
        for i in range(13):
            self.assertFalse(days[i].find(href=True))

        booked_days = [x for x in days if x.find(class_='booking')]
        self.assertEqual(3, len(booked_days))
        self.assertEqual(booked_days[0], days[13])
        self.assertEqual(booked_days[1], days[14])
        self.assertEqual(booked_days[2], days[15])

        node = booked_days[0].find(class_='booking')
        self.assertEqual(booking_url, booked_days[0].find(href=True)['href'])
        self.assertTrue(node)
        self.assertIn('first', node['class'])
        self.assertNotIn('last', node['class'])

        node = booked_days[1].find(class_='booking')
        self.assertEqual(booking_url, booked_days[1].find(href=True)['href'])
        self.assertTrue(node)
        self.assertNotIn('first', node['class'])
        self.assertNotIn('last', node['class'])

        node = booked_days[2].find(class_='booking')
        self.assertEqual(booking_url, booked_days[2].find(href=True)['href'])
        self.assertTrue(node)
        self.assertIn('last', node['class'])
        self.assertNotIn('first', node['class'])

        for i in range(16, 31):
            booking_url = f'{reverse("website:booking")}?year=2018&month=1&day={i+1}'
            self.assertEqual(booking_url, days[i].find(href=True)['href'])
            response = self.client.get(booking_url)
            self.assertEqual(200, response.status_code)

    def _render_template(self, context):
        template_to_render = Template(
            '{% load calendar %}'
            '{% calendar year month bookings %}'
        )
        return template_to_render.render(context)


@mock.patch('salling_group_holidays.v1.holidays')
class CalendarViewTests(TestCase):

    def setUp(self):
        get_user_model().objects.create_user('bobby', 'littlebobby@gmail.com', 'tables')
        self.client.login(username='bobby', password='tables')

    @freeze_time('2019-06-01')
    def test_default_calendar(self, mock_holidays):
        response = self.client.get('/calendar')
        self.assertEqual(200, response.status_code)
        self.assertEqual(2019, response.context['year'])
        self.assertEqual(6, response.context['month'])

    def test_specific_month(self, mock_holidays):
        response = self.client.get('/calendar/2024/07/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(2024, response.context['year'])
        self.assertEqual(7, response.context['month'])

    def test_invalid_month(self, mock_holidays):
        response = self.client.get('/calendar/2020/42/')
        self.assertEqual(404, response.status_code)
