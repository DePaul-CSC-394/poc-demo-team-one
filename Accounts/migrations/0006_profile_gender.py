# Generated by Django 5.1.6 on 2025-03-10 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0005_alter_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='gender',
            field=models.TextField(default='female', max_length=6),
        ),
    ]
