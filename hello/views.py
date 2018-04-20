from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpRequest
from django.http import JsonResponse
from django.template.loader import render_to_string
import requests
import json
from .models import Certificates

# def login(request):
    # CAS login
    # redirect_url = "https://fed.princeton.edu/cas/login"

    # if "ticket" in request.args:  # This means CAS has redirected back to us
    #     session["CAS_TOKEN"] = request.args["ticket"]

    # if "CAS_TOKEN" in session:  # There is a token already, but we might not trust
    #     if validate(session["CAS_TOKEN"]):  # ensure token validity
    #         if 'CAS_AFTER_LOGIN_SESSION_URL' in session:
    #             redirect_url = session.pop('CAS_AFTER_LOGIN_SESSION_URL')
    #         else:
    #             redirect_url = "/"
    #     else:
    #         del session["CAS_TOKEN"]
    # return redirect(redirect_url)

def index(request):
    # intialize html string
    htmlOut = render_to_string('index.html')
    # gets user specific information
    # currentStudent = Students.objects.get(netid = 'testStudent')

    certificates = Certificates.objects.all()

    currentStudent = ""
    listOfInfo = interpretedData(currentStudent)
    certsComplete = listOfInfo[0]
    coursesComplete = listOfInfo[1]
    certsAttainable = listOfInfo[2]
    coursesNeeded = listOfInfo[3]

    for certificate in certificates:
        # add header to htmlOut
        studentContext = {
            'student_name' : certificate.title,
            'student_major' : certificate.contact_name,
            'student_degree' : "AB",
            'student_year' : 2020,
            'gen_numCertsComplete' : 1,
            'gen_numCoursesComplete' : 16,
            'gen_numCertsAttainable' : 3,
            'gen_numCoursesNeeded' : 12
        }


    # htmlOut += render_to_string('header_template.html', studentContext)

    # htmlOut += render_to_string('bottom_end_structure.html')

    # return html code
    return HttpResponse(htmlOut)

# returns the certificate data to be presented to the user
def certificate(request):
    # get all certificates for given student
    if request.method == 'GET':
	    netID = request.path.split('/')[:-2]

	    # gets object for student representation
	    #student = Students.objects.get(name = netID)
	    certificates = Certificates.objects.all()
        data = {}
        for certificate in certificates:
            data["title"] = certificate.title
            data["contact name"] = certicate.contact_name
	    # insert parser that returns completed certificates
	    # courses completed by the student
	    # for certificate in certicates:
	        # completionFunction(student.netID, certificate, student.year, student.coursesCompleted)
	        # if true, student.completedCertificates += '.' + certificate
	        # else
	            # add to outputted certificates
	            # update track satisfied
	            # for each updated track:
	                # add counted courses

	    # format the certificates from favorited/completion to low
	    # order favorited first
	    # order by completion percentage

	    # return certificate information
	    data = {
	    "name" : "value"
	    }
	    return JsonResponse(data)


# connects to interpreter for certsComplete, coursesComplete, certsAttainable, coursesNeeded
def interpretedData(student):
    # call interpreter and pull needed information
    return [5, 2, 1, 3]

# separates field of information in the track field
def parseTrack(trackSequence):
    rawInfo = trackSequence.split('*')
    courses = str(rawInfo[:-1]).split('%')
    rawInfo[:-1] = courses

    return rawInfo

def getrequest(request):
    return render(request,'getCertificateRequest.html')

# def testtranscript(request):
#     return render(request, 'testtranscript.html')


# def result(request):
#     BASE_SERVICE_URL = "https://transcriptapi.tigerapps.org"
#     ticket = request.GET.get("ticket")
#     request_url = '{base}/transcript/?ticket={ticket}'.format(base = BASE_SERVICE_URL,
#         ticket = ticket)
#     r = requests.get(request_url)
#     try:
#         transcript = r.json()["transcript"]
#     except (ValueError, KeyError):
#         flash("Something went wrong! Please try again later.")
#         return redirect(url_for("index"))

#     # allGrades = []
#     # if transcript["grades"] != '':
#     #     for course,grade in transcript["grades"].items():
#     #         # grade is '' if the course has not yet been taken (i.e no grade available).
#     #         if course != '':
#     #             allGrades.append(course)
#     # else:
#     #     for semester,allCourses in transcript["courses"].items():
#     #         allGrades.append(semester)

#     return render(request, 'testtranscriptresult.html', {'transcript': transcript})


#OLD

# Create your views here.
# def index(request):
#     # return HttpResponse('Hello from Python!')
#     c = Certs()
#     c.save()
#     certificates = Certs.objects.all()
#     if not certificates:
#     	return render(request, 'nodata.html')
#     else:
#     	return render(request, 'index.html', {'certificates': certificates})


# def db(request):

# 	greeting = Greeting()
# 	greeting.save()

# 	greetings = Greeting.objects.all()

# 	return render(request, 'db.html', {'greetings': greetings})

# def testjson(request):
#     responseData = {
#     'id' : 4,
#     'name' : 'Test Response',
#     'roles' : ['Admin', 'User']
#     }
#     return JsonResponse(responseData)
