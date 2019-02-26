from django.db import models
from django.contrib.auth.models import User
from fernet_fields import EncryptedTextField
import os 
# Create your models here.

def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.id), filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', primary_key=True)
    firstlogin = models.BooleanField(default=True)
    code = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=20)
    code_created = models.DateTimeField(null=True)
    avatar = models.ImageField(upload_to='uploads/', blank=True, null=True)


class AlpacaAPIKeys(models.Model):
    id = models.IntegerField(primary_key=True)
    key_id = EncryptedTextField(max_length=None)
    secret_key = EncryptedTextField(max_length=120)


