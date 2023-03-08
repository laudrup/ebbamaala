import logging

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import signals
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.utils import translation

from .models import Booking

logger = logging.getLogger(__name__)


def send_emails(subject, template, booking):
    users = User.objects.exclude(pk=booking.user.pk).filter(is_superuser=True)
    for user in users:
        if not user.email:
            continue
        with translation.override('da'):  # TODO: Use users preferred language
            body = render_to_string(template, {'booking': booking, 'user': user})
        logger.debug(f'Sending email to {user.email}. Subject: {subject}. Body: {body}')
        send_mail(subject, body, 'admin@ebbamaala.se', [user.email], fail_silently=False)


def booking_changed(sender, instance, created, **kwargs):
    if created:
        logger.info(f'{instance} has been created')
        subject = _('New booking of the house in Ebbamåla')
    else:
        logger.info(f'{instance} has been updated')
        subject = _('Booking of the house in Ebbamåla has been updated')
    send_emails(subject, 'email/booking_created.txt', instance)


def booking_deleted(sender, instance, **kwargs):
    logger.info(f'{instance} has been deleted')
    send_emails(_('A booking of the house in Ebbamåla has been cancelled'),
                'email/booking_deleted.txt',
                instance)


signals.post_save.connect(booking_changed, sender=Booking)
signals.post_delete.connect(booking_deleted, sender=Booking)
