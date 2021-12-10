from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    
    def __str__(self):
        return  self.profile.name


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    WEX = models.DateField()
    DOB = models.DateField()
    level = models.IntegerField(default=2)
    PTO = models.IntegerField(default=0)
    team = models.IntegerField()
    OFF = models.IntegerField(default=0)

    def __str__(self):
        return  self.name