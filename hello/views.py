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
import ast
import re
import collections
import requests
import json
import hello.verifier
import hello.new_verifier
from .models import Students,Certificates,Metadata
from django.views.decorators.csrf import csrf_exempt
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
        # newUser = Students()
        # newUser.netid = netId
        # newUser.save()
        # redirect to tigerapps transcript upload
        return redirect("https://showme333.herokuapp.com/about")
        #return redirect("https://transcriptapi.tigerapps.org?redirect=https://showme333.herokuapp.com/transcript_result")
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
        return redirect("https://showme333.herokuapp.com/about")

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

    # if student doesn't exist in db, just add their netid
    if Students.objects.filter(netid = netId).count() == 0:
        # if not, add user netid to db
        newUser = Students()
        newUser.netid = netId
        newUser.save()

    # save courses associated with netid into db
    user = Students.objects.get(netid=netId)
    user.coursesCompleted = json.dumps(allCourses)
    user.save()

    # redirect back to index page
    return redirect("https://showme333.herokuapp.com/index")


@login_required(login_url = '/accounts/login')
def index(request):
    if request.user.is_authenticated:
        netId = request.user.username

    #user tries to bypass intended flow without courses uploaded, redirect to transcript upload page
    if Students.objects.filter(netid = netId).count() == 0:
        return redirect("https://transcriptapi.tigerapps.org?redirect=https://showme333.herokuapp.com/transcript_result")
    else:
        return render(request, 'index.html', {'user': netId})

@login_required(login_url = '/accounts/login')
def about(request):
    if request.user.is_authenticated:
        netId = request.user.username
    return render(request, 'about.html', {'user': netId})

@login_required(login_url = '/accounts/login')
def data(request):
    if request.user.is_authenticated:
        netId = request.user.username
    return render(request, 'data.html', {'user': netId})

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
            # basket = []
            # ogbasket = list(Students.objects.filter(netid = netId).values())[0]["courseBasket"]
            # ogbasket = ogbasket[1:len(ogbasket) - 1]
            # courses = ogbasket.split(', ')
            # for i in range(0, len(courses)):
            #     stupid = courses[i].split('*')[0]
            #     studentCourses.append(stupid[1:len(stupid) -1])
            #     basket.append(stupid[1:len(stupid) -1])
            # for i in range(0, len(ogbasket)):
            #     output = ogbasket[i].split('*')
            #     courseid = output[0]
            #     studentCourses.append(courseid)



        # call interpreter
        allCerts = ["AAS", "AMS", "CWR", "EMS", "ENT", "FIN", "GHP", "GSS", "LAS", "LIN", "NEU", "PAC", "PEB", "SML", "SPA", "THR", "URB", "VPL"]
        allCertsCourses = []
        allCertsReqs = []
        formattedCourses = [[]]
        totalOutput = []

        allReturned = []

        count = 0

        allMetadata = Metadata.objects.all()

        copy = []

        # format courses from transcript to be passed into interpreter
        for i in range (0, len(studentCourses)):
            formattedCourses[0].append({"name" : studentCourses[i]})

        # extract courses and reqs from output of interpreter
        for i in range(0, len(allCerts)):
            allCertsCourses.append(json.loads(hello.new_verifier.main(formattedCourses, allCerts[i], 2018)[0]))
            allCertsReqs.append(json.loads(hello.new_verifier.main(formattedCourses, allCerts[i], 2018)[1]))

        copy.append(allCertsCourses)
        # take courses from required courses in cert json and append to allCertsReqs
        for i in range(0, len(allCertsReqs)):
            testCertificate = list(Certificates.objects.filter(title = allCertsReqs[i]["name"]).values())
            allReturned.append(testCertificate)
            if (testCertificate):
                trend = list(Metadata.objects.filter(code=testCertificate[0]["code"]).values())[0]["trend"]
                number_of_students = list(Metadata.objects.filter(code=testCertificate[0]["code"]).values())[0]["number_of_students"]
                description = testCertificate[0]["description"]
                urls = testCertificate[0]["link_page"]
                contactName = testCertificate[0]["contact_name"]
                contactEmail = testCertificate[0]["contact_email"]
                allCertsReqs[i]["description"] = description
                allCertsReqs[i]["urls"] = urls
                allCertsReqs[i]["contacts"] = {"name" : contactName, "email" : contactEmail}
                allCertsReqs[i]["number_of_students"] = number_of_students
                if trend == 0:
                    allCertsReqs[i]["trend"] = ""
                elif trend == 1:
                    allCertsReqs[i]["trend"] = '<i style= "color: #00c1eb" class="fa fa-line-chart" data-toggle="tooltip" data-placement="top" title="Trending: The number of students taking this certificate has increased over the past 4 years."></i>'

                reqList = json.loads(testCertificate[0]["tracks"])
                for j in range(0, len(reqList)):
                    courseList = reqList[j]["courses"]
                    courseListNew = []
                    for k in range(0, len(courseList)):
                        matchCourseList = allCertsCourses[i][0]
                        successOrFail = "info"
                        for l in range(0, len(matchCourseList)):
                            regexString = courseList[k].replace("*", "[0-9]")
                            if (matchCourseList[l]["used"]):
                                count += 1
                            if (re.search(regexString, matchCourseList[l]["name"])) and (matchCourseList[l]["used"]):
                                successOrFail = "success"
                                # if (matchCourseList[l]["name"]) in basket:
                                #     successOrFail = "warning"
                                # else:
                                #     successOrFail = "success"
                        courseListNew.append({"title" : courseList[k], "satisfied" : successOrFail})

                    allCertsReqs[i]["req_list"][j]["course_list"] = courseListNew

                totalOutput.append(allCertsReqs[i])


        # order list of courses by relevance to student

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



        for i in range(0,len(totalOutput)):
            for j in range(0, len(totalOutput[i]["req_list"])):
                newCourseList = []
                for l in range(0, len(topThree)):
                    for k in range(0, len(totalOutput[i]["req_list"][j]["course_list"])):
                        if topThree[l] == totalOutput[i]["req_list"][j]["course_list"][k]["title"][0:3]:
                            newCourseList.append(totalOutput[i]["req_list"][j]["course_list"][k])
                            #del totalOutput[i]["req_list"][j]["course_list"][k]
                for m in range(0, len(totalOutput[i]["req_list"][j]["course_list"])):
                    seen = False
                    for n in range(0, len(newCourseList)):
                        if (newCourseList[n]["title"] == totalOutput[i]["req_list"][j]["course_list"][m]["title"]):
                            seen = True
                    if (seen == False):
                        newCourseList.append(totalOutput[i]["req_list"][j]["course_list"][m])
                # totalOutput[i]["req_list"][j]["course_list"] =newCourseList
                newCourseListTwo = []
                for o in range(0, len(newCourseList)):
                    if(newCourseList[o]["satisfied"] == "success"):
                        newCourseListTwo.append(newCourseList[o])
                for p in range(0, len(newCourseList)):
                    seenTwo = False
                    for q in range(0, len(newCourseListTwo)):
                        if (newCourseList[p]["title"] == newCourseListTwo[q]["title"]):
                            seenTwo = True
                    if (seenTwo == False):
                        newCourseListTwo.append(newCourseList[p])
                totalOutput[i]["req_list"][j]["course_list"] =newCourseListTwo

        # adds format for each track for visual
        for i in range(0, len(totalOutput)):
            colors = ["info", "danger", "success", "warning", "primary"]
            for j in range(0, len(totalOutput[i]["req_list"])):
                textColor = "#ffffff"
                percentage = 0
                if totalOutput[i]["req_list"][j]["min_needed"] != 0:
                    percentage = totalOutput[i]["req_list"][j]["count"]/totalOutput[i]["req_list"][j]["min_needed"] * 100
                if percentage > 100:
                    percentage = 100
                if percentage == 0:
                    textColor = "#f4f3f4"
                totalOutput[i]["req_list"][j]["barGraph"] = [colors[j%5], totalOutput[i]["req_list"][j]["count"], totalOutput[i]["req_list"][j]["min_needed"], percentage, textColor]

        # orders certificates
        for i in range(0, len(totalOutput)):
            minRequired = 0
            amountTaken = 0
            for j in range(0, len(totalOutput[i]["req_list"])):
                minRequired += totalOutput[i]["req_list"][j]["min_needed"]
                amountTaken += totalOutput[i]["req_list"][j]["count"]

            totalOutput[i]["count"] = amountTaken
            totalOutput[i]["min_needed"] = minRequired

            if totalOutput[i]["min_needed"] == 0:
                totalOutput[i]["percentage"] = 0
            elif totalOutput[i]["min_needed"] > 0 and (totalOutput[i]["count"]/totalOutput[i]["min_needed"] * 100) < 100:
                totalOutput[i]["percentage"] = int(round(totalOutput[i]["count"]/totalOutput[i]["min_needed"] * 100))
            else:
                totalOutput[i]["percentage"] = 100

        # orders by percent complete
        totalOutput.sort(key = lambda item:item['percentage'], reverse = True)
        return JsonResponse(totalOutput, safe=False)

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
        allCerts = ["AAS", "AMS", "CWR", "EMS", "ENT", "FIN", "GHP", "GSS", "LAS", "LIN", "NEU", "PAC", "PEB", "SML", "SPA", "THR", "URB", "VPL"]
        allCertsCourses = []
        allCertsReqs = []
        formattedCourses = [[]]
        totalOutput = []


        # format courses from transcript to be passed into interpreter
        for i in range (0, len(studentCourses)):
            formattedCourses[0].append({"name" : studentCourses[i]})

        '''
        basket = json.loads(Students.objects.get(netid=netId).courseBasket)
        for i in range(0, len(basket)):
            formattedCourses[0].append({"name" : basket[i]})
        '''

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

                        '''
                        # updates color for courses from queue
                        for t in range(0, len(courseListNew)):
                            if courseListNew[t]["title] in basket:
                                courseListNew[t]["satisfied"] = "warning"
                        '''

                    allCertsReqs[i]["req_list"][j]["course_list"] = courseListNew

                totalOutput.append(allCertsReqs[i])

        for i in range(0, len(totalOutput)):
            minRequired = 0
            amountTaken = 0
            for j in range(0, len(totalOutput[i]["req_list"])):
                minRequired += totalOutput[i]["req_list"][j]["min_needed"]
                amountTaken += totalOutput[i]["req_list"][j]["count"]

            totalOutput[i]["count"] = amountTaken
            totalOutput[i]["min_needed"] = minRequired

        completeCert = 0
        attainable = 0
        neededCourses = 0
        # iterate through output courses to populate meta data
        for i in range(0, len(totalOutput)):
            if totalOutput[i]["satisfied"] == True:
                completeCert += 1
            else:
                # calculates if the certificate is attainable
                if totalOutput[i]["count"]/totalOutput[i]["min_needed"] >= 0.60:
                    attainable += 1
                    neededCourses += totalOutput[i]["min_needed"] - totalOutput[i]["count"]

        numTaken = 0
        for i in range(0, len(formattedCourses)):
            for j in range(0, len(formattedCourses[i])):
                numTaken += 1

        metaList = [completeCert, numTaken, attainable, neededCourses]
    return JsonResponse(metaList, safe = False)

@csrf_exempt
@login_required(login_url = '/accounts/login')
def delete(request):
    # if request.method == 'POST':
    #     returnTest = ""
    #     if request.user.is_authenticated:
    #         netId = request.user.username

    #     if Students.objects.filter(netid = netId).count() != 0:
    #         user = Students.objects.get(netid=netId)
    #         user.courseBasket = ""
    #         returnTest = user.courseBasket
    #         user.save()

    return JsonResponse(["Complete"], safe = False)

@csrf_exempt
@login_required(login_url = '/accounts/login')
def save(request):
    # if request.method == 'POST':
    #     returnTest = ""
    #     if request.user.is_authenticated:
    #         netId = request.user.username

    #     if Students.objects.filter(netid = netId).count() != 0:
    #         user = Students.objects.get(netid=netId)
    #         user.courseBasket = json.loads(request.body)
    #         returnTest = user.courseBasket
    #         user.save()

    return JsonResponse(["Complete"], safe = False)

@login_required(login_url = '/accounts/login')
def queue(request):
    # get course queue for student
    # if request.method == 'GET':
    #     returnQueue = []
    #     if request.user.is_authenticated:
    #         netId = request.user.username

    #     if Students.objects.filter(netid = netId).count() != 0:
    #         user = Students.objects.get(netid=netId)
    #         returnQueue = json.dumps(user.courseBasket)

    return JsonResponse(["Complete"], safe = False)
