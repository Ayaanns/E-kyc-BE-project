#BACKEND REQUIRED MODULES FOR
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

#USER CREATIONS RELATED MODULES
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, get_user_model
#from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
#from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView

#CBV MODELS
from django.views.generic import CreateView

#USER DEFINED MODULES (CREATED)
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from ekyc import logger

User = get_user_model()

# Create your views here.
@login_required
def ekyc_home(request):
    return render(request, 'home.html')


"""
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
"""

def signup_view(request):
    logger.info("into the signup page view")
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after successful signup
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

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
    template_name = 'login.html'
    success_url = reverse_lazy('ekyc_home')
    success_message = "Successfully logged in!"  # Add a success message
    form_class = CustomAuthenticationForm

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        response = super().form_valid(form)
        return response

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


