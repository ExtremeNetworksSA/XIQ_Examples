#!/usr/bin/env python3
import requests
import json
import os
import math
import pandas as pd
from requests.exceptions import HTTPError
from pprint import pprint


# User variables
switch_model_list = [] #List the switch models to gather inside of the []'s. Make sure model names have quotes around each model and seperated by a comma. Tested with 'SR_2148P', 'SR_2208P', and 'X435_8P_4S'
totalretries = 5 #Value can be adjusted - this will adjust how many attempts to try each API call
pagesize = '' #Value can be added to set page size. If nothing in quotes default value will be used (500)

# Change to correct values 
CLIENTID = '***'
SECRET = '***'
REDIRECT_URI = '***'
TOKEN = '***'
ownerId = '***'
DATACENTER = '***'

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
device_list = []

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
        r = requests.get(url, headers=HEADERS, timeout=10)
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
                failmsg = (f"Status Code {data['error']['status']}: ")
                if 'message' in data['error']:
                    failmsg += data['error']['message']
                elif 'code' in data['error']:
                    failmsg += data['error']['code']
                raise TypeError(f"API Failed with reason: {failmsg} - on API {url}")
        return data

def retrieveDevices():
    page = 0
    pageCount = 0
    firstCall = True
    success = 0
    global device_list
    data = {}
    url = "{}/xapi/v1/monitor/devices?ownerId={}".format(baseurl, ownerId)
    while page <= pageCount: 
        for count in range(1, totalretries):      
            try:
                data = get_api_call(url,page,pageCount)
            except TypeError as e:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with {e}")
            except ValueError as e:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with {e}")
            except HTTPError as e:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with {e}")
            except:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with unknown API error:\n 	{url}")	
            else:
                print("Successful Connection")
                success = 1
                break
                #print(data['pagination'])
        if success != 1:
            print("Failed to collect devices")
            raise SystemExit

        if firstCall == True:
            totalCount = data['pagination']['totalCount']
            countInPage = data['pagination']['countInPage']
            if countInPage < totalCount:
                pageCount = math.ceil(int(totalCount)/int(countInPage))
            firstCall = False
        page += 1
        for device in data['data']:
            if device['model'] in switch_model_list:
                switch = {"Switch Name":device['hostName'], "Status": device['connected'], "deviceId":device['deviceId'], "Open Ports": " "}
                device_list.append(switch)
    print(f"Found {len(device_list)} Switches")

def getSwithportDetails():
    success = 0
    global device_list
    data = {}
    device_count = 1
    for device in device_list:
        url = "{}/xapi/v1/monitor/devices/{}?ownerId={}".format(baseurl, device['deviceId'],ownerId)
        print(f"Started device {device_count} of {len(device_list)}")
        device_count += 1 
        for count in range(1, totalretries +1): 
            try:
                data = get_api_call(url)
            except TypeError as e:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with {e}")
            except ValueError as e:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with {e}")
            except HTTPError as e:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with {e}")
            except:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with unknown API error:\n 	{url}")	
            else:
                print("Successful Connection")
                success = 1
                break
                #print(data['pagination'])
        if success != 1:
            print("Failed to collect devices")
            raise SystemExit

        open_portlist = []
        disabled_portlist = []
        for port in data['data']['ports']:
            if 'UP' not in port['status']:
                open_portlist.append(port['ifName'])
                if 'DISABLED' in port['status']:
                    disabled_portlist.append(port['ifName'])
        portstr = port_range(open_portlist)
        disabledportstr = port_range(disabled_portlist)
        device['Model'] = data['data']['model']  
        device['Open Ports'] = portstr
        device['Disabled Ports'] = disabledportstr

def port_range(port_list):
    new_list = []
    for port in port_list:
        newport = port.replace('eth1/','')
        newport = port.replace('1/0/','')
        newport = int(newport)
        new_list.append(newport)
    
    sorted_list = sorted(new_list)
    #print(sorted_list)
    port_range_list = []
    listmin = 0 
    for i in sorted_list:
        if i+1 in sorted_list:
            if listmin == 0:
                listmin = i
            else:
                continue
        elif listmin == 0:
            port_range_list.append(f"{str(i)}")
        else:
            port_range_list.append(f"{str(listmin)}-{str(i)}")
            listmin = 0
    port_range_str = "; ".join(port_range_list)
    return port_range_str

def status_correct(status):
    if status == True:
        return "Online"
    elif status == False:
        return "Offline"
    else:
        return status
## MAIN 

retrieveDevices()
if len(device_list) == 0:
    raise SystemExit
getSwithportDetails()
df = pd.DataFrame(device_list)
df.set_index('deviceId', inplace=True)
df['Status'] = df['Status'].apply(status_correct)
df = df.sort_values('Switch Name')
df[['Switch Name', 'Model', 'Status', 'Open Ports', 'Disabled Ports']].to_csv("OpenPortList.csv",index=False)
