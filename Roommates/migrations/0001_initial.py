# Generated by Django 5.1.6 on 2025-03-10 16:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RoommateResponses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owns_pets', models.BooleanField(blank=True, null=True)),
                ('okay_with_pets', models.BooleanField(blank=True, null=True)),
                ('okay_with_female', models.BooleanField(blank=True, null=True)),
                ('okay_with_male', models.BooleanField(blank=True, null=True)),
                ('cleanliness', models.BooleanField(blank=True, null=True)),
                ('work_study', models.BooleanField(blank=True, null=True)),
                ('quiet_night', models.BooleanField(blank=True, null=True)),
                ('host_gatherings', models.BooleanField(blank=True, null=True)),
                ('share_supplies', models.BooleanField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
