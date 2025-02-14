import string
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import SendCode


def EmailConfirmation(request, emailto, username, password):
    chars = ''.join((string.digits))
    conf_code = ''.join(random.choice(chars) for _ in range(6))
    code = SendCode.object.filter(user=request.user).create(send_code=conf_code)
    code.user = request.user
    code.save()


    content = f"Hello, {username}\nThanks for signing up on our site\nVerification Code : {conf_code}\n"

    send_mail(
        "Email Confirmation Code", #subject of the mail
        content, # mail body
        settings.EMAIL_HOST_USER #from 
        [username],
        fail_silently=False,
    )
