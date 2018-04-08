from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting
from .models import Certificates

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')

    #NEW
    certificate = Certificates(
    	name = "Applications of Computing", prereqs = "COS 126;COS 226;COS 217", 
    	departmentHead = "Colleen Kenny"
    	)

    certificate.save()

    certs = Certificates.objects.all()

    #END NEW
    return render(request, 'index.html', {'certificates' : certs})


def db(request):

	greeting = Greeting()
	greeting.save()

	greetings = Greeting.objects.all()

	return render(request, 'db.html', {'greetings': greetings})

