from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.RenameField('Booking', 'start', 'start_date'),
        migrations.RenameField('Booking', 'end', 'end_date'),
    ]
