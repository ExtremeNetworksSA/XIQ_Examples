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

## Change to correct values - Retail
#CLIENTID = '44dcb001'
#SECRET = 'f678f00b87484bedb144988e059bcaca'
#REDIRECT_URI = 'https://127.0.0.1:4000'
#TOKEN = '9knn-oN-rODQWWqU8tQIY5ykEvyHwRmt44dcb001'
#ownerId = '94009'
#DATACENTER = 'ava'

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
msg = ''
pagesize = '400' #Value can be added to set page size. If nothing in quotes default value will be used (500)


# function that makes the API call with the provided url
def get_api_call(url, page=0, pageCount=0, pageSize=0):
    ## used for page if pagesize is set manually
    if page > 0:
        url = '{}&page={}'.format(url, page)
    if pageSize:
        url = "{}&pageSize={}".format(url, pagesize)
    ## the first call will not show as the data returned is used to collect the total count of Clients which is used for the page count
    #print(f"####{url}####")
    if pageCount != 0:
        print("API call on page {:>2} of {:2}".format(page, pageCount), end=": ")
    else:
        print("Attemping call", end=": ")
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
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

def collectRadioMac(data):
    global msg
    for device in data['data']:
        #pprint(device)
        if device['simType'] == 'SIMULATED':
            print(f"Device {device['hostName']} ({device['macAddress']} - id[{device['deviceId']}]) is a simulated device and will not be tracked")
            continue
        ap_id = device['deviceId']
        ap_name = device['hostName']
        url = "{}/xapi/v1/monitor/devices/{}?ownerId={}".format(baseurl, ap_id, ownerId)
        try:
            data = get_api_call(url)
        except TypeError as e:
            print(f"API failed with {e} - {device['hostName']}")
            continue
        except HTTPError as e:
            print(f"API HTTP Error {e}- {device['hostName']}")
            continue
        except:
            print(f"API failed with unknown API error:\n 	{url}- {device['hostName']}")		
            continue
        else:
            print("Successful Connection")
            ap_info = data['data']
            if "wifiInterfaces" in ap_info:
                for radio in ap_info['wifiInterfaces']:
                    if radio['macAddress']:
                        msg += f"{ap_info['hostName']},{radio['interfaceName']}, {radio['macAddress']}\n"

    
def retrieveDevices():
    page = 0
    pageCount = 0
    firstCall = True
    data = {}
    url = "{}/xapi/v1/monitor/devices?ownerId={}".format(baseurl, ownerId)
    while page <= pageCount:    
        try:
            data = get_api_call(url,page,pageCount,pagesize)
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
        collectRadioMac(data)



def main():  
    global msg    
    retrieveDevices()
    print(msg)

if __name__ == '__main__':
    main()