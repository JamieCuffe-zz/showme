from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Greeting
from .models import Certs

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    c = Certs()
    c.save()
    certificates = Certs.objects.all()
    if not certificates:
    	return render(request, 'nodata.html')
    else:
    	return render(request, 'index.html', {'certificates': certificates})


def db(request):

	greeting = Greeting()
	greeting.save()

	greetings = Greeting.objects.all()

	return render(request, 'db.html', {'greetings': greetings})

def testjson(request):
    responseData = {
    'id' : 4,
    'name' : 'Test Response',
    'roles' : ['Admin', 'User']
    }
    return JsonResponse(responseData)

