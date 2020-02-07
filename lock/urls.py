from django.urls import path
from . import views

urlpatterns = [
    path('', views.index , name="index"),
    path('login', views.user_login, name='login'),
    path('pre_register', views.user_pre_register),
    path('register/<id>', views.user_register, name='register'),
    path('logout', views.user_logout, name="logout"),
    path('share_sms/<otp>', views.share_sms),
    path('share_email/<otp>', views.share_email),
    path('lock_history', views.lock_history),
    path('api_test', views.api_test)
]