# Generated by Django 5.1.6 on 2025-03-11 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Roommates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='roommateresponses',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
