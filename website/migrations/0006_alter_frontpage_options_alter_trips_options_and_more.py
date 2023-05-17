# Generated by Django 4.1.7 on 2023-05-16 19:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0005_trips"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="frontpage",
            options={
                "get_latest_by": "pub_date",
                "verbose_name": "Frontpage",
                "verbose_name_plural": "Frontpages",
            },
        ),
        migrations.AlterModelOptions(
            name="trips",
            options={
                "get_latest_by": "pub_date",
                "verbose_name": "Tips for Trips",
                "verbose_name_plural": "Tips for Trips",
            },
        ),
        migrations.RemoveField(
            model_name="booking",
            name="approved",
        ),
    ]