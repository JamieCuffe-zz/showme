import test_verifier
import json
def main():

    allCerts = ["PAC", "ACM", "FIN", "GHP", "AAS"]
    allCertsCourses = []
    allCertsReqs = []
    formattedCourses = [[{"name" : "COS 126"}, {"name" : "COS 226"}, {"name" : "COS 217"}]]
    totalOutput = []

    allReturned = []

    returned = json.loads(test_verifier.main(formattedCourses))

    print(returned)

    # extract courses and reqs from output of interpreter
    # allCertsCourses.append(json.loads(test_verifier.main(formattedCourses, allCerts[i])[0]))
    # allCertsReqs.append(json.loads(test_verifier.main(formattedCourses, allCerts[i], 2018)[1]))

    # print(allCertsReqs)
    # print("\n")
    # print(allCertsCourses)

main()