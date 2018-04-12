from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpRequest
from django.http import JsonResponse
import requests 
from .models import Certificates

def login(request):
    # redirects to index for the test case
    index(request)

def index(request):
    # intialize html string
    htmlOut = ''

    # gets user specific information
    #currentStudent = Students.objects.get(netid = 'testStudent')
    
    listOfInfo = interpretedData(currentStudent)
    certsComplete = listOfInfo[0]
    coursesComplete = listOfInfo[1]
    certsAttainable = listOfInfo[2]
    coursesNeeded = listOfInfo[3]
    
    # add header to htmlOut
    studentContext = {
        'student_first' = "Test",
        'student_last' = "Student",
        'student_major' = "ENG",
        'student_degree' = "AB",
        'student_year' = "2020",
        'gen_numCertsComplete' = 2,
        'gen_numCoursesComplete' = 16,
        'gen_numCertsAttainable' = 3,
        'gen_numCoursesNeeded' = 12
    }
    htmlOut += render_to_string('header_template.html', studentContext)

    # iterate through all certificates
    certificates = Certificates.objects.all()
    for certificate in certificates:
        percentComplete = 75
        coursesComplete = 14
        certificateContext = {
            'cert_name' = certificate.title,
            'cert_description' = certificate.description,
            'cert_contactName' = certificate.contact_name,
            'cert_contactEmail' = certificate.contact_email,
            'cert_website' = certificate.link_page,
            'cert_threeLetterCode' = certificate.code,
            'drop_percentComplete' = percentComplete,
            'drop_coursesComplete' = coursesComplete
        }
        htmlOut += render_to_string('display_cert_template.html', certificateContext)

        # track1 information 
        if len(certificate.track1) > 0:
            track1 = parseTrack(str(certificate.track1))

        # track2 information 
        track2 = parseTrack(str(certificate.track2))

        # track3 information 
        track3 = parseTrack(str(certificate.track3))

        # track4 information 
        track4 = parseTrack(str(certificate.track4))

        # track5 information 
        track5 = parseTrack(str(certificate.track5))

        # track6 information 
        track6 = parseTrack(str(certificate.track6))
    
    # return html code 
    return HttpResponse(htmlOut)

# connects to interpreter for certsComplete, coursesComplete, certsAttainable, coursesNeeded
def interpretedData(student):
    # call interpreter and pull needed information
    return [5, 2, 1, 3]

# separates field of information in the track field
def parseTrack(trackSequence):
    rawInfo = trackSequence.split('*')


def testtranscript(request):
    return render(request, 'testtranscript.html')


def result(request):
    BASE_SERVICE_URL = "https://transcriptapi.tigerapps.org"
    ticket = request.GET.get("ticket")
    request_url = '{base}/transcript/?ticket={ticket}'.format(base = BASE_SERVICE_URL,
        ticket = ticket)
    r = requests.get(request_url)
    try:
        transcript = r.json()["transcript"]
    except (ValueError, KeyError):
        flash("Something went wrong! Please try again later.")
        return redirect(url_for("index"))

    # allGrades = []
    # if transcript["grades"] != '':
    #     for course,grade in transcript["grades"].items():
    #         # grade is '' if the course has not yet been taken (i.e no grade available).
    #         if course != '':
    #             allGrades.append(course)
    # else:
    #     for semester,allCourses in transcript["courses"].items():
    #         allGrades.append(semester)

    return render(request, 'testtranscriptresult.html', {'transcript': transcript})
    

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

