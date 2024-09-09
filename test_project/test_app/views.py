from django.shortcuts import render,redirect
from .models import profileDataModel, OTP
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import re
import random

# Create your views here.
@login_required(login_url='/login')
def home(request):
  if request.method == "GET" and 'query' in request.GET:
    query = request.GET['query']
    db_data = profileDataModel.objects.filter(name__exact = query)
    context = {
     "data":db_data,

    }
    return render(request, "home.html", context)
  else:
    db_data = profileDataModel.objects.all()
    context = {
      "data":db_data,

    }
    return render(request, "home.html", context)
    
@login_required(login_url='/login')
def addStd(request):
  if request.method == "POST":

    c_dt = request.POST
    name = c_dt.get("name")
    roll = c_dt.get("roll")
    p_image = request.FILES.get("image")
    if not profileDataModel.objects.filter(name=name).exists():
        save_db = profileDataModel(name=name, roll=roll, p_image=p_image)
        save_db.save()
        return redirect('Home')
    else:
        messages.error(request, "message")
        return redirect('Home')
  context = {
    

  }
  return render(request, "create.html", context)
  
def validate_password(password):
    if not re.search(r'[A-Z]', password):
      return('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
      return('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', password):
      return('Password must contain at least one digit.')
    if len(password) <= 8:
      return('Password must be at least 8 characters long.')
    else:
      return ("pass_ok")
def generate_otp():
  otp = random.randint(1000, 9999)
  return otp
def send_otp(user, subject, otp):
  subject = subject
  message = f"You'r verification code is: {otp}"
  from_email = settings.EMAIL_HOST_USER
  recipient = [user.email]
  send_mail(subject, message, from_email, recipient, fail_silently=False)
  OTP.objects.create(user=user, otp=otp)
  return(f"An otp Has been sent to this {user.email} email")
  
def register_user(request):
  if request.method == "POST":
    username = request.POST.get("username")
    first_name = request.POST.get("name1")
    last_name = request.POST.get("name2")
    email = request.POST.get("email")
    password = request.POST.get("password1")
    password2 = request.POST.get("password2")
    if User.objects.filter(username=username).exists():
      messages.error(request, "Username already exists.")
      return redirect("/register")
    elif validate_password(password) == "pass_ok":
      user = User.objects.create_user(username=username,first_name=first_name, last_name=last_name, email=email, password=password, is_active=False)
      otp = generate_otp()
      subject = "Email Verification Code."
      send_otp(user, subject, otp)
      
      return render(request, "verify_otp.html", {'username': user.username, 'password': password})
    else:
      messages.error(request, validate_password(password))
      return redirect("/register")
  

  context = {
    

  }
  return render(request, 'register.html', context)
  
def verify_otp(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    otp = request.POST['otp']

    try:
      otp_record = OTP.objects.get(username=username, otp=otp)

      if otp_record.is_expired():
        # Handle expired OTP
        otp_record.delete()  # Optional: remove expired OTP
        return render(request, 'verify_otp.html', {'error': 'OTP has expired. Please request a new one.'})

      # If OTP is valid and not expired
      user = User.objects.get(username=username)
      user.is_active = True
      user.set_password(password)
      user.save()
      otp_record.delete()  # Optional: remove OTP after use
      return redirect('login')
    except OTP.DoesNotExist:
      # Handle invalid OTP
      return render(request, 'verify_otp.html', {'error': 'Invalid OTP.'})

  return render(request, 'verify_otp.html')
  
  
def login_user(request):
  if request.method == "POST":
    username = request.POST.get("username")
    password = request.POST.get("password")
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      
      return redirect("/")
    else:
      messages.error(request, "User Not Found")
  context = {
    

  }
  return render(request, 'login.html', context)
  
def logout_user(request):
  logout(request)
  return redirect("/login")
    
  