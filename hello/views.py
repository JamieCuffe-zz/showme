from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting
from .models import Certificates

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')

    #NEW
    certificate = Certs(
    	name = "Applications of Computing", prereqs = "COS 126", 
    	name = "sorex", phonenumber = "002376970"
    	)
    
    certificate.save()

    #END NEW
    return render(request, 'index.html')


def db(request):

	greeting = Greeting()
	greeting.save()

	greetings = Greeting.objects.all()

	return render(request, 'db.html', {'greetings': greetings})

