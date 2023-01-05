#!/usr/bin/env python3
import requests
import json
import os
import time
import logging
import pandas as pd

#XIQ_username = "enter your ExtremeCloudIQ Username"
#XIQ_password = "enter your ExtremeCLoudIQ password"
####OR###
## TOKEN permission needs - enduser, pcg:key
XIQ_token = '****'

today = time.strftime("%Y-%m-%d")

#-------------------------
# logging
PATH = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    filename='{}/XIQ-Inventory.log'.format(PATH),
    filemode='a',
    level=os.environ.get("LOGLEVEL", "INFO"),
    format= '%(asctime)s: %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

URL = "https://api.extremecloudiq.com"
headers = {"Accept": "application/json", "Content-Type": "application/json"}

def getAccessToken(XIQ_username, XIQ_password):
    url = URL + "/login"
    payload = json.dumps({"username": XIQ_username, "password": XIQ_password})
    response = requests.post(url, headers=headers, data=payload)
    if response is None:
        log_msg = "ERROR: Not able to login into ExtremeCloudIQ - no response!"
        logging.error(log_msg)
        raise TypeError(log_msg)
    if response.status_code != 200:
        log_msg = f"Error getting access token - HTTP Status Code: {str(response.status_code)}"
        logging.error(f"{log_msg}")
        logging.warning(f"\t\t{response}")
        raise TypeError(log_msg)
    data = response.json()

    if "access_token" in data:
        #print("Logged in and Got access token: " + data["access_token"])
        headers["Authorization"] = "Bearer " + data["access_token"]
        return 0

    else:
        log_msg = "Unknown Error: Unable to gain access token"
        logging.warning(log_msg)
        raise TypeError(log_msg)

def retrieveDevices(pageSize):
    page = 1
    pageCount = 1
    firstCall = True

    device_list = []

    while page <= pageCount:
        url = URL + "/devices?page=" + str(page) + "&limit=" + str(pageSize)

        # Get the next page of the ppsk users
        response = requests.get(url, headers=headers, verify = True)
        if response is None:
            log_msg = "Error retrieving Devices from XIQ - no response!"
            logging.error(log_msg)
            raise TypeError(log_msg)

        elif response.status_code != 200:
            log_msg = f"Error retrieving Devices from XIQ - HTTP Status Code: {str(response.status_code)}"
            logging.error(log_msg)
            logging.warning(f"\t\t{response.json()}")
            raise TypeError(log_msg)

        rawList = response.json()
        device_list = device_list + rawList['data']

        if firstCall == True:
            pageCount = rawList['total_pages']
        print(f"completed page {page} of {rawList['total_pages']} collecting Devices")
        page = rawList['page'] + 1 
    return device_list

def main():
    if 'XIQ_token' not in globals():
        try:
            login = getAccessToken(XIQ_username, XIQ_password)
        except TypeError as e:
            print(e)
            raise SystemExit
        except:
            log_msg = "Unknown Error: Failed to generate token"
            logging.error(log_msg)
            print(log_msg)
            raise SystemExit     
    else:
        headers["Authorization"] = "Bearer " + XIQ_token
    try:
        device_list = retrieveDevices(100)
    except TypeError as e:
        print(e)
        print("script exiting....")
        raise SystemExit
    except:
        log_msg = ("Unknown Error: Failed to retrieve devices from XIQ")
        logging.error(log_msg)
        print(log_msg)
        print("script exiting....")
        raise SystemExit

    log_msg = ("Successfully parsed " + str(len(device_list)) + " XIQ devices")
    logging.info(log_msg)
    print(f"{log_msg}\n")  

    device_df = pd.DataFrame(device_list)
    device_df = device_df.set_index('id')
    device_df.to_csv(f"{PATH}/{today}_XIQ_Inventory.csv")


if __name__ == '__main__':
	main()