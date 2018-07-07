import calendar as cal
import datetime

import requests

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
            return '<div class="day-cell"></div>'

        day_template = """
        <div class="day-cell current-month {extra_classes}">
          <div class="row">
            <div class="col-sm-12">
              <div class="row">
                <div class="day-number col float-right">
                  {day}
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <div class="d-none d-xl-block text-center">
                    {description}
                  </div>
                </div>
              </div>
            </div>
          </div>
          {reservation}
        </div>
        """

        date = datetime.date(self._year, self._month, day)

        description = self._holidays[date]['name'] if date in self._holidays else '</br>'
        reservation = ''

        for booking in self._bookings:
            if date >= booking.start and date <= booking.end:
                reservation = '<div class="row"><span class="reserved mt-1 mb-1 {}"><br/></span></div>'
                if date == booking.start:
                    reservation = reservation.format('first')
                elif date == booking.end:
                    reservation = reservation.format('last')
                else:
                    reservation = reservation.format('')
        extra_classes = []

        if weekday in [5, 6] or date in self._holidays and self._holidays[date]['holiday']:
            extra_classes = ['weekend']

        if self._istoday(day):
            extra_classes = ['today']

        return day_template.format(extra_classes=' '.join(extra_classes),
                                   description=description,
                                   day=day,
                                   reservation=reservation)

    def _getweeknum(self, theweek):
        for (d, wd) in theweek:
            if d != 0:
                date = datetime.date(self._year, self._month, d)
                return date.isocalendar()[1]
        assert(False)

    def _formatweek(self, theweek):
        week_template = """
        <div class="week-row">
          <div class="week-number d-flex align-items-center">
            {}
          </div>
          {}
        </div>
        """

        s = ''.join(self._formatday(d, wd) for (d, wd) in theweek)
        weeknum = self._getweeknum(theweek)
        return week_template.format(weeknum, s)

    def _formatweekday(self, day):
        weekday_template = """
        <strong class="week">
          {}
        </strong>
        """
        weekday = _(cal.day_abbr[day])
        return weekday_template.format(weekday.capitalize())

    def _formatweekheader(self):
        weekheader_template = """
        <div class="weeks">
          <div class="week-number d-flex">
          </div>
          {}
        </div>
        """
        s = ''.join(self._formatweekday(i) for i in self.iterweekdays())
        return weekheader_template.format(s)

    def _formatmonth(self):
        v = []
        a = v.append
        a('<div class="calendar">')
        a(self._formatweekheader())
        a('<div class="dates">')
        for week in self.monthdays2calendar(self._year, self._month):
            a(self._formatweek(week))
        a('</div>')
        a('</div>')
        return ''.join(v)


register = template.Library()


@register.simple_tag()
def calendar(year, month, bookings):
    cal = BootstrapCalendar(year, month, bookings)
    return mark_safe(cal.render())


@register.filter()
def month_name(month):
    return _(cal.month_name[month])
