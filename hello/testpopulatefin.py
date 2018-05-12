import json

def populateCertificate_db():

    newCertificate = {}
    # opens json of certificates 
    data = json.load(open('Certificates/FIN_2018.json', encoding="utf8"))

    # iterates through each certificate and adds them to Certificates models
    newCertificate["tracks"] = json.dumps(findTracks(data['req_list']))

    print(newCertificate["tracks"])

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
            #print(addingToList)
            if len(addingToList) > 0:
                returnList.append(addingToList)

    return returnList


populateCertificate_db()


