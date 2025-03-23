# Generated by Django 5.1.6 on 2025-02-22 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Housing', '0007_alter_housinglisting_photo_1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='housingbooking',
            name='was_denied',
            field=models.BooleanField(blank=True, default=True),
        ),
        migrations.AlterField(
            model_name='housinglisting',
            name='photo_1',
            field=models.ImageField(blank=True, max_length=500, upload_to='photos/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='housinglisting',
            name='photo_2',
            field=models.ImageField(blank=True, max_length=500, upload_to='photos/%Y/%m/%d/'),
        ),
    ]
