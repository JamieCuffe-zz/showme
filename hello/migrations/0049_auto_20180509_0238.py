# Generated by Django 2.0.4 on 2018-05-09 06:38

from django.db import migrations
import json

def populateCertificate_db(apps, schema_editor):
    Certificates = apps.get_model('hello', 'Certificates', require_ready=True)

    # opens json of certificates 
    data = json.load(open('allcertificates.json', encoding="utf8"))

    # iterates through each certificate and adds them to Certificates models
    for i in range(len(data)):
        newCertificate = Certificates()

        # immediately accessible fields
        newCertificate.title = data[i]['name']
        newCertificate.code = data[i]['code']
        newCertificate.link_page = data[i]['urls'][0]
        newCertificate.contact_name = data[i]['contacts'][0]['name']
        newCertificate.contact_email = data[i]['contacts'][0]['email']
        newCertificate.contact_title = data[i]['contacts'][0]['type']
        newCertificate.description = data[i]['description']

        # determines number of total courses needed 
        newCertificate.total_courses = findTotal(data[i])

        # fields that need to be recursively traced
        newCertificate.tracks = json.dumps(findTracks(data[i]['req_list']))

        # saves certificate to database
        newCertificate.save()

# formats tracks
def findTracks(requirements):
    returnList = []

    # iterates through list of requirements 
    for i in range(len(requirements)):
        # node with course information
        if 'course_list' in requirements[i]:
            trackInfo = {}
            trackInfo['name'] = requirements[i]['name']
            trackInfo['courses'] = []
            for course in range(len(requirements[i]['course_list'])):
                trackInfo['courses'].append(requirements[i]['course_list'][course].split(':')[0])
            returnList.append(trackInfo)

        # not a node
        elif 'req_list' in requirements[i]:
            addingToList = []
            addingToList = list(findTracks(requirements[i]['req_list']))
            if len(addingToList) > 0:
                returnList.append(addingToList)

    return returnList

# finds number of courses needed for certificate
def findTotal(certificate):
    total = 0
    for i in range(len(certificate['req_list'])):
        total += certificate['req_list'][i]['min_needed']

    return total

class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0048_auto_20180509_0200'),
    ]

    operations = [
    migrations.RunPython(populateCertificate_db)
    ]