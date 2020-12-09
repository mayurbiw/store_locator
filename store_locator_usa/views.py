from django.shortcuts import render, HttpResponse, HttpResponseRedirect, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

import json

# Create your views here.

# Create your views here.
def index(request):
    if request.user.is_authenticated:  
        return HttpResponseRedirect(reverse("generate_report"))

    if request.method == 'POST':  
        
        email = request.POST['InputEmail']
        password = request.POST['InputPassword']
        
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            user = User.objects.create_user(
            username = email,
            password = password,
            email = email
            )
            user.save()
            print(email)
            print(password) 
            return HttpResponseRedirect(reverse("generate_report"))

        else:
            login(request, user)  
            return HttpResponseRedirect(reverse("generate_report"))

    return render(request, "store_locator_usa/index.html", {"message": None}) 

def generate_report(request):
    return render(request, "store_locator_usa/generateReport.html", {"message": None})

def create_report(request,brandname):
    try:
       print(brandname)
    except:
        data = {
        "success": False
        }
        return HttpResponse(json.dumps(data))

    data  = {
        "success": True
    }
    return HttpResponse(json.dumps(data))

