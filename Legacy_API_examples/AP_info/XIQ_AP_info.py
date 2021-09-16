#!/usr/bin/env python3
import requests
import json
import os
import math
import pandas as pd
import multiprocessing
from requests.exceptions import HTTPError
from pprint import pprint

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
pagesize = '' #Value can be added to set page size. If nothing in quotes default value will be used (500)
sizeofbatch = 50 #Value can be adjusted - this will adjust how many simultanious API calls will happen when collecting radio info

# function that makes the API call with the provided url
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

def get_api_call_multi(device, url, mp_queue):
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
    except HTTPError as http_err:
        mp_queue.put(f"ERROR: HTTP error occurred: {http_err} - on API {url} - device {device['name']}")
    except Exception as err:
        mp_queue.put(f"ERROR: Other error occurred: {err}: on API {url} - device {device['name']}")
    else:
        data = json.loads(r.text)
        if 'error' in data:
            if data['error']:
                failmsg = (f"Status Code {data['error']['status']}: {data['error']['message']}")
                mp_queue.put(f"ERROR: API Failed with reason: {failmsg} - on API {url} - device {device['name']}")
            else:
                txinfo = {}
                rxinfo = {}
                for radio in data['data']['wifiInterfaces']:
                    txinfo[radio['interfaceName']] = radio['txByteCount']
                    rxinfo[radio['interfaceName']] = radio['rxByteCount']
                device['tx']=txinfo
                device['rx']=rxinfo
    mp_queue.put(device)
    
            
def radiodetails(ap_list):
    updated_ap_list = []
    for i in range(0, len(ap_list), sizeofbatch):
        batch = ap_list[i:i+sizeofbatch]
        if i+sizeofbatch < len(ap_list):
            print(f"Collecting {i+1}-{i+sizeofbatch} of {len(ap_list)}: APs radio info")
        else:
            print(f"Collecting {i+1}-{len(ap_list)} of {len(ap_list)}: APs radio info")
        mp_queue = multiprocessing.Queue()
        processes = []
        for device in batch:
            url = "{}/xapi/v1/monitor/devices/{}?ownerId={}".format(baseurl, device['deviceid'], ownerId)
            p = multiprocessing.Process(target=get_api_call_multi,args=(device,url,mp_queue))
            processes.append(p)
            p.start()
        for p in processes:
            try:
                p.join()
                p.terminate()
            except:
                print("Error occured in thread")
        mp_queue.put('STOP')
        for line in iter(mp_queue.get, 'STOP'):
            if "ERROR" in line:
                print(line)
            else:
                updated_ap_list.append(line)
    return updated_ap_list
            
def retrieveDevices():
    page = 0
    pageCount = 0
    firstCall = True
    ap_list = []
    url = "{}/xapi/v1/monitor/devices?ownerId={}".format(baseurl, ownerId)
    while page <= pageCount:    
        try:
            data = get_api_call(url,page,pageCount)
        except TypeError as e:
            print("Failed Connection")
            print(f"API failed with {e}")
            raise SystemExit
        except HTTPError as e:
            print("Failed Connection")
            print(f"API HTTP Error {e}")
            raise SystemExit
        except:
            print("Failed Connection")
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
        for device in data['data']:
            if device['locations'] == None:
                locations = 'Unassigned'
            else:
                locations = '/'.join(device['locations'])
            deviceinfo = {
                'deviceid': device['deviceId'],
                'name': device['hostName'],
                'location': locations,
                'status': device['connected'],
                'tx': {},
                'rx': {}
            }
            if deviceinfo['status'] == True:
                deviceinfo['status'] = 'connected'
            else:
                deviceinfo['status'] = 'disconnected'
            ap_list.append(deviceinfo)
    ap_list = radiodetails(ap_list)
    return ap_list    

def main():
    ap_list = retrieveDevices()
    pprint(ap_list)
    df = pd.DataFrame(ap_list)
    df.set_index('deviceid', inplace=True)
    print(df)
    #df.to_csv('test.csv', index=False)

if __name__ == '__main__':
    main()