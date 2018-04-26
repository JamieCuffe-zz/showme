#!/usr/bin/env python
import json
from pprint import pprint
# import jsonschema # must be installed via pip
import os
import collections

# schema_location = "schema.json" # path to the requirements JSON schema
majors_location = "hello/Certificates/" # path to folder conatining the major requirements JSONs
# certificates_location = "../certificates/" # path to folder conatining the certificate requirements JSONs
# AB_requirements_location = "../degrees/AB_2018.json" # path to the AB requirements JSON
# BSE_requirements_location = "../degrees/BSE_2018.json" # path to the BSE requirements JSON

# def check_major(major_name, courses, year=2018, user_info=None):
#     """
#     Returns information about the major requirements satisfied by the courses
#     given in courses.
    
#     ## Parameter descriptions not updated yet...
#     :param major_name: the name of the major
#     :param courses: a list of course-listings
#     :param year: the year for which to pull the requirements
#     :param user_info: supplementary information about the user
#     :type major_name: string
#     :type courses: 1D array, 2D array
#     :type year: int
#     :type user_info: dict
#     :returns: Whether the major requirements are satisfied
#     :returns: The list of courses with info about the requirements they satisfy
#     :returns: A simplified json with info about how much of each requirement is satisfied
#     :rtype: (bool, dict, dict)
#     """
#     major_filename = major_name + "_" + str(year)  + ".json"
#     major_filepath = os.path.join(majors_location, major_filename)
#     major = {}
#     with open(major_filepath, 'r') as f:
#         major = json.load(f)
#     # with open(schema_location, 'r') as s:
#     #     schema = json.load(s)
#     # validate(major,schema)
#     _init_counts(major)
#     _init_min_ALL(major)
#     _init_path_to(major)
#     courses = _process_courses(courses)
#     _update_paths(major, courses)
#     courses = _format_output_courses(courses)
#     formatted_major = _format_output(major)
#     return formatted_major["satisfied"], courses, formatted_major

def check_certificate(major_name, courses, year=2018, user_info=None):
    """
    Returns information about the major requirements satisfied by the courses
    given in courses.
    
    ## Parameter descriptions not updated yet...
    :param major_name: the name of the major
    :param courses: a list of course-listings
    :param year: the year for which to pull the requirements
    :param user_info: supplementary information about the user
    :type major_name: string
    :type courses: 1D array, 2D array
    :type year: int
    :type user_info: dict
    :returns: Whether the major requirements are satisfied
    :returns: The list of courses with info about the requirements they satisfy
    :returns: A simplified json with info about how much of each requirement is satisfied
    :rtype: (bool, dict, dict)
    """
    major_filename = major_name + "_" + str(year)  + ".json"
    major_filepath = os.path.join(majors_location, major_filename)
    major = {}
    with open(major_filepath, 'r') as f:
        major = json.load(f)
    # with open(schema_location, 'r') as s:
    #     schema = json.load(s)
    # validate(major,schema)
    _init_counts(major)
    _init_min_ALL(major)
    _init_path_to(major)
    courses = _process_courses(courses)
    _update_paths(major, courses)
    courses = _format_output_courses(courses)
    formatted_major = _format_output(major)
    return formatted_major["satisfied"], courses, formatted_major


def validate(data,schema):
    """
    Validates the JSON stored in data based on the JSON schema stored in schema
    
    :param data: the requirements JSON to be validated
    :param schema: the JSON schema
    :type data: dict (representing a requirements JSON)
    :type schema: dict (representing a JSON schema)
    :returns: true if the data conforms to the JSON schema specified
    :rtype: bool
    """
    try:
        jsonschema.validate(data,schema)
        return True
    except():
        return False

def _format_output(major):
    output = collections.OrderedDict()
    if ("name" not in major) or (major["name"] == '') or (major["name"] == None):
        return None
    # for key in major:
    #     if key != "course_list" and key != "req_list":
    #         output[key] = major[key]
    output["name"] = major["name"]
    output["path_to"] = major["path_to"]
    output["satisfied"] = (major["min_needed"]-major["count"] <= 0)
    for key in ["count", "min_needed", "max_counted"]:
        output[key] = major[key]
    if "req_list" in major: # internal node. recursively call on children
        req_list = []
        for req in major["req_list"]:
            child = _format_output(req)
            if (child != None):
                req_list.append(_format_output(req))
        if req_list:
            output["req_list"] = req_list
    # elif "course_list" in major:
    #     output["course_list"] = ["..."]
    #     # for course in major["course_list"]:
    #     #     print(course)
    return output

def _process_courses(courses):
    courses = [[course_object["name"] for course_object in semester] for semester in courses]
    courses = [[{
        "name": c.split(':')[0],
        "used": False,
        "reqs_satisfied": []
    } for c in sem] for sem in courses]
    return courses
    
def _format_output_courses(courses):
    return courses

def _json_format(obj):
   return json.dumps(obj, sort_keys=False, indent=2, separators=(',', ': ')) + "\n"

def _init_counts(major):
    """
    Initializes all the counts to zero and ensures that min_needed and 
    max_counted exist.
    """
    major["count"] = 0
    if "min_needed" not in major:
        if "type" in major: # check for root
            major["min_needed"] = "ALL"
        else:
            major["min_needed"] = 0
    if major["min_needed"] == None:
        major["min_needed"] = 0
    if "max_counted" not in major:
        major["max_counted"] = None
    if "req_list" in major:
        num_subreqs = 0
        for req in major["req_list"]:
            num_subreqs += 1
            _init_counts(req)
    return major

def _init_min_ALL(major):
    """
    Replaces every instance of min_needed="ALL" with the actual number.
    """
    num_counted_from_below = 0
    if "req_list" in major:
        for req in major["req_list"]:
            num_counted_from_below += _init_min_ALL(req)
    elif "course_list" in major: # written as loop in case other actions neeed later
        for _ in major["course_list"]: 
            num_counted_from_below += 1
    if major["min_needed"] == "ALL":
        major["min_needed"] = num_counted_from_below
    if major["max_counted"] == None:
        return num_counted_from_below
    else:
        return min(major["max_counted"], num_counted_from_below)

def _update_paths(major, courses):
    """
    Finds augmenting paths from leaves to the root, and updates those paths. 
    """
    old_deficit = major["min_needed"] - major["count"]
    if (major["max_counted"] != None):
        old_available = major["max_counted"] - major["count"]
        if old_available <= 0: # already saturated, nothing to update
            return 0
    was_satisfied = (old_deficit <= 0)
    newly_satisfied = 0
    if "req_list" in major: # recursively check subrequirements
        for req in major["req_list"]:
            newly_satisfied += _update_paths(req, courses)
    elif "course_list" in major:
        newly_satisfied = _mark_courses(major["path_to"],major["course_list"],courses)
    major["count"] += newly_satisfied
    new_deficit = major["min_needed"] - major["count"]
    # new_available = major["max_counted"] - major["count"]
    if (not was_satisfied) and (new_deficit <= 0): # this req just became satisfied
        if major["max_counted"] == None: # unlimited
            return major["count"]
        else:
            return min(major["max_counted"],major["count"]) # cut off at max
    elif (was_satisfied) and (new_deficit <= 0): # this requirement was already satisfied, but added more
        if major["max_counted"] == None: # unlimited
            return newly_satisfied
        else:
            return min(old_available,newly_satisfied) # cut off at old_available
    else: # requirement still not satisfied
        return 0

def _init_path_to(major, path_to_parent = None):
    separator = '//'
    if path_to_parent == None:
        major["path_to"] = str(major["name"])
    else:
        major["path_to"] = str(path_to_parent) + separator + str(major["name"])
    if "req_list" in major:
        for req in major["req_list"]:
           _init_path_to(req, major["path_to"])

def _mark_courses(path_to, course_list, courses):
    num_marked = 0
    for sem in courses:
        for c in sem:
            if path_to in c["reqs_satisfied"]: # already used
                continue
            for pattern in course_list:
                if _course_match(c["name"], pattern):
                    num_marked += 1
                    c["reqs_satisfied"].append(path_to)
                    c["used"] = True
                    break
    return num_marked

def _course_match(course_name, pattern):
    pattern = pattern.split(':')[0]
    pattern = pattern.split('/')
    pattern = ["".join(p.split()).upper() for p in pattern]
    listings = course_name.split('/')
    listings = ["".join(l.split()).upper() for l in listings]
    for code in listings:
        if code in pattern:
            return True
        if pattern[0][4] == '*':
            if pattern[0][:4] == code[:4]:
                return True
        elif pattern[0][5] == '*':
            if pattern[0][:5] == code[:5]:
                return True

    return False

def main(courses, major_name, year):
    #with open ("verifier_tests/1.test", "r") as f:
        #major_name = f.readline()[:-1]
        #year = int(f.readline())
        #courses = json.loads(f.read())
    satisfied,courses,major = check_certificate(major_name,courses)
    totalOutput = []
    totalOutput.append(_json_format(courses))
    totalOutput.append(_json_format(major))
    # print(_json_format(courses)),
    # print("\n"),
    # print(_json_format(major)),
    # for entry in totalOutput:
    #     print(entry)

    
    return totalOutput

# if __name__ == "__main__":
#     main("PAC", 2018)