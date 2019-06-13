import csv
import json
import sys
import os

def setValue(value, field, it):
    if isinstance(value, dict) or isinstance(value, list) and field not in it: # prevent override
            it[field] = value
    if not isinstance(value, dict) and not isinstance(value, list):
            it[field] = value

def setAttribute(profile, lastKeys, field, value):
    it = {}
    for key in lastKeys:
        keyVal = key.split('/')
        k = keyVal[0]
        if not it:
            it = profile[k]
        else:
            it = it[k]
            # it is list it means we need to search its content
            # go to that index
            # if it[k][key.split('/')[0]] as found exist
            # it = found
            # if not exist keep it as it is
            if isinstance(it, list):
                index = int(keyVal[1])
                if len(it) > index:
                    it = it[index]

    if isinstance(it, list):
        index = int(lastKeys[-1].split('/')[1]) # get index from ['contactnumber/0']
        if len(it) > index: # find element and element attribute to set value
            setValue(value, field, it[index])
        else: # list is empty so create an element
            for i in range(len(it), index + 1, 1):
                it.append({})
            it[index][field] = value
    else:
        setValue(value, field, it)

def defineField(profile, field):
    keyVal = field.split('/')
    if len(keyVal) > 1:
        key = keyVal[0]
        if key not in profile:
            profile[key] = []
    elif field not in profile:
        profile[field] = {}

profiles = []

def properValue(value):
    proper = None
    try:
        proper = eval(value)
    except:
        proper = value
    return proper

# app starts here

userInput = input("CSV file path: \n")
# assert os.path.exists(userInput): 'CSV not found at path, ' + str(userInput)
if not os.path.exists(userInput):
    print('CSV not found at: ' + str(userInput))
    sys.exit(0)

print('parser running...')
with open(userInput) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    profile = {}
    lastId = None
    firstProfile = True
    for row in csv_reader: # read the csv line by line
        if line_count > 0: # don't read columns
            # print(row[1].rsplit(':', 1))
            fieldValue = row[1].rsplit(':', 1)
            rawFields = [x.strip() for x in fieldValue[0].split('.')]
            rawFields[-1] = rawFields[-1] + ':' + fieldValue[1]
            # stop updating profile when id changes
            # add profile and build it afterwards
            if lastId != row[0]: # new id means add and build profile
                if not firstProfile:
                    profile = {} # reset profile and build it
                profile['id'] = row[0]
                profiles.append(profile) # this profile will be built below
                lastId = row[0]
                firstProfile = False

            lastKeys = []
            for field in rawFields: # build the profile up
                keyVal = field.split(':') # field and value format, we separate it
                if len(keyVal) == 1: # ['answers'] if field doesn't contain value we build it
                    if len(lastKeys) == 0:
                        defineField(profile, field)
                    else:
                        _keyVal = field.split('/')
                        if len(_keyVal) > 1:
                            setAttribute(profile, lastKeys, _keyVal[0], [])
                        else:
                            setAttribute(profile, lastKeys, field, {})
                    lastKeys.append(field)
                else: # ['type', 'mobile']
                    if len(lastKeys) == 0:
                        profile[keyVal[0]] = properValue(keyVal[1])
                    else:
                        setAttribute(profile, lastKeys, keyVal[0], properValue(keyVal[1]))
                    lastKeys.append(keyVal[0])
        line_count += 1

os.makedirs('output', exist_ok=True)
file = open('output/output.json', 'w')
# file.write(json.dumps(profiles, indent=4, sort_keys=True))
file.write(json.dumps(profiles))
file.close()
print('parser completed...')