from django.db import models

# Create your models here.
class profileDataModel(models.Model):
  name = models.CharField(max_length=50)
  roll = models.PositiveIntegerField()
  #p_image = models.CharField(max_length=50)
  p_image = models.ImageField(upload_to='profile_images')
  
  def __str__(self):
    return self.name