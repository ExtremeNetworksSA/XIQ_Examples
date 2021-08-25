#!/usr/bin/env python3
import requests
import json
import os
import math
from requests.exceptions import HTTPError
from pprint import pprint

# Change to correct values 
CLIENTID = '***'
SECRET = '***'
REDIRECT_URI = '***'
TOKEN = '***'
ownerId = '***'
DATACENTER = '***'

# add/remove AP and switch lists
ap_model_list = ['AP_1130','AP_121','AP_230','AP_30','AP_410C']
switch_model_list = ['SR_2148P','X440_G2_12p_10_G4']les

# Used to build API call
baseurl = 'https://{}.extremecloudiq.com'.format(DATACENTER)
HEADERS= {
    'X-AH-API-CLIENT-ID':CLIENTID,
    'X-AH-API-CLIENT-SECRET':SECRET,
    'X-AH-API-CLIENT-REDIRECT-URI':REDIRECT_URI,
    'Authorization':'Bearer {}'.format(TOKEN),
    'Content-Type': 'application/json'
    }

PATH = os.path.dirname(os.path.abspath(__file__))

# Global Objects
locations = {}
locations['Unassigned']={}
modelset = []
pagesize = '400' #Value can be added to set page size. If nothing in quotes default value will be used (500)



# function that makes the API call with the provided url
# if pageCount is defined (all calls per hour after initial call) if the call fails they will be added to the secondtry list 
def get_api_call(url, page=0, pageCount=0):
    ## used for page if pagesize is set manually
    if page > 0:
        url = '{}&page={}'.format(url, page)
    if pagesize:
        url = "{}&pageSize={}".format(url, pagesize)
    ## the first call will not show as the data returned is used to collect the total count of Clients which is used for the page count
    #print(f"####{url}####")
    if pageCount != 0:
        print("API call on page {:>2} of {:2}".format(page, pageCount), end=": ")
    else:
        print("Attemping call", end=": ")
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
    except HTTPError as http_err:
        #if pageCount != 0:
        #    secondtry.append(url)
        raise HTTPError(f'HTTP error occurred: {http_err} - on API {url}')  
    except Exception as err:
        #if pageCount != 0:
        #    secondtry.append(url)
        raise TypeError(f'Other error occurred: {err}: on API {url}')
    else:
        data = json.loads(r.text)
        if 'error' in data:
            if data['error']:
                failmsg = (f"Status Code {data['error']['status']}: {data['error']['message']}")
                raise TypeError(f"API Failed with reason: {failmsg} - on API {url}")
        return data

def checkLocations(data):
    global locations
    global modelset
    for device in data['data']:
        #pprint(device)
        if device['simType'] == 'SIMULATED':
            print(f"Device {device['hostName']} ({device['macAddress']} - id[{device['deviceId']}]) is a simulated device and will not be tracked")
            continue
        if device['locations'] == None:
            #print(f"Device {device['hostName']} ({device['macAddress']} - id[{device['deviceId']}]) does not have a location assigned")
            if device['model'] not in locations['Unassigned']:
                locations['Unassigned'][device['model']] = 1
            else:
                locations['Unassigned'][device['model']] += 1
        else:
            loclist = device['locations']
            #print(loclist)
            #mainLocation = '/'.join([str(elem) for elem in loclist])
            if len(loclist) > 2:
                mainLocation = loclist[2]
            else:
                mainLocation = 'Unassigned'
                #print(mainLocation)
            if mainLocation not in locations:
                locations[mainLocation]={}
            if device['model'] not in locations[mainLocation]:
                locations[mainLocation][device['model']] = 1
            else:
                locations[mainLocation][device['model']] += 1

    
def retrieveDevices():
    page = 0
    pageCount = 0
    firstCall = True
    data = {}
    url = "{}/xapi/v1/monitor/devices?ownerId={}".format(baseurl, ownerId)
    while page <= pageCount:    
        try:
            data = get_api_call(url,page,pageCount)
        except TypeError as e:
            print(f"API failed with {e}")
            raise SystemExit
        except HTTPError as e:
            print(f"API HTTP Error {e}")
            raise SystemExit
        except:
            print(f"API failed with unknown API error:\n 	{url}")		
            raise SystemExit
        else:
            print("Successful Connection")
            #print(data['pagination'])
        if firstCall == True:
            totalCount = data['pagination']['totalCount']
            countInPage = data['pagination']['countInPage']
            if countInPage < totalCount:
                pageCount = math.ceil(int(totalCount)/int(countInPage))
            firstCall = False
        page += 1
        checkLocations(data)
        
retrieveDevices()

msg = "Location, Total APs, Total Switches, "
for model in ap_model_list:
    msg += "{}, ".format(model)
for model in switch_model_list:
    msg += "{}, ".format(model)
msg += 'Total Devices,\n'
for site, devices in sorted(locations.items()):
    total_devices = sum(devices.values())
    msg += "{}, ".format(site.replace(',',''))
    #print("{}, {}, ".format(site, devices))
    msg_line = ''
    ap_count = 0
    switch_count = 0
    for model in devices:
        if model in ap_model_list:
            ap_count += devices[model]
        elif model in switch_model_list:
            switch_count += devices[model]
        else:
            print(f"Unable to find device with model {model}")
    for model in ap_model_list + switch_model_list:
        if model in devices:
            msg_line += "{}, ".format(devices[model])
        else:
            msg_line += " 0, "
    msg += "{},{},{}{},\n".format(ap_count,switch_count,msg_line,total_devices)
#pprint(locations)
#print(msg)
with open(PATH+"/Location_Models.csv", 'w') as f:
    f.write(msg)
