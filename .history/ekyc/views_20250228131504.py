from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse

import threading

from .forms import CustomUserCreationForm, CustomAuthenticationForm, PinVerificationForm
from ekyc import logger
from .models import CustomUser
from .HumanV import HumanVerificationSystem
from .NLP import UserInfo, get_user_info
from .OCR import capture_image_with_guide, extract_text_with_confidence, extract_aadhar_details

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

def home(request):
    return render(request, 'home.html')

def human_verification(request):
    verifier = HumanVerificationSystem()
    result = verifier.verify_human()
    if result:
        return JsonResponse({'status': 'success', 'message': 'Human verification successful!'})
    else:
        return JsonResponse({'status': 'failure', 'message': 'Human verification failed or interrupted.'})

def nlp_process(request):
    user_info = UserInfo()
    stop_event = threading.Event()
    info_thread = threading.Thread(target=get_user_info, args=(stop_event, user_info))
    info_thread.start()
    info_thread.join()
    return JsonResponse({
        'status': 'success',
        'first_name': user_info.first_name,
        'last_name': user_info.last_name,
        'age': user_info.age,
        'phone': user_info.phone
    })

def ocr_process(request):
    image_path = capture_image_with_guide()
    if not image_path:
        return JsonResponse({'status': 'failure', 'message': 'Image capture failed.'})
    
    text_results = extract_text_with_confidence(image_path)
    if not text_results:
        return JsonResponse({'status': 'failure', 'message': 'No text could be extracted from the image.'})
    
    details = extract_aadhar_details(text_results)
    return JsonResponse(details)


