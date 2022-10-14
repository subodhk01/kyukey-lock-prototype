from django.db import models

from django.contrib.auth.models import User

class OTP(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=100)
    source = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class History(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=20)

class Lock(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=10)
    otp = models.CharField(max_length=100)

class PreRegistration(models.Model):
    email = models.CharField(max_length=20)
    registered = models.BooleanField(default=0)

class ShareHistory(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=10)
    source = models.CharField(max_length=20)
    destination = models.CharField(max_length=40)

class API(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=500)

