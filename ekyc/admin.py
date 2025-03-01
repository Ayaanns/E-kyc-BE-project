from django.contrib import admin
from .models import CustomUser, KYCSession

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(KYCSession)
