from django.shortcuts import render,redirect
from .models import profileDataModel
from django.contrib import messages

# Create your views here.
def home(request):
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
  db_data = profileDataModel.objects.all()
  context = {
    "data":db_data,

  }
  return render(request, "base.html", context)