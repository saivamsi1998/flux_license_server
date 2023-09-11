import datetime

from django.db import models
from django.utils import timezone

class User(models.Model):
    user_id = models.CharField(max_length=500)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    def __str__(self):
        return self.email

class Offer(models.Model):
    license_id = models.CharField(max_length=500)
    max_license_count = models.IntegerField()
    active_license_count = models.IntegerField(default=0)
    def __str__(self):
        return self.license_id

class OfferAppMap(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    app_id = models.CharField(max_length=100)
    def __str__(self):
        return str(self.offer) + " - " + self.app_id

class OfferUserMap(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.offer) + " - " + str(self.user)

class License(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=500)
    def __str__(self):
        return self.user.email + "/" + self.device_id

class LicenseAppMap(models.Model):
    license = models.ForeignKey(License, on_delete=models.CASCADE)
    app_id = models.CharField(max_length=100)
    last_active_time = models.DateTimeField("last active time")
    def __str__(self):
        return str(self.license) + " - " + self.app_id
