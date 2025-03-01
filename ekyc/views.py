from django.shortcuts import render, redirect
from django.urls import reverse_lazy
<<<<<<< HEAD
from django.http import HttpResponse

#USER CREATIONS RELATED MODULES
=======
>>>>>>> dev
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import cv2
import json
import base64

import threading

<<<<<<< HEAD
#EMAIL RELATED MODULES
from .token import account_activation_token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
#---
#from .mail_send import EmailConfirmation


#USER DEFINED MODULES (CREATED)
from .forms import CustomUserCreationForm, CustomAuthenticationForm
=======
from .forms import CustomUserCreationForm, CustomAuthenticationForm, PinVerificationForm
>>>>>>> dev
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
<<<<<<< HEAD
            user.is_active = False
            user.save()
            email = form.cleaned_data.get('email')
            mail_system(request, user, email)
            login(request, user)  # Log the user in after successful signup
            return redirect('login')
=======
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
>>>>>>> dev
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

<<<<<<< HEAD
#just for email varification and checking.
def mail_system(request, user, to_email):
    mail_subject = "Activation link has been sent to your email id"
    message = render_to_string("acc_active_email.html", {
        'user': user, 
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': "https" if request.is_secure() else "http"
    })
    #to_email = form.cleaned_data.get('email')
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        return HttpResponse("Please confirm your email address to complete the registration")
    else:
        return HttpResponse("Something is wrong, Please check your email!")

def activate(request, uidb64, token):  
    return redirect('home')
    # User = get_user_model()  
    # try:  
    #     uid = force_text(urlsafe_base64_decode(uidb64))  
    #     user = User.objects.get(pk=uid)  
    # except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
    #     user = None  
    # if user is not None and account_activation_token.check_token(user, token):  
    #     user.is_active = True  
    #     user.save()  
    #     return HttpResponse('Thank you for your email confirmation. Now you can login your account.')  
    # else:  
    #     return HttpResponse('Activation link is invalid!')  

# def login_view(request):
#     print("hello world")
#     if request.method == 'POST':
#         form = CustomAuthenticationForm(data=request.POST)
#         print("hello --here we go")
#         if form.is_valid():
#             print("gosh --inside")
#             email = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, username=email, password=password)
#             print("ohh yeah! --pass the test")
#             if user is not None:
#                 print("success! --redirect to home")
#                 login(request, user)
#                 return redirect('ekyc_home')
#     else:
#         form = CustomAuthenticationForm()
#     return render(request, 'login.html', {'form': form})
# def signup(request):
#     if request.method == "POST":
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             # Use the saved user's email rather than form data
#             #email = user.email
#
#             ## Get raw password before it's hashed
#             #raw_password = form.cleaned_data.get('password1')
#
#             ## Authenticate with the raw password
#             #user = authenticate(request, email=email, password=raw_password)
#
#             if user is not None:  # Changed condition to check if user exists
#                 login(request, user)
#                 return redirect('ekyc_home')  # Redirect to home after successful signup
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'signup.html', {'form': form})
#
# #login route here
class Login(SuccessMessageMixin, LoginView):  # Inherit from LoginView instead of CreateView
    logger.info("INTO THE LOGIN PAGE RIGHT NOW!")
=======
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
>>>>>>> dev
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

@login_required
def human_verification(request):
    """Handle both GET (initial page load) and POST (frame processing) requests"""
    if request.method == 'GET':
        return render(request, 'human_verification.html')
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            frame_data = data.get('frame')
            
            if not frame_data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No frame data provided'
                })

            # Process the frame using verifier
            frame_bytes = base64.b64decode(frame_data.split(',')[1])
            frame_arr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(frame_arr, cv2.IMREAD_COLOR)
            
            result = verifier.verify_frame(frame)
            return JsonResponse(result)

        except Exception as e:
            logger.error(f"Error in human verification: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

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

verifier = HumanVerificationSystem()

@csrf_exempt
def process_frame(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'})

    try:
        data = json.loads(request.body)
        frame_data = data.get('frame')
        
        if not frame_data:
            return JsonResponse({'error': 'No frame data provided'})

        # Convert base64 to frame
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        frame_arr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(frame_arr, cv2.IMREAD_COLOR)

        # Process frame
        result = verifier.verify_frame(frame)
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def capture_photo(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'})

    try:
        data = json.loads(request.body)
        frame_data = data.get('frame')
        
        if not frame_data:
            return JsonResponse({'error': 'No frame data provided'})

        # Convert base64 to frame
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        frame_arr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(frame_arr, cv2.IMREAD_COLOR)

        # Save photo
        filename = verifier.save_photo(frame)
        if filename:
            return JsonResponse({'success': True, 'filename': filename})
        else:
            return JsonResponse({'error': 'Failed to save photo'})

    except Exception as e:
        return JsonResponse({'error': str(e)})


