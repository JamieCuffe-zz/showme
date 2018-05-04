from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.http import HttpRequest
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import ModelBackend
from django.core.serializers.json import DjangoJSONEncoder
import os
import re
import collections
import requests
import json
import hello.verifier
import hello.new_verifier
from .models import Students, Certificates
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
@login_required(login_url = '/accounts/login')
def userCookiesTest(request):
    if request.user.is_authenticated:
        netId = request.user.username
    return render(request, 'userCookiesTest.html', {'netid': netId})

@login_required(login_url = '/accounts/login')
def transcript_check(request):
    #return redirect("https://showme333.herokuapp.com/certificate")
    # netId = None
    if request.user.is_authenticated:
        netId = request.user.username
    #netId = "roopar"
    # check if user is in database already
    if Students.objects.filter(netid = netId).count() == 0:
        # if not, add user netid to db
        newUser = Students()
        newUser.netid = netId
        newUser.save()
        # redirect to tigerapps transcript upload
        return redirect("https://transcriptapi.tigerapps.org?redirect=https://showme333.herokuapp.com/transcript_result")
    # if user is in db already, their courses must be there already - redirect to main page
    else:
        return redirect("https://showme333.herokuapp.com/index")


def transcript_result(request):
    if request.user.is_authenticated:
        netId = request.user.username
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

    allCourses = []
    if transcript["grades"]:
        for course,grade in transcript["grades"].items():
            # grade is '' if the course has not yet been taken (i.e no grade available).
            if course != '':
                allCourses.append(course)
    elif transcript["courses"]:
        for semester,courses in transcript["courses"].items():
            for course in courses:
                allCourses.append(course)

    # update database with courses associated with netid
    user = Students.objects.get(netid=netId)
    user.coursesCompleted = json.dumps(allCourses)
    user.save()

    # redirect back to index page
    return redirect("https://showme333.herokuapp.com/index")


@login_required(login_url = '/accounts/login')
def index(request):
    if request.user.is_authenticated:
        netId = request.user.username
    # intialize html string
    #htmlOut = render_to_string('index.html')
    # gets user specific information
    # currentStudent = Students.objects.get(netid = 'testStudent')

    #certificates = Certificates.objects.all()

    # currentStudent = ""
    # listOfInfo = interpretedData(currentStudent)
    # certsComplete = listOfInfo[0]
    # coursesComplete = listOfInfo[1]
    # certsAttainable = listOfInfo[2]
    # coursesNeeded = listOfInfo[3]

    # for certificate in certificates:
    #     # add header to htmlOut
    #     studentContext = {
    #         'student_name' : certificate.title,
    #         'student_major' : certificate.contact_name,
    #         'student_degree' : "AB",
    #         'student_year' : 2020,
    #         'gen_numCertsComplete' : 1,
    #         'gen_numCoursesComplete' : 16,
    #         'gen_numCertsAttainable' : 3,
    #         'gen_numCoursesNeeded' : 12
    #     }


    # htmlOut += render_to_string('header_template.html', studentContext)

    # htmlOut += render_to_string('bottom_end_structure.html')

    # return html code
    #return HttpResponse(htmlOut)
    return render(request, 'index.html', {'user': netId})

# def my_view(request):


# returns the certificate data to be presented to the user
@login_required(login_url = '/accounts/login')
def certificate(request):
    # get all certificates for given student
    if request.method == 'GET':
        studentCourses = []
        # get course data for student and reformat
        if request.user.is_authenticated:
            netId = request.user.username
            # student = Students.objects.filter(netid = netId)
            # courses = student.values("coursesCompleted")
            # data = list(courses)[0]["coursesCompleted"]
            # studentCourses = json.loads(data)
            studentCourses = json.loads(list(Students.objects.filter(netid = netId).values("coursesCompleted"))[0]["coursesCompleted"])

        # call interpreter 
        allCerts = ["PAC", "ACM", "FIN", "GHP", "AAS"]
        allCertsCourses = []
        allCertsReqs = []
        formattedCourses = [[]]
        totalOutput = []

        
        # format courses from transcript to be passed into interpreter
        for i in range (0, len(studentCourses)):
            formattedCourses[0].append({"name" : studentCourses[i]})

        # extract courses and reqs from output of interpreter
        for i in range(0, len(allCerts)):
            allCertsCourses.append(json.loads(hello.new_verifier.main(formattedCourses, allCerts[i], 2018)[0]))
            allCertsReqs.append(json.loads(hello.new_verifier.main(formattedCourses, allCerts[i], 2018)[1]))

        # take courses from required courses in cert json and append to allCertsReqs

        for i in range(0, len(allCertsReqs)):
            testCertificate = list(Certificates.objects.filter(title = allCertsReqs[i]["name"]).values())
            if (testCertificate):
                description = testCertificate[0]["description"]
                urls = testCertificate[0]["link_page"]
                contactName = testCertificate[0]["contact_name"]
                contactEmail = testCertificate[0]["contact_email"]
                allCertsReqs[i]["description"] = description
                allCertsReqs[i]["urls"] = urls
                allCertsReqs[i]["contacts"] = {"name" : contactName, "email" : contactEmail}
                
                reqList = json.loads(testCertificate[0]["tracks"])
                for j in range(0, len(reqList)):
                    courseList = reqList[j]["courses"]
                    courseListNew = []
                    for k in range(0, len(courseList)):
                        matchCourseList = allCertsCourses[0][0]
                        successOrFail = "info"
                        for l in range(0, len(matchCourseList)):
                            regexString = courseList[k].replace("*", "[0-9]")
                            if (re.search(regexString, matchCourseList[l]["name"])) and (matchCourseList[l]["used"]):
                                successOrFail = "success"
                        courseListNew.append({"title" : courseList[k], "satisfied" : successOrFail})
                    allCertsReqs[i]["req_list"][j]["course_list"] = courseListNew

                totalOutput.append(allCertsReqs[i])

        orderedCourses={}

        for course in studentCourses:
            seen = False
            for key in orderedCourses:
                if course[0:3] == key:
                    orderedCourses[key] += 1
                    seen = True
            if seen == False:
                orderedCourses[course[0:3]] = 1

        # orderedCourses = sorted(orderedCourses, key=lambda k: list(k.values())[0])
        orderedCourses = sorted(orderedCourses,key=orderedCourses.get, reverse=True)

        topThree = []

        if len(orderedCourses) >= 3:
            topThree = orderedCourses[:3]
        else:
            topThree = orderedCourses


        test = []

        for i in range(0,len(totalOutput)):
            for j in range(0, len(totalOutput[i]["req_list"])):
                newCourseList = []
                for l in range(0, len(topThree)):
                    for k in range(0, len(totalOutput[i]["req_list"][j]["course_list"])):
                        test = topThree[l]
                #         if topThree[l] == totalOutput[i]["req_list"][j]["course_list"][k]["title"][0:3]:
                #             newCourseList.append(totalOutput[i]["req_list"][j]["course_list"][k])
                #             del totalOutput[i]["req_list"][j]["course_list"][k]
                #     for m in range(0, len(totalOutput[i]["req_list"][j]["course_list"])):
                #         newCourseList.append(totalOutput[i]["req_list"][j]["course_list"][m])
                # totalOutput[i]["req_list"][j]["course_list"] =newCourseList




        # orders courses
        # for i in range(0, len(totalOutput)):
        #     totalOutput[i]['percentage'] = round((totalOutput[i]['count']/totalOutput[i]["min_needed"]) * 100)

        # # orders by percent complete
        # totalOutput.sort(key = lambda item:item['percentage'], reverse = True)
        return JsonResponse(test, safe=False)

    # POST request - puts student netid and course basket into db

def student_coursebasket(request):
    if request.method == 'POST':
        netID = request.path.split('/')[:-2]
        students = Students.objects.all()
        courses = request.body
        student = Students(netid=netID, coursebasket=courses)
        student.save()

# connects to interpreter for certsComplete, coursesComplete, certsAttainable, coursesNeeded
@login_required(login_url = '/accounts/login')
def interpretedData(student):
    # call interpreter and pull needed information
    return [5, 2, 1, 3]

# separates field of information in the track field
@login_required(login_url = '/accounts/login')
def parseTrack(trackSequence):
    rawInfo = trackSequence.split('*')
    courses = str(rawInfo[:-1]).split('%')
    rawInfo[:-1] = courses

    return rawInfo

@login_required(login_url = '/accounts/login')
def getrequest(request):
    return render(request,'getCertificateRequest.html')

@login_required(login_url = '/accounts/login')
def testtranscript(request):
    return render(request, 'testtranscript.html')

@login_required(login_url = '/accounts/login')
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

    allCourses = []
    if transcript["grades"]:
        for course,grade in transcript["grades"].items():
            # grade is '' if the course has not yet been taken (i.e no grade available).
            if course != '':
                allCourses.append(course)
    elif transcript["courses"]:
        for semester,courses in transcript["courses"].items():
            for course in courses:
                allCourses.append(course)
        #return render(request, 'testtranscriptresult.html', {'transcript': transcript})
        #for semester,courses in transcript["courses"].items():

    #return redirect("https://showme333.herokuapp.com/index")
    return render(request, 'testtranscriptresult.html', {'transcript': allCourses})


    # return render(request, 'testtranscriptresult.html', {'transcript': transcript})

@login_required(login_url = '/accounts/login')
def metainfo(request):
    # get all certificates for given student
    if request.method == 'GET':
        studentCourses = []
        # get course data for student and reformat
        if request.user.is_authenticated:
            netId = request.user.username
            # student = Students.objects.filter(netid = netId)
            # courses = student.values("coursesCompleted")
            # data = list(courses)[0]["coursesCompleted"]
            # studentCourses = json.loads(data)
            studentCourses = json.loads(list(Students.objects.filter(netid = netId).values("coursesCompleted"))[0]["coursesCompleted"])

        # call interpreter 
        allCerts = ["PAC", "ACM", "FIN", "GHP", "AAS"]
        allCertsCourses = []
        allCertsReqs = []
        formattedCourses = [[]]
        totalOutput = []

        
        # format courses from transcript to be passed into interpreter
        for i in range (0, len(studentCourses)):
            formattedCourses[0].append({"name" : studentCourses[i]})

        # extract courses and reqs from output of interpreter
        for i in range(0, len(allCerts)):
            allCertsCourses.append(json.loads(hello.verifier.main(formattedCourses, allCerts[i], 2018)[0]))
            allCertsReqs.append(json.loads(hello.verifier.main(formattedCourses, allCerts[i], 2018)[1]))

        # take courses from required courses in cert json and append to allCertsReqs

        for i in range(0, len(allCertsReqs)):
            testCertificate = list(Certificates.objects.filter(title = allCertsReqs[i]["name"]).values())
            if (testCertificate):
                description = testCertificate[0]["description"]
                urls = testCertificate[0]["link_page"]
                contactName = testCertificate[0]["contact_name"]
                contactEmail = testCertificate[0]["contact_email"]
                allCertsReqs[i]["description"] = description
                allCertsReqs[i]["urls"] = urls
                allCertsReqs[i]["contacts"] = {"name" : contactName, "email" : contactEmail}
                
                reqList = json.loads(testCertificate[0]["tracks"])
                for j in range(0, len(reqList)):
                    courseList = reqList[j]["courses"]
                    courseListNew = []
                    for k in range(0, len(courseList)):
                        matchCourseList = allCertsCourses[0][0]
                        successOrFail = "info"
                        for l in range(0, len(matchCourseList)):
                            regexString = courseList[k].replace("*", "[0-9]")
                            if (re.search(regexString, matchCourseList[l]["name"])) and (matchCourseList[l]["used"]):
                                successOrFail = "success"
                        courseListNew.append({"title" : courseList[k], "satisfied" : successOrFail})
                    allCertsReqs[i]["req_list"][j]["course_list"] = courseListNew

                totalOutput.append(allCertsReqs[i])

        completeCert = 0
        attainable = 0
        neededCourses = 0
        # iterate through output courses to populate meta data
        for i in range(0, len(totalOutput)):
            if totalOutput[i]["satisfied"] == True:
                completeCert += 1
            else:
                # calculates if the certificate is attainable 
                if totalOutput[i]["count"]/totalOutput[i]["min_needed"] >= 0.75:
                    attainable += 1
                    neededCourses += totalOutput[i]["min_needed"] - totalOutput[i]["count"]
        
        numTaken = 0
        for i in range(0, len(formattedCourses)):
            for j in range(0, len(formattedCourses[i])):
                numTaken += 1

        metaList = [completeCert, numTaken, attainable, neededCourses]
        return JsonResponse(metaList, safe = False)