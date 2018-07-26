from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import markdownx.models
import website.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Frontpage',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True,
                                        serialize=False,
                                        verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_now=True)),
                ('content', markdownx.models.MarkdownxField(verbose_name='Content')),
            ],
            options={
                'verbose_name': 'Frontpage',
                'verbose_name_plural': 'Frontpages',
            },
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True,
                                        serialize=False,
                                        verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('description', models.CharField(blank=True,
                                                 max_length=500,
                                                 verbose_name='Description')),
                ('pub_date', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(editable=False, unique=True)),
            ],
            options={
                'verbose_name': 'Photo Gallery',
                'verbose_name_plural': 'Photo Galleries',
            },
        ),
        migrations.CreateModel(
            name='GalleryPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True,
                                        serialize=False,
                                        verbose_name='ID')),
                ('photo', models.ImageField(upload_to=website.models.gallery_path,
                                            verbose_name='Photo')),
                ('description', models.CharField(blank=True,
                                                 max_length=500,
                                                 verbose_name='Description')),
                ('date', models.DateTimeField(editable=False,
                                              null=True,
                                              verbose_name='Photo Date')),
                ('gallery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              to='website.Gallery')),
            ],
            options={
                'verbose_name': 'Photo',
                'verbose_name_plural': 'Photos',
            },
        ),
        migrations.CreateModel(
            name='HeaderImage',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True,
                                        serialize=False,
                                        verbose_name='ID')),
                ('photo', models.ImageField(upload_to='headers', verbose_name='Photo')),
            ],
            options={
                'verbose_name': 'HeaderImage',
                'verbose_name_plural': 'HeaderImages',
            },
        ),
        migrations.CreateModel(
            name='PracticalInfo',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True,
                                        serialize=False,
                                        verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_now=True)),
                ('content', markdownx.models.MarkdownxField(verbose_name='Content')),
            ],
            options={
                'verbose_name': 'Practical Info',
                'verbose_name_plural': 'Practical Info',
            },
        ),
    ]
