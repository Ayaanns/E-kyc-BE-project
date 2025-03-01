from django.urls import path
from . import views

urlpatterns = [
    path('', views.ekyc_home, name="ekyc_home"),
    path('process_video/', views.process_video, name="process_video"),
    path('process_id_card/', views.process_id_card, name="process_id_card"),
    path('human_verification/', views.human_verification, name='human_verification'),
    path('nlp_process/', views.nlp_process, name='nlp_process'),
    path('ocr_process/', views.ocr_process, name='ocr_process'),

    #login related routes
    path('login/', views.Login.as_view(), name="login"),
    path('signup/', views.signup_view, name="signup"),
    path('verify/', views.verify_pin, name="verify_pin"),
]
