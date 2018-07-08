import calendar as cal
import datetime

import requests

from django.template.loader import render_to_string
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django import template


class BootstrapCalendar(cal.Calendar):

    def __init__(self, year, month, bookings):
        super().__init__()
        self._year = year
        self._month = month
        self._bookings = bookings
        self._today = datetime.date.today()
        self._holidays = self._getholidays()

    def render(self):
        return self._formatmonth()

    def _getholidays(self):
        url = 'https://api.dansksupermarked.dk/v1/holidays/'
        last_day = cal.monthrange(self._year, self._month)[1]
        params = {
            'startDate': datetime.date(self._year, self._month, 1).isoformat(),
            'endDate': datetime.date(self._year, self._month, last_day).isoformat()
        }
        headers = {'Authorization': 'Bearer {}'.format(settings.DS_API_KEY)}
        r = requests.get(url, headers=headers, params=params)
        result = {datetime.datetime.strptime(val['date'], '%Y-%m-%d').date():
                  {'name': val['name'],
                   'holiday': val['nationalHoliday']}
                  for val in r.json()}
        return result

    def _istoday(self, day):
        if self._today.year != self._year:
            return False
        if self._today.month != self._month:
            return False
        return self._today.day == day

    def _formatday(self, day, weekday):
        if day == 0:
            return render_to_string('calendar/day.html', {'day': day})

        date = datetime.date(self._year, self._month, day)
        description = self._holidays[date]['name'] if date in self._holidays else None

        booking = next((b for b in self._bookings
                        if date >= b.start and date <= b.end), None)
        booking_class = 'booking'
        if booking:
            if date == booking.start:
                booking_class = 'booking first'
            elif date == booking.end:
                booking_class = 'booking last'

        day_class = ''
        if self._istoday(day):
            day_class = 'today'
        elif weekday in [5, 6] or date in self._holidays and self._holidays[date]['holiday']:
            day_class = 'weekend'

        return render_to_string('calendar/day.html', {'day': day,
                                                      'month': self._month,
                                                      'year': self._year,
                                                      'day_class': day_class,
                                                      'description': description,
                                                      'booking': booking,
                                                      'booking_class': booking_class})

    def _getweeknum(self, theweek):
        firstday = next(d for (d, wd) in theweek if d != 0)
        date = datetime.date(self._year, self._month, firstday)
        return date.isocalendar()[1]

    def _formatweek(self, theweek):
        days = [self._formatday(d, wd) for (d, wd) in theweek]
        weeknum = self._getweeknum(theweek)
        return render_to_string('calendar/week.html', {'weeknum': weeknum,
                                                       'days': days})

    def _formatweekheader(self):
        weekdays = [_(cal.day_abbr[day]) for day in self.iterweekdays()]
        return render_to_string('calendar/weekheader.html', {'weekdays': weekdays})

    def _formatmonth(self):
        weekheader = self._formatweekheader()
        weeks = [self._formatweek(week) for week in
                 self.monthdays2calendar(self._year, self._month)]
        return render_to_string('calendar/month.html', {'weekheader': mark_safe(weekheader),
                                                        'weeks': weeks})


register = template.Library()


@register.simple_tag()
def calendar(year, month, bookings):
    cal = BootstrapCalendar(year, month, bookings)
    return mark_safe(cal.render())


@register.filter()
def month_name(month):
    return _(cal.month_name[month])
