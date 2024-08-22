from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="Home"),
    path('create', views.addStd, name="AddStudent")
]
