from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from utils.custom_user_manager import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


#ITS ABOUT SENDING AND RECEVING THE CODE FROM THE USER FOR EMAIL VARIFICATION.
# class SendCode(models.Model):
#     user = models.OneToOneField(CustomUser, null=True, on_delete=models.CASCADE)
#     send_code = models.CharField(max_length=20)
#
#     def __str__(self):
#         return self.send_code
#
# class ReceivedCode(models.Model):
#     user = models.OneToOneField(CustomUser, null=True, on_delete=models.CASCADE)
#     received_code = models.CharField(max_length=20)
#
#     def __str__(self):
#         return self.received_code
#


# Create your models here.
class KYCSession(models.Model):
    name = models.CharField(max_length=100)
    birth_date = models.DateField()
    id_card_image = models.ImageField(upload_to='id_cards/')
    liveness_score = models.FloatField()
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

