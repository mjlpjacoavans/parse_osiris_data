from flatten_json import flatten
from pprint import pprint
import pandas as pd
import json, csv


"""
This repo has been stripped from the actual requested files to protect my privacy (also data won't be up to data)
Before being able to anything useful at all with this data the data should be aquired. 
The workflow followed was as follows: (TODO: Be more detailed)

1. Intercept all courses with burpsuite.
2. Export the bodies in bulk
3. Parse the data to only get the json body with cyberchef
4. Merge the seperate bodies into a single list with this script
5. Extract the result keys with this script
6. Request statistics for keys with burp intruder
7. Export all request data and extract bodies with cybershef
8. Match statistics data with course data in this script
9. Clean up
10. Export to a flat csv file
"""


courses = []

# Load courses file (pre-parsed from burp)
js = open("osiris-cleaned-data.json","r").read().split("HTTP/2 200 OK") 


# Merge all items into single json list
for j in js:
    j = json.loads(j)
    try:items = j["items"]
    except KeyError:
        continue
    courses.extend(items)


# Use results to get the id_resultaat ids which are needed for getting result statistics
# for j in courses:
#     print(j["id_resultaat"])


# Load course results data
result_statistics_file = open("osiris-analyse-data-course-results-parsed.json","r").read().split("|||")
# print(len(result_statistics_file))

# Merge all items into single json list
for j in result_statistics_file:
    if j:
        j = json.loads(j)
        if not "failure" in j.keys():
            id_resultaat = j["id_resultaat"]
            
            # Lookup if the currrent statistic belongs to a course
            for course in courses:
                if course["id_resultaat"] == id_resultaat:
                    course["course_results_statistics"] = j



# Flatten and only get courses with statistics added
dict_flattened = [flatten(d) for d in courses if "course_results_statistics" in d.keys()]



# Make the keys numeric
for course in dict_flattened:
    for key, value in course.items():
        # if key == "course_results_statistics_aantal_deelnemers":
        #     print(key, value)
        #     course[key] = value.replace("scto:","")

        if key == "id_cursus":
            course[key] = value.replace("curs:","")

        if key == "id_geldend_resultaat":
            course[key] = value.replace("sgre:","")

        if key == "id_resultaat":
            course[key] = value.replace("scto:","")

        if key == "course_results_statistics_id_resultaat":
            course[key] = value.replace("scto:","")


# Calculate percentages passeds
for course in dict_flattened:
    participants = course["course_results_statistics_aantal_deelnemers"]
    passeds = course["course_results_statistics_aantal_voldoendes"]
    ratio = (passeds/participants) * 100
    course["passeds_ratio"] = ratio



print(len(dict_flattened))


# Save everything to disk
outj = json.dumps(dict_flattened, sort_keys=True, indent=4)
f = open("osiris-data-combined.json","w")
f.write(outj)


df = pd.read_json("osiris-data-combined.json")

df.to_csv("osiris-data-combined.csv", index=False)

