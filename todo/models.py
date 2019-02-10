from django.db import models
from django.contrib.auth.models import User
import os 
# Create your models here.

def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstlogin = models.BooleanField(default=False)
    code = models.CharField(max_length=6)
    code_created = models.DateField(auto_now=False, auto_now_add=False)
    avatar = models.ImageField(upload_to=get_image_path, blank=True, null=True)

class Todo(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


