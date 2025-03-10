from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class RoommateResponses(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Roommate Preferences
    owns_pets = models.BooleanField(null=True, blank=True)
    okay_with_pets = models.BooleanField(null=True, blank=True)
    okay_with_female = models.BooleanField(null=True, blank=True)
    okay_with_male = models.BooleanField(null=True, blank=True)
    cleanliness = models.BooleanField(null=True, blank=True)
    work_study = models.BooleanField(null=True, blank=True)
    quiet_night = models.BooleanField(null=True, blank=True)
    host_gatherings = models.BooleanField(null=True, blank=True)
    share_supplies = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"RoommateResponses for {self.user.username}"

