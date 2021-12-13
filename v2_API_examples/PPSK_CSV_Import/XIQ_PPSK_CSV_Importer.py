#!/usr/bin/env python3
import json
import requests
import logging
import os
import pandas as pd
import numpy as np
from pprint import pprint


####################################
# written by:   Tim Smith
# e-mail:       tismith@extremenetworks.com
# date:         8th December 2021
# version:      1.0.0
####################################

#XIQ_username = "enter your ExtremeCloudIQ Username"
#XIQ_password = "enter your ExtremeCLoudIQ password"
####OR###
## TOKEN permission needs - enduser
XIQ_token = "****"

usergroupID = "enter the user group id"

filename = "PPSK_Users.csv"

#-------------------------
# logging
PATH = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    filename='{}/XIQ_PPSK_CSV_Importer.log'.format(PATH),
    filemode='a',
    level=os.environ.get("LOGLEVEL", "INFO"),
    format= '%(asctime)s: %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

URL = "https://api.extremecloudiq.com"
headers = {"Accept": "application/json", "Content-Type": "application/json"}

def GetaccessToken(XIQ_username, XIQ_password):
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
        try:
            data = response.json()
            if "error_message" in data:
                log_msg += f"\n\t{data['error_message']}"
        except:
            log_msg += ""
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

def retrievePPSKusers(pageSize, usergroupID):
    #print("Retrieve all PPSK users from ExtremeCloudIQ")
    page = 1

    ppskusers = []

    while page < 1000:
        url = URL + "/endusers?page=" + str(page) + "&limit=" + str(pageSize) + "&user_group_ids=" + str(usergroupID)
        #print("Retrieving next page of PPSK users from ExtremeCloudIQ starting at page " + str(page) + " url: " + url)

        # Get the next page of the ppsk users
        response = requests.get(url, headers=headers, verify = True)
        if response is None:
            log_msg = "Error retrieving PPSK users from XIQ - no response!"
            logging.error(log_msg)
            raise TypeError(log_msg)
        elif response.status_code != 200:
            log_msg = f"Error retrieving PPSK users from XIQ - HTTP Status Code: {str(response.status_code)}"
            logging.error(f"Error retrieving PPSK users from XIQ - HTTP Status Code: {str(response.status_code)}")
            logging.warning(f"\t\t{response.json()}")
            try:
                data = response.json()
                if "error_message" in data:
                    log_msg += f"\n\t{data['error_message']}"
            except:
                log_msg += ""
            raise TypeError(log_msg)
        rawList = response.json()['data']
        #for name in rawList:
        #    print(name)
        #print("Retrieved " + str(len(rawList)) + " users on this page")
        ppskusers = ppskusers + rawList
        if len(rawList) == 0:
            #print("Reached the final page - stopping to retrieve users ")
            break
        page = page + 1
    return ppskusers

def CreatePPSKuser(payload, name):
    url = URL + "/endusers"

    #print("Trying to create user using this URL and payload " + url)
    response = requests.post(url, headers=headers, data=payload, verify=True)
    if response is None:
        log_msg = "Error adding PPSK user - no response!"
        logging.error(log_msg)
        raise TypeError(log_msg)

    elif response.status_code != 200:
        log_msg = f"Error adding PPSK user {name} - HTTP Status Code: {str(response.status_code)}"
        logging.error(log_msg)
        logging.warning(f"\t\t{response.json()}")
        try:
            data = response.json()
            if "error_message" in data:
                log_msg += f"\n\t{data['error_message']}"
        except:
            log_msg += ""
        raise TypeError(log_msg)

    elif response.status_code ==200:
        logging.info(f"successfully created PPSK user {name}")
        print(f"successfully created PPSK user {name}")
    #print(response)

def deleteuser(userId):
    url = URL + "/endusers/" + str(userId)
    #print("\nTrying to delete user using this URL and payload\n " + url)
    response = requests.delete(url, headers=headers, verify=True)
    if response is None:
        log_msg = f"Error deleting PPSK user {userId} - no response!"
        logging.error(log_msg)
        raise TypeError(log_msg)
    elif response.status_code != 200:
        log_msg = f"Error deleting PPSK user {userId} - HTTP Status Code: {str(response.status_code)}"
        logging.error(log_msg)
        logging.warning(f"\t\t{response}")
        try:
            data = response.json()
            if "error_message" in data:
                log_msg += f"\n\t{data['error_message']}"
        except:
            log_msg += ""
        raise TypeError(log_msg)
    elif response.status_code == 200:
        return 'Success'
    #print(response)

def main():
    ##  load CSV file   ##
    if os.path.isfile(PATH + '/' + filename):
        try:
            df = pd.read_csv(PATH + '/' + filename)
        except:
            print(f"failed to load file {filename}")
            print("script exiting....")
            raise SystemExit
    else:
        print(f"The file {filename} was not in {PATH}")
        print("script exiting....")
        raise SystemExit

    
    df = df.replace(np.nan," ")

    ## Get token for Main Account ##
    if not XIQ_token:
        try:
            login = GetaccessToken(XIQ_username, XIQ_password)
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
    
    # Retrieve PPSK users for group id
    try:
        ppsk_users = retrievePPSKusers(100,usergroupID)
    except TypeError as e:
        print(e)
        print("script exiting....")
        raise SystemExit
    except:
        log_msg = ("Unknown Error: Failed to retrieve users from XIQ")
        logging.error(log_msg)
        print(log_msg)
        print("script exiting....")
        raise SystemExit
    log_msg = ("Successfully parsed " + str(len(ppsk_users)) + " XIQ users")
    logging.info(log_msg)
    print(f"\n{log_msg}")
    
    for index, row in df.iterrows():
        if any(row['User Name'] in x['user_name'] for x in ppsk_users):
            print(f"User {row['User Name']} already exists, skipping user")
        else:
            payload = json.dumps({"user_group_id": usergroupID ,
                "name": f"{row['First Name']} {row['Last Name']}",
                "user_name": row['User Name'],
                "organization": row['Organization'],
                "visit_purpose": row['Visiting Purpose'],
                "description": row['Description'],
                "email_address": row['Email'],
                "password": row['Password'],
                "email_password_delivery": row['Email']})
            try:
                CreatePPSKuser(payload, row['User Name'])
            except TypeError as e:
                log_msg = f"failed to create {row['User Name']}: {e}"
                logging.error(log_msg)
                print(log_msg)
            except:
                log_msg = f"Unknown Error: Failed to create user {row['User Name']} - {row['Email']}"
                logging.error(log_msg)
                print(log_msg)
    for ppsk_user in ppsk_users:
        if ppsk_user['user_name'] not in df.values:
            ## Delete PPSK user ##
            try:
                result= deleteuser(ppsk_user['id'])
            except TypeError as e:
                logmsg = f"Failed to delete user {ppsk_user['user_name']}  with error {e}"
                logging.error(logmsg)
                print(logmsg)
                continue
            except:
                log_msg = f"Unknown Error: Failed to create user {ppsk_user['user_name']} "
                logging.error(log_msg)
                print(log_msg)
                continue
            if result == 'Success':
                log_msg = f"User {ppsk_user['user_name']} - {ppsk_user['id']} was successfully deleted."
                logging.info(log_msg)
                print(log_msg)  
        
if __name__ == '__main__':
	main()