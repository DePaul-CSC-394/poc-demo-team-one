from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address_line1 = models.TextField(blank=True)
    address_line2 = models.TextField(blank=True)
    city = models.TextField(blank=True)
    state = models.CharField(blank=True, max_length=2)
    emergency_name = models.TextField(blank=True)
    emergency_phone = models.TextField(blank=True)
    phone = models.TextField(blank=True)
    intro = models.TextField(blank=True)
    looking_roomate = models.BooleanField(blank=True, default=False)
    name = models.TextField(blank=True)
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True, max_length=500, default="/media/photos/2025/03/03/profile_placeholder.png")
    gender = models.TextField(default="female", max_length=6)

#used chatgpt assistance to figure out how to create profile object everytime a user is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()