from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="Home"),
    path('create', views.addStd, name="AddStudent"),
    path('register', views.register_user, name="AddUser"),
    path('verify_otp', views.verify_otp),
    path('login', views.login_user, name="LoginUser"),
    path('logout', views.logout_user)
]
