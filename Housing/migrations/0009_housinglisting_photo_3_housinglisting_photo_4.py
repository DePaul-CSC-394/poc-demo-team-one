# Generated by Django 5.1.6 on 2025-03-05 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Housing', '0008_housingbooking_was_denied_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='housinglisting',
            name='photo_3',
            field=models.ImageField(blank=True, max_length=500, upload_to='photos/%Y/%m/%d/'),
        ),
        migrations.AddField(
            model_name='housinglisting',
            name='photo_4',
            field=models.ImageField(blank=True, max_length=500, upload_to='photos/%Y/%m/%d/'),
        ),
    ]
