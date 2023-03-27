#!/usr/bin/env python
import json
import sys
import os
import inspect
import getpass
import requests
import pandas as pd
from requests.exceptions import HTTPError
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

PATH = current_dir

URL = "https://api.extremecloudiq.com"

print("Enter your XIQ login credentials")
username = input("Email: ")
password = getpass.getpass("Password: ")

headers = {"Accept": "application/json", "Content-Type": "application/json"}

locationTree_df = pd.DataFrame(columns = [
    "id",
    "create_time",
    "update_time",
    "org_id",
    "parent_id",
    "name",
    "unique_name",
    "type",
    "address"
    ])

count = 0
global_name = ''

# get access token
def GetaccessToken(username, password):
    url = URL + "/login"
    payload = json.dumps({"username": username, "password": password})
    response = requests.post(url, headers=headers, data=payload)
    if response is None:
        print("ERROR: Not able to login into ExtremeCloudIQ - no response!")
        return -1
    if response.status_code != 200:
        print(f"Error creating building in XIQ - HTTP Status Code: {str(response.status_code)}")
        raise TypeError(response)
    data = response.json()

    if "access_token" in data:
        print("Logged in and Got access token")
        headers["Authorization"] = "Bearer " + data["access_token"]
        return 0

    else:
        raise TypeError("Unknown Error: Unable to gain access token")
    
def __get_api_call(info, url):
        try:
            response = requests.get(url, headers= headers)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err} - on API to {info} - {url}')
            raise ValueError(f'HTTP error occurred: {http_err}') 
        if response is None:
            log_msg = "ERROR: No response received from XIQ!"
            print(log_msg)
            raise ValueError(log_msg)
        if response.status_code != 200:
            log_msg = f"Error - HTTP Status Code: {str(response.status_code)} on API to {info}"
            print(f"{log_msg}")
            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"\t\t{response.text}")
            else:
                if 'error_message' in data:
                    print(f"\t\t{data['error_message']}")
                    raise ValueError(log_msg)
            raise ValueError(log_msg) 
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Unable to parse json data - {url} - HTTP Status Code: {str(response.status_code)}")
            raise ValueError("Unable to parse the data from json, script cannot proceed")
        return data


# LOCATIONS

def __buildLocationDf(location):
    global locationTree_df, count, global_name
    if 'parent_id' not in location:
        temp_df = pd.DataFrame([{
            'id': location['id'], 
            'create_time':location['create_time'], 
            'update_time':location['update_time'],
            'org_id':location['org_id'],
            'name':location['name'],
            'unique_name':location['unique_name'],
            'type':location['type'],
            'address':location['address']
            }])
        locationTree_df = pd.concat([locationTree_df, temp_df], ignore_index=True)
        global_name = location['name']
    else:
        temp_df = pd.DataFrame([{
            'id': location['id'], 
            'create_time':location['create_time'], 
            'update_time':location['update_time'],
            'org_id':location['org_id'],
            'parent_id':location['parent_id'],
            'name':location['name'],
            'unique_name':location['unique_name'],
            'type':location['type'],
            'address':location['address']
            }])
        
        locationTree_df = pd.concat([locationTree_df, temp_df], ignore_index=True)
    if location['type'] == 'Location':
        url = "{}/locations/tree?parentId={}&expandChildren=false".format(URL,location['id'])
        location['children'] = __get_api_call("gather child for {}".format(location['name']),url)
    elif location['type'] == "BUILDING":
        url = "{}/locations/tree?parentId={}&expandChildren=true".format(URL,location['id'])
        location['children'] = __get_api_call("gather child for {}".format(location['name']),url)
    r = json.dumps(location['children'])
    #print(r)
    if location['children']:
        parent_name = location['name']
        for child in location['children']:
            sys.stdout.write(".")
            sys.stdout.flush()
            count += 1
            __buildLocationDf(child)

def gatherLocations():
    global locationTree_df
    info=f"gather location tree"
    url = "{}/locations/tree?expandChildren=false".format(URL)
    response = __get_api_call(info,url)
    print("Gathering Locations", end="")
    for location in response:
        global_id = location['id']
        url = "{}/locations/tree?parentId={}&expandChildren=false".format(URL,global_id)
        child_response = __get_api_call(info,url)
        location['children'] = child_response
        __buildLocationDf(location)
    print("Completed")
    return (locationTree_df)


# MAIN
try:
    login = GetaccessToken(username, password)
except TypeError as e:
    print(e)
    raise SystemExit
except:
    print("Unknown Error: Failed to generate token")
    raise SystemExit

location_df = gatherLocations()
print(f"Writing CSV File {global_name}.csv")
location_df.to_csv(f"{PATH}/{global_name}_export.csv", index=False)



