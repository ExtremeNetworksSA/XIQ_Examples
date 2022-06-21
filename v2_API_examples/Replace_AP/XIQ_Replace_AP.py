#!/usr/bin/env python3
import requests
import json
import time
from pprint import pprint
from requests.exceptions import HTTPError


#Global Objects
# The Name of the AP to replace
Old_AP_Name = 'Enter the name of the old AP'
# The serial number of the new AP
new_AP_SN = 'Enter serial number of the new AP'
pagesize = '' #Value can be added to set page size. If nothing in quotes default value will be used (10). Page Size, min = 1, max = 100
totalretries = 5


# generated xiq token with minimum "device:list, device, device:cli" permissions
XIQ_token = "****"
baseurl = "https://api.extremecloudiq.com"
HEADERS = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Bearer " + XIQ_token}


# function that makes the API call with the provided url
# if pageCount is defined (all calls per hour after initial call) if the call fails they will be added to the secondtry list 
def get_api_call(url, page=0, pageCount=0,  msg='', count = 1):
    ## used for page if pagesize is set manually
    url_parms = []
    if page > 0:
        url = url + '&page={}'.format(page)
    if pagesize:
        url = url + "&limit={}".format(pagesize)
    #print(url)
    
    #print(f"####  {url}  ####")
    if pageCount != 0:
        print("API call {} page {:>2} of {:2} - attempt {} of {}".format(msg,page, pageCount, count, totalretries), end=": ")
    else:
        print("Attempting call {} - attempt {} of {}".format(msg, count, totalretries), end=": ")
    try:
        response = requests.get(url, headers=HEADERS, timeout=60)
    except HTTPError as http_err:
        raise HTTPError(f'HTTP error occurred: {http_err} - on API {url}')  
    except Exception as err:
        raise TypeError(f'Other error occurred: {err}: on API {url}')
    else:
        if response is None:
            error_msg = f"Error retrieving API {msg} from XIQ - no response!"
            raise TypeError(error_msg)
        elif response.status_code != 200:
            error_msg = f"Error retrieving API {msg} from XIQ - HTTP Status Code: {str(response.status_code)}"
            raise TypeError(error_msg)   
        data = response.json()
        return data

def post_api_call(url, payload = {}, msg='', count = 1):
    #print(f"####  {url}  ####")

    print("Attempting call {} - attempt {} of {}".format(msg, count, totalretries), end=": ")
    try:
        response = requests.post(url, headers=HEADERS, data=payload, timeout=60)
    except HTTPError as http_err:
        raise HTTPError(f'HTTP error occurred: {http_err} - on API {url}')  
    except Exception as err:
        raise TypeError(f'Other error occurred: {err}: on API {url}')
    else:
        if response is None:
            error_msg = f"Error retrieving API {msg} from XIQ - no response!"
            raise TypeError(error_msg)
        if response.status_code == 202:
            return "Success"
        elif response.status_code != 200:
            error_msg = f"Error API {msg} to XIQ - HTTP Status Code: {str(response.status_code)}"
            #raise TypeError(error_msg)  
            try: 
                data = response.json()
            except json.JSONDecodeError:
                print(f"Failed to parse json data {msg}")
                print(f"\t\t{response.text()}")
            else:
                if 'error_message' in data:
                    log_msg = (f"Status Code {str(response.status_code)}: {data['error_message']}")
                    print(f"API Failed with reason: {log_msg}")
                    print("Script is exiting...")
                    raise SystemExit
        return data

def put_api_call(url, payload='', info='', count = 1):
    print("Attempting call {} - attempt {} of {}".format(info, count, totalretries), end=": ")
    try:
        if payload:
            response = requests.put(url, headers= HEADERS, data=payload)
        else:
            response = requests.put(url, headers= HEADERS)
    except HTTPError as http_err:
        raise ValueError(f'HTTP error occurred: {http_err}') 
    if response is None:
        log_msg = f"ERROR: No response received from XIQ {info}!"
        raise ValueError(log_msg)
    if response.status_code != 200:
        log_msg = f"Error API {info} to XIQ - HTTP Status Code: {str(response.status_code)}"
        print(f"API {info} failed with = {log_msg}")
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Failed to parse json data {info}")
            print(f"\t\t{response.text()}")
        else:
            if 'error_message' in data:
                log_msg = (f"Status Code {str(response.status_code)}: {data['error_message']}")
                print(f"API Failed with reason: {log_msg}")
                print("Script is exiting...")
                raise SystemExit
    return response.status_code


def delete_api_call(url, info='', count = 1):
    print(f"Attempting call {info} - attempt {count} of {totalretries}", end=": ")
    try:
        response = requests.delete(url, headers=HEADERS)
    except HTTPError as http_err:
        raise ValueError(f'HTTP error occurred: {http_err}') 
    if response is None:
        log_msg = f"ERROR: No response received from XIQ {info}!"
        raise ValueError(log_msg)
    if response.status_code != 200:
        log_msg = f"Error API {info} to XIQ - HTTP Status Code: {str(response.status_code)}"
        print(f"API {info} failed with = {log_msg}")
        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Failed to parse json data {info}")
            print(f"\t\t{response.text()}")
        else:
            if 'error_message' in data:
                log_msg = (f"Status Code {str(response.status_code)}: {data['error_message']}")
                print(f"API Failed with reason: {log_msg}")
                print("Script is exiting...")
                raise SystemExit
    return response.status_code

def __setup_get_api_call(url, error_msg):
    for count in range(1, totalretries):
        try:
            response = get_api_call(url=url,msg=error_msg, count=count)
        except TypeError as e:
            print(f"API failed with {e}")
            count+=1
            success = False
        except HTTPError as e:
            print(f"API HTTP Error {e}")
            count+=1
            success = False
        except:
            print(f"API failed {error_msg} with an unknown API error:\n 	{url}")		
            count+=1
            success = False
        else:
            print("Successful Connection")
            success = True
            break
    if success == False:
        print(f"API call {error_msg} failed too many times. Script is exiting...")
        raise SystemExit
    if 'error' in response:
        if response['error_mssage']:
            log_msg = (f"Status Code {response['error_id']}: {response['error_message']}")
            print(f"API Failed {error_msg} with reason: {log_msg}")
            print("Script is exiting...")
            raise SystemExit
    return response

def __setup_post_api_call(info, url, payload):
    success = 0
    for count in range(1, totalretries):
        try:
            response = post_api_call(url=url, payload=payload, msg=info, count=count)
        except TypeError as e:
            print(f"API failed with {e}")
            count+=1
            success = False
        except HTTPError as e:
            print(f"API HTTP Error {e}")
            count+=1
            success = False
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
        print("failed {}. Cannot continue to import".format(info))
        print("exiting script...")
        raise SystemExit
    if 'error' in response:
        if response['error_mssage']:
            log_msg = (f"Status Code {response['error_id']}: {response['error_message']}")
            print(f"API Failed {info} with reason: {log_msg}")
            print("Script is exiting...")
            raise SystemExit
    return response  

def __setup_put_api_call(info, url, payload=''):
    success = 0
    for count in range(1, totalretries):
        try:
            if payload:
                put_api_call(url=url, payload=payload, info=info, count=count)
            else:
                put_api_call(url=url, info=info)
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
        print("failed to {}. Cannot continue to configure device.".format(info))
        print("exiting script...")
        raise SystemExit
    
    return 'Success'

def __setup_delete_api_call(info, url):
    success = 0
    for count in range(1, totalretries):
        try:
            delete_api_call(url=url, info=info, count=count)
        except ValueError as e:
            print(f"API to {info} failed attempt {count} of {totalretries} with {e}")
        except Exception as e:
            print(f"API to {info} failed with {e}")
            print("script is exiting...")
            raise SystemExit
        else:
            success = 1
            break
    if success != 1:
        print(f"failed to {info}. Cannot continue.")
        print("script is exiting")
        raise SystemExit
    return 'Success'

def getDevice(ap_name):
    ap_data = {}
    error_msg = f"to receive old AP with the name '{ap_name}'"
    url = f"{baseurl}/devices?hostnames={ap_name}"
    data = __setup_get_api_call(url,error_msg)
    if len(data['data']) == 0:
        print(f"No APs were found with the name '{ap_name}'. Script is exiting...")
        raise SystemExit
    for ap in data['data']:
        ap_id = ap['id']
        ap_data[ap_id] = {
            'ap_name': ap['hostname'],
            'ap_model': ap['product_type']
            }
    if len(ap_data) != 1:
        print(f"More than one AP was found with the name '{ap_name}. Script is exiting...")
        raise SystemExit
    
    #get network policy for device
    error_msg = f"to receive old AP '{ap_name}'s network policy"
    url = f"{baseurl}/devices/{ap_id}/network-policy"
    data = __setup_get_api_call(url,error_msg)
    ap_data[ap_id]['network-policy'] = data['id']

    #get location info for device
    error_msg = f"to receive old AP '{ap_name}'s location info"
    url = f"{baseurl}/devices/{ap_id}/location"
    data = __setup_get_api_call(url,error_msg)
    ap_data[ap_id]['location'] = {
        "location_id": data['location_id'],
        "x": data['x'],
        "y": data['y'],
        "latitude": data['latitude'],
        "longitude": data['longitude']
    }
    return ap_id, ap_data[ap_id]
    
def onboardAps(data):
    info="to onboard APs"
    url = f"{baseurl}/devices/:onboard"
    payload = json.dumps(data)
    response = __setup_post_api_call(info=info,url=url,payload=payload)
    return response

def checkApBySerial(ap_serial):
    info="to check new AP by Serial Number"
    url = f"{baseurl}/devices?limit=100&sns={ap_serial}"
    response = __setup_get_api_call(url=url, error_msg=info)
    if response['data']:
        return(response['data'][0])
    else:
        print("These AP serial numbers were not able to be onboarded at this time. Please check the serial numbers and try again")
        print("script is exiting...")
        raise SystemExit
    
def renameAP(ap_id, name):
    info="to rename AP '{}'".format(ap_id)
    url = f"{baseurl}/devices/{ap_id}/hostname?hostname={name}"
    response = __setup_put_api_call(info,url)
    return response

def changeAPLocation(ap_id, data):
    info=f"to set location for AP '{ap_id}'"
    payload = json.dumps(data)
    url = f"{baseurl}/devices/{ap_id}/location"
    response = __setup_put_api_call(info,url,payload=payload)
    return response

def changeAPNetworkPolicy(ap_id, np_id):
    info=f"to set the network-policy for AP '{ap_id}'"
    url = f"{baseurl}/devices/{ap_id}/network-policy?networkPolicyId={np_id}"
    response = __setup_put_api_call(info,url)
    return response

def deleteAP(ap_id):
    info = f'to delete device {ap_id}'
    url = f"{baseurl}/devices/{ap_id}"
    response = __setup_delete_api_call(info,url)
    return response
    
def main():
    replaceSuccess = True
    global Old_AP_Name
    apid, ap_data = getDevice(Old_AP_Name)
    data = {
            "extreme":{
                "sns" : [new_AP_SN]
            }
        }
    response = onboardAps(data)
    time.sleep(10)
    if response != 'Success':
        print(f"Failed to onboard APs with these serial numbers:  {new_AP_SN}. Script is exiting...")
        raise SystemExit
    else:
        print("Validating")
    # checks if the device exists based on the serial number. If the device is already onboarded in a different viq this will return with no devices.
    new_ap_data = checkApBySerial(new_AP_SN)
    print(f"AP '{new_AP_SN} is onboarded")
    # Check if the model is the same as the previous device
    if new_ap_data['product_type'].strip() != ap_data['ap_model'].strip():
        print(f"The new AP is a {new_ap_data['product_type']} but the old device was a {ap_data['ap_model']}. Script is exiting...")
        raise SystemExit
    # Get the device id for the new ap
    new_ap_id = new_ap_data['id']
    # rename the new AP
    response = renameAP(new_ap_id, ap_data['ap_name'])
    if response != "Success":
        print(f"Failed to change name of {new_ap_id}")
        replaceSuccess = False
    else:
        print(response)
    # Set the location of the new AP
    response = changeAPLocation(new_ap_id, ap_data['location'])
    if response != "Success":
        print(f"Failed to set location of {new_ap_id}")
        replaceSuccess = False
    else:
        print(response)
    # Set the network policy of the new AP
    response = changeAPNetworkPolicy(new_ap_id,ap_data['network-policy'])
    if response != "Success":
        print(f"Failed to set the network-policy of {new_ap_id}")
        replaceSuccess = False
    else:
        print(response)
    # check if everything has worked so far
    if replaceSuccess:
        # delete the old AP
        deleteAP(apid)
        if response != "Success":
            print(f"Failed to delete {apid} from XIQ!")
        else:
            print(response)
    else:
        print(f"Because of the above error, the script will not delete AP {apid}")


if __name__ == '__main__':
	main()