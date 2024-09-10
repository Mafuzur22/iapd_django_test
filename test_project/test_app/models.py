from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class profileDataModel(models.Model):
  name = models.CharField(max_length=50)
  roll = models.PositiveIntegerField()
  p_image = models.CharField(max_length=50)
  #p_image = models.ImageField(upload_to='profile_images')
  
  def __str__(self):
    return self.name
    
class OTP(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  otp = models.CharField(max_length=6)
  created_at = models.DateTimeField(default=timezone.now)
  expires_at = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))

  def is_expired(self):
    return timezone.now() > self.expires_at