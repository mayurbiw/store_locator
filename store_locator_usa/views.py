import json
from django.shortcuts import render, HttpResponse, HttpResponseRedirect, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from .tasks import send_email_task


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
    
    print("creating a report for " + str(brandname) )
    
    try:
        send_email_task.delay(str(brandname),request.user.email)
        data  = {
            "success": True
        }
    
    except:
        data  = {
            "success": False
        }
    
    finally:
        return HttpResponse(json.dumps(data))




    

