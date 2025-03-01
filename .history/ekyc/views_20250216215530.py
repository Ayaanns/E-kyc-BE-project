# #BACKEND REQUIRED MODULES FOR
# from django.shortcuts import render, redirect
# from django.urls import reverse_lazy
#
# #USER CREATIONS RELATED MODULES
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import login, logout, authenticate, get_user_model
# #from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
# #from django.contrib.auth.models import User
# from django.contrib.messages.views import SuccessMessageMixin
# from django.contrib.auth.views import LoginView
# from django.contrib import messages
#
# #CBV MODELS
# from django.views.generic import CreateView
#
# #USER DEFINED MODULES (CREATED)
# from .forms import CustomUserCreationForm, CustomAuthenticationForm, PinVerificationForm
# from ekyc import logger
#
# #EMAIL RELATED IMPORTS
# #from .model import SendCode, ReceivedCode
# import string
# import random
# from django.core.mail import send_mail
# from django.conf import settings
# from .models import CustomUser
#
# def send_verification_email(request, user):
#     subject = "Email Verification PIN"
#     message = f"""
#     Hello {request.user.username},
#
#     Your email verification PIN is: {user.pin}
#
#     This PIN will expire in 24 hours.
#
#     Thank you,
#     Your Website Team
#     """
#     from_email = settings.DEFAULT_FROM_EMAIL
#     recipient_list = [user.email]
#
#     send_mail(subject, message, from_email, recipient_list)
#
#
#
# User = get_user_model()
#
# # Create your views here.
# @login_required
# def ekyc_home(request):
#     return render(request, 'home.html')
#
#
# def signup_view(request):
#     logger.info("into the signup page view")
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False
#             user.save()
#
#             #generate pin
#             user.generate_pin()
#
#
#             #rawpassword = form.cleaned_data.get('password1')
#             #user = authenticate(email=user.email, password=raw_password)
#             #login(request, user)
#
#
#             send_verification_email(request, user)
#             #
#             # if user is not None:
#             #     if user.is_active:
#             #         login(request, user)  # Log the user in after successful signup
#             #         send_verification_email(request, )
#             #         return redirect('e_verification')
#             #         #return redirect('login')
#             messages.success(request, f"Verification PIN sent to {user.email}.")
#             return redirect('verify_pin')
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'signup.html', {'form': form})
#
# # def login_view(request):
# #     print("hello world")
# #     if request.method == 'POST':
# #         form = CustomAuthenticationForm(data=request.POST)
# #         print("hello --here we go")
# #         if form.is_valid():
# #             print("gosh --inside")
# #             email = form.cleaned_data.get('username')
# #             password = form.cleaned_data.get('password')
# #             user = authenticate(request, username=email, password=password)
# #             print("ohh yeah! --pass the test")
# #             if user is not None:
# #                 print("success! --redirect to home")
# #                 login(request, user)
# #                 return redirect('ekyc_home')
# #     else:
# #         form = CustomAuthenticationForm()
# #     return render(request, 'login.html', {'form': form})
# # def signup(request):
# #     if request.method == "POST":
# #         form = CustomUserCreationForm(request.POST)
# #         if form.is_valid():
# #             user = form.save()
# #             # Use the saved user's email rather than form data
# #             #email = user.email
# #
# #             ## Get raw password before it's hashed
# #             #raw_password = form.cleaned_data.get('password1')
# #
# #             ## Authenticate with the raw password
# #             #user = authenticate(request, email=email, password=raw_password)
# #
# #             if user is not None:  # Changed condition to check if user exists
# #                 login(request, user)
# #                 return redirect('ekyc_home')  # Redirect to home after successful signup
# #     else:
# #         form = CustomUserCreationForm()
# #     return render(request, 'signup.html', {'form': form})
# #
# # #login route here
# #@login_required
# def verify_pin(request):
#     # try:
#     #     email_verification = CustomUser.objects.get(user=request.user)
#     # except CustomUser.DoesNotExist:
#     #     messages.error(request, "Please request email verification first.")
#     #     return redirect('email_verify')
#     if not request.user.is_authenticated:
#         messages.info(request, "Please login to verify your email!")
#         return redirect('login')
#
#     email_verification = request.user
#
#     if email_verification.is_verified:
#         messages.info(request, "Your email is already verified.")
#         return redirect("ekyc_home")
#
#     if request.method == "POST":
#         form = PinVerificationForm(request.POST)
#         if form.is_valid():
#             entered_pin = form.cleaned_data.get('pin')
#             success, message = email_verification.verify_pin(entered_pin)
#
#             if success:
#                 #email_verification.is_active = True 
#                 messages.success(request, message)
#                 return redirect('login')
#             else:
#                 messages.error(request, message)
#
#     else:
#         form  = PinVerificationForm()
#     return render(request, 'signup.html', {'form': form})
#
#
# class Login(SuccessMessageMixin, LoginView):  # Inherit from LoginView instead of CreateView
#     logger.info("INTO THE LOGIN PAGE RIGHT NOW!")
#     template_name = 'login.html'
#     success_url = reverse_lazy('ekyc_home')
#     success_message = "Successfully logged in!"  # Add a success message
#     form_class = CustomAuthenticationForm
#
#     def get_success_url(self):
#         return self.success_url
#
#     def form_valid(self, form):
#         """Security check complete. Log the user in."""
#         user = form.get_user()
#         if not user.is_verified:
#             messages.error(self.request, "Please verify your email before logging in!")
#             return redirect('verify_pin')
#         response = super().form_valid(form)
#         return response

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .forms import CustomUserCreationForm, CustomAuthenticationForm, PinVerificationForm
from ekyc import logger
from .models import CustomUser

User = get_user_model()

def send_verification_email(user):
    subject = "Email Verification PIN"
    message = f"""
    Hello {user.username},
    
    Your email verification PIN is: {user.pin}
    
    This PIN will expire in 24 hours.
    
    Thank you,
    Your Website Team
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    send_mail(subject, message, from_email, recipient_list)

@login_required
def ekyc_home(request):
    return render(request, 'home.html')

def signup_view(request):
    logger.info("into the signup page view")
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # User needs to be active to log in
            user.is_verified = False  # But not verified yet
            user.generate_pin()
            user.save()

            # Send verification email
            send_verification_email(user)
            
            # Log in the user after signup
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=user.email, password=raw_password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Verification PIN sent to {user.email}.")
                return redirect('verify_pin')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def verify_pin(request):
    user = request.user

    if user.is_verified:
        messages.info(request, "Your email is already verified.")
        return redirect("ekyc_home")

    if request.method == "POST":
        form = PinVerificationForm(request.POST)
        if form.is_valid():
            entered_pin = form.cleaned_data.get('pin')
            success, message = user.verify_pin(entered_pin)

            if success:
                user.is_verified = True
                user.save()
                messages.success(request, message)
                return redirect('ekyc_home')
            else:
                messages.error(request, message)
    else:
        form = PinVerificationForm()
    
    return render(request, 'signup.html', {'form': form})

class Login(SuccessMessageMixin, LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('ekyc_home')
    success_message = "Successfully logged in!"
    form_class = CustomAuthenticationForm

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        user = form.get_user()
        if not user.is_verified:
            messages.error(self.request, "Please verify your email before logging in.")
            login(self.request, user)
            return redirect('verify_pin')
        return super().form_valid(form)

#--MAIN FEATURS HERE ---------------------------------
@login_required
def process_video(request):
    logger.info("INTO THE process_video PAGE RIGHT NOW!")
    if request.method == "POST":
        video_feed = request.FILES.get('video')
        liveness_score = 0.95
        return JsonResponse({'liveness_score': liveness_score})
    return JsonResponse({'error': 'invalide request'})


@login_required
def process_id_card(request):
    logger.info("INTO THE process_id_card PAGE RIGHT NOW!")
    if request.method == "POST":
        id_image = request.FILES.get('id_image')
        result = "Valid ID"
        return JsonResponse({'result': result})
    return JsonResponse({'error': 'invalide request'})


