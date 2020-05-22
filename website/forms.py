from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Booking


class BookingForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['booker'].initial = user.get_full_name()

    class Meta:
        model = Booking
        fields = ('booker', 'description', 'start_date', 'end_date')
        localized_fields = ('start_date', 'end_date')
        widgets = {
            'start_date': forms.TextInput(attrs={'class': 'form-control'}),
            'end_date': forms.TextInput(attrs={'class': 'form-control'}),
            'booker': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'placeholder':
                                                 _('Any relevant information related to your booking')}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if not start_date or not end_date:
            return cleaned_data
        if end_date < start_date:
            raise forms.ValidationError(_('Booking cannot end before it starts.'),
                                        code='invalid')

        overlapping_booking = self._find_overlapping(start_date, end_date)
        if overlapping_booking:
            raise forms.ValidationError(_('{user} has already booked these dates.'
                                          .format(user=overlapping_booking.user)),
                                        code='invalid')
        return cleaned_data

    def save(self):
        booking = super().save(commit=False)
        booking.user = self.user
        if self.user.is_superuser:
            booking.approved = True
        booking.save()
        return booking

    def _find_overlapping(self, start_date, end_date):
        for booking in Booking.objects.all():
            if end_date >= booking.start_date and booking.end_date >= start_date:
                return booking
