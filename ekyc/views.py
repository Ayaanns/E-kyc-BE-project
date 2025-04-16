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
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import cv2
import json
import base64
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import datetime

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from ekyc import logger
from .models import CustomUser
from .HumanV import HumanVerificationSystem
from .NLP import UserInfo, get_user_info
from .OCR import extract_text_with_confidence, extract_aadhar_details, process_single_frame, process_multiple_frames

User = get_user_model()

@login_required
def ekyc_home(request):
    return render(request, 'home.html')

def signup_view(request):
    logger.info("into the signup page view")
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=user.email, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('ekyc_home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

class Login(SuccessMessageMixin, LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('ekyc_home')
    success_message = "Successfully logged in!"
    form_class = CustomAuthenticationForm

    def get_success_url(self):
        return self.success_url

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
    """Handle NLP process and trigger OCR process sequentially"""
    try:
        user_info = UserInfo()
        stop_event = threading.Event()
        info_thread = threading.Thread(target=get_user_info, args=(stop_event, user_info))
        info_thread.start()
        info_thread.join()

        if any(value.startswith("Waiting for") for value in [
            user_info.first_name, 
            user_info.last_name, 
            user_info.age, 
            user_info.phone
        ]):
            return JsonResponse({
                'status': 'error',
                'message': 'NLP process failed to collect all required information'
            })

        # Return only NLP results first - OCR will be handled by separate request
        return JsonResponse({
            'status': 'success',
            'first_name': user_info.first_name,
            'last_name': user_info.last_name,
            'age': user_info.age,
            'phone': user_info.phone
        })

    except Exception as e:
        logger.error(f"Error in NLP process: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })
    finally:
        stop_event.set()

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

@csrf_exempt
def ocr_process(request):
    """Quick OCR process with single frame check"""
    try:
        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

        data = json.loads(request.body)
        frame_data = data.get('frame')
        
        # Process frame
        frame_bytes = base64.b64decode(frame_data.split(',')[1])
        frame_arr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(frame_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return JsonResponse({'status': 'detecting', 'message': 'Invalid frame data'})

        # Quick process single frame
        card_detected, result = process_multiple_frames(frame, num_frames=1)
        
        if card_detected:
            if result:
                print(f"OCR Results: {result}")
                return JsonResponse({
                    'status': 'success',
                    'message': 'OCR completed',
                    'results': result
                })
            return JsonResponse({
                'status': 'detecting',
                'message': 'Card detected, retrying OCR...'
            })
        
        return JsonResponse({
            'status': 'detecting',
            'message': 'Looking for Aadhar card...'
        })

    except Exception as e:
        logger.error(f"Error in OCR process: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


