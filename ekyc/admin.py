from django.contrib import admin
<<<<<<< HEAD
# from .models import CustomUser, SendCode, ReceivedCode
#
# # Register your models here.
# admin.site.register(CustomUser)
# admin.site.register(SendCode)
# admin.site.register(ReceivedCode)
=======
from .models import CustomUser, KYCSession

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(KYCSession)
>>>>>>> dev
