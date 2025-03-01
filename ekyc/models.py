from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
<<<<<<< HEAD
from utils.custom_user_manager import CustomUserManager

=======
from django.utils import timezone
import random

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        #extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # if not extra_fields.get('is_staff'):
        #     raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)
>>>>>>> dev

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    pin = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


<<<<<<< HEAD
#ITS ABOUT SENDING AND RECEVING THE CODE FROM THE USER FOR EMAIL VARIFICATION.
# class SendCode(models.Model):
#     user = models.OneToOneField(CustomUser, null=True, on_delete=models.CASCADE)
=======
    def generate_pin(self):
        self.pin = str(random.randint(100000, 999999))
        self.expires_at = timezone.now() + timezone.timedelta(minutes=2)
        self.save()
        return self.pin

    def verify_pin(self, entered_pin):
        if timezone.now() > self.expires_at:
            return False, "PIN has Expired!"

        if self.pin != entered_pin:
            return False, "Incorrect PIN!"

        self.is_verified = True
        self.save()
        return True, "Email Successfully Verified!"


#models for sending the code and receving the code.
# class SendCode(models.Model): #for sending the code
#     email = models.OneToOneField(CustomUser, null=True, on_delete=models.CASCADE)
>>>>>>> dev
#     send_code = models.CharField(max_length=20)
#
#     def __str__(self):
#         return self.send_code
#
<<<<<<< HEAD
# class ReceivedCode(models.Model):
#     user = models.OneToOneField(CustomUser, null=True, on_delete=models.CASCADE)
#     received_code = models.CharField(max_length=20)
#
#     def __str__(self):
#         return self.received_code
#

=======
# class ReceivedCode(models.Model): #for sending the code
#     email = models.OneToOneField(CustomUser, null=True, on_delete=models.CASCADE)
#     receive_code = models.CharField(max_length=20)
#
#     def __str__(self):
#         return self.receive_code
>>>>>>> dev

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

