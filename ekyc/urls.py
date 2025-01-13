from django.urls import path
from . import views


urlpatterns = [
    path('', views.ekyc_home, name="ekyc_home"),
    path('process_video/', views.process_video, name="process_video"),
    path('process_id_card/', views.process_id_card, name="process_id_card"),
]
