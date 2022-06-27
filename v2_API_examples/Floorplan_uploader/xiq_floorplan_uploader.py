#!/usr/bin/env python3
import requests
from requests.exceptions import HTTPError, ConnectTimeout
import json
import os
import inspect
import time
import getpass
import sys
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

PATH = current_dir

URL = "https://api.extremecloudiq.com"
headers = {"Accept": "application/json", "Content-Type": "application/json"}
totalretries = 5


def __post_api_call(url, payload):
    try:
        response = requests.post(url, headers= headers, data=payload)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err} - on API {url}')
        raise ValueError(f'HTTP error occurred: {http_err}') 
    if response is None:
        log_msg = "ERROR: No response received from XIQ!"
        print(log_msg)
        raise ValueError(log_msg)
    if response.status_code == 202:
        return "Success"
    elif response.status_code != 200:
        log_msg = f"Error - HTTP Status Code: {str(response.status_code)}"
        print(f"{log_msg}")
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"\t\t{response.text()}")
        else:
            if 'error_message' in data:
                print(f"\t\t{data['error_message']}")
                raise Exception(data['error_message'])
        raise ValueError(log_msg)
    try:
        data = response.json()
    except json.JSONDecodeError:
        print(f"Unable to parse json data - {url} - HTTP Status Code: {str(response.status_code)}")
        raise ValueError("Unable to parse the data from json, script cannot proceed")
    return data

def __getAccessToken(user_name, password):
    info = "get XIQ token"
    success = 0
    url = URL + "/login"
    payload = json.dumps({"username": user_name, "password": password})
    for count in range(1, totalretries):
        try:
            data = __post_api_call(url=url,payload=payload)
        except ValueError as e:
            print(f"API to {info} failed attempt {count} of {totalretries} with {e}")
        except Exception as e:
            print(f"API to {info} failed with {e}")
            print('script is exiting...')
            raise SystemExit
        except:
            print(f"API to {info} failed attempt {count} of {totalretries} with unknown API error")
        else:
            success = 1
            break
    if success != 1:
        print("failed to get XIQ token. Cannot continue to import")
        print("exiting script...")
        raise SystemExit
    
    if "access_token" in data:
        #print("Logged in and Got access token: " + data["access_token"])
        headers["Authorization"] = "Bearer " + data["access_token"]
        return 0
    else:
        log_msg = "Unknown Error: Unable to gain access token for XIQ"
        print(log_msg)
        raise ValueError(log_msg)


def __image_api_call(url, files):
    try:
        response = requests.post(url, headers= headers, files=files)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err} - on API {url}')
        raise ValueError(f'HTTP error occurred: {http_err}') 
    if response is None:
        log_msg = "ERROR: No response received from XIQ!"
        print(log_msg)
        raise ValueError(log_msg)
    if response.status_code != 200:
        log_msg = f"Error - HTTP Status Code: {str(response.status_code)}"
        print(f"{log_msg}")
        try: 
            data = response.json()
        except json.JSONDecodeError:
            print(f"\t\t{response.text()}")
        else:
            if 'error_message' in data:
                print(f"\t\t{data['error_message']}")
                raise Exception(data['error_message'])
        raise ValueError(log_msg)
    return 0

#FLOORS
def uploadFloorplan(filename):
    info=f"upload file '{filename}'"
    success = 0
    url = "{}/locations/floorplan".format(URL)
    filepathname = PATH + f"/images/{filename}"
    files={
        'file' : (f'{filename}', open(filepathname, 'rb'), 'image/png'),
        'type': 'image/png'
    }
    for count in range(1, totalretries):
        try:
            __image_api_call(url=url, files=files)
        except ValueError as e:
            print(f"\nAPI to {info} failed attempt {count} of {totalretries} with {e}")
        except Exception as e:
            print(f"\nAPI to {info} failed with {e}")
            print('script is exiting...')
            raise SystemExit
        except:
            print(f"\nAPI to {info} failed attempt {count} of {totalretries} with unknown API error")
        else:
            success = 1
            break
    if success != 1:
        print("\nfailed to {}. Cannot continue to import".format(info))
        print("exiting script...")
        raise SystemExit
    else:
        return 0


#MAIN

## XIQ Login

print("Enter your XIQ login credentials")
username = input("Email: ")
password = getpass.getpass("Password: ")


__getAccessToken(username,password)
print("successfully logged into XIQ")
del headers['Content-Type']
for filename in os.listdir(PATH+'/images'):
    print(f"Uploading {filename} to XIQ.... ", end='')
    sys.stdout.flush()
    uploadFloorplan(filename)
    time.sleep(10)
    print("Completed\n")