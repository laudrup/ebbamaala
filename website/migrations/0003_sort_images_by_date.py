from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_add_booking_model'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='galleryphoto',
            options={'ordering': ['date'], 'verbose_name': 'Photo', 'verbose_name_plural': 'Photos'},
        ),
    ]
