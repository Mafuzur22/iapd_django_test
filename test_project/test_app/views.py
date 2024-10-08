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
    db_data = profileDataModel.objects.filter(name__icontains = query)
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
    if validate_password(password) != "pass_ok":
      messages.error(request, validate_password(password))
      return redirect("/register")
    if password != password2:
      messages.error(request, "Confirm Password Does,t match.")
      return redirect("/register")

    user = User.objects.create_user(username=username,first_name=first_name, last_name=last_name, email=email, password=password, is_active=False)
    user.set_password(password)
    otp = generate_otp()
    subject = "Email Verification Code."
    send_otp(user, subject, otp)

    return render(request, "verify_otp.html", {'user_id': user.id})


  context = {


  }
  return render(request, 'register.html', context)

def verify_otp(request):
  if request.method == 'POST':
    user_id = request.POST.get('user_id')
    otp = request.POST.get('otp')
    int(user_id)

    try:
      otp_record = OTP.objects.get(user_id=user_id, otp=otp)

      if otp_record.is_expired():
        # Handle expired OTP
        otp_record.delete()  # Optional: remove expired OTP
        return render(request, 'verify_otp.html', {'error': 'OTP has expired. Please request a new one.'})

      # If OTP is valid and not expired
      user = User.objects.get(id=user_id)
      user.is_active = True
      user.save()
      otp_record.delete()
      messages.success(request, "User Created") # Optional: remove OTP after use
      return redirect('/login')
    except OTP.DoesNotExist:
      # Handle invalid OTP
      return render(request, 'verify_otp.html', {'error': 'Invalid OTP.'})

  return render(request, 'verify_otp.html')

def send_notifi_mail(user, subject, message):
  subject = subject
  message = message
  from_email = settings.EMAIL_HOST_USER
  recipient = [user.email]
  send_mail(subject, message, from_email, recipient, fail_silently=False)

def login_user(request):
  if request.method == "POST":
    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      subject = "LogIn Alert"
      message = f"Your account has been signed in {user.username}"
      send_notifi_mail(user, subject, message)
      return redirect("/")

    else:
      messages.error(request, "User Not Found")
  context = {


  }
  return render(request, 'login.html', context)

def logout_user(request):
  user = request.user
  logout(request)
  subject = "LogOut Alert"
  message = f"Your account has been signed out {user.username}"
  send_notifi_mail(user, subject, message)
  return redirect("/login")


def reset_user_password(request):
  if request.method == "POST":
    try:
      username = request.POST['username']
      new_password = request.POST['new_password1']
      new_password2 = request.POST['new_password2']

      if validate_password(new_password) != "pass_ok":
        messages.error(request, validate_password(new_password))
        return redirect("/reset")
      if new_password != new_password2:
        messages.error(request, "Confirm Password Does,t match.")
        return redirect("/reset")

      user = User.objects.get(username=username)
      otp = generate_otp()
      subject = "Email Verification Code."
      send_otp(user, subject, otp)

      return render(request, "verify_pass_otp.html", {'user_id': user.id, 'new_password': new_password})


    except User.DoesNotExist:
      messages.error(request, 'User does not exist.')
      return redirect('/login')
  return render(request, 'reset_password.html')

def reset_verify(request):
  if request.method == 'POST':
    user_id = request.POST.get('user_id')
    otp = request.POST.get('otp')
    int(user_id)
    new_password = request.POST['new_password']

    try:
      otp_record = OTP.objects.get(user_id=user_id, otp=otp)

      if otp_record.is_expired():
        # Handle expired OTP
        otp_record.delete()  # Optional: remove expired OTP
        return render(request, 'verify_pass_otp.html', {'error': 'OTP has expired. Please request a new one.'})

      # If OTP is valid and not expired
      user = User.objects.get(id=user_id)
      user.set_password(new_password)
      user.save()
      otp_record.delete()
      messages.success(request, "Password Reset") # Optional: remove OTP after use
      return redirect('/login')
    except OTP.DoesNotExist:
      # Handle invalid OTP
      return render(request, 'verify_pass_otp.html', {'error': 'Invalid OTP.'})

  return render(request, 'verify_pass_otp.html')