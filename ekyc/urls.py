from django.urls import path
from . import views


urlpatterns = [
    path('', views.ekyc_home, name="ekyc_home"),
    path('process_video/', views.process_video, name="process_video"),
    path('process_id_card/', views.process_id_card, name="process_id_card"),

    #login related routes
    path('login/', views.Login.as_view(), name="login"),
    # path('signup/', views.signup, name="signup"),
    # path('login/', views.login_view, name="login"),
    path('signup/', views.signup_view, name="signup"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),  
]
