#!/usr/bin/env python3
import requests
import json
import math
import os
import logging
import math
from requests.exceptions import HTTPError


PATH = os.path.dirname(os.path.abspath(__file__))



# User variables
totalretries = 3
findapps = ['YOUTUBE','NETFLIX']
# Used to setting times in API call
# Please enter time in Zulu format
startTime = '2021-08-20T19:00:00.000Z'
endTime = '2021-08-25T19:00:00.000Z'


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
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }


# Global Objects
client_info = {}
found_clients = {}
secondtry = []
clientsWithNoData = 0 
wiredClients = 0
pagesize = '' #Value can be added to set page size. If nothing in quotes default value will be used (500)
filename = ('Test.csv')


# logging for any API ERRORs
logging.basicConfig(
    filename='{}/Application_Search.log'.format(PATH),
    filemode='a',
    level=os.environ.get("LOGLEVEL", "INFO"),
    format= '%(asctime)s: %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)


# used for debuging
def debug_print(msg):
    print(msg)
    #lines = msg.splitlines()
    #for line in lines:
    #	logging.info(msg)


# function that makes the API call with the provided url
# if pageCount is defined (all calls per hour after initial call) if the call fails they will be added to the secondtry list 
def get_api_call(url, page=0, pageCount=0):
    ## used for page if pagesize is set manually
    if pagesize:
        url = "{}&pageSize={}".format(url, pagesize)
    ## the first call will not show as the data returned is used to collect the total count of Clients which is used for the page count
    #print(f"####{url}####")
    if pageCount != 0:
        print(f"API call on page {page} of {pageCount-1}", end=": ")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except HTTPError as http_err:
        if pageCount != 0:
            secondtry.append(url)
        raise HTTPError(f'HTTP error occurred: {http_err} - on API {url}')  
    except Exception as err:
        if pageCount != 0:
            secondtry.append(url)
        raise TypeError(f'Other error occurred: {err}: on API {url}')
    else:
        data = json.loads(r.text)
        if 'error' in data:
            if data['error']:
                print(data['error'])
                if data['error']['status'] and data['error']['message']:
                    failmsg = (f"Status Code {data['error']['status']}: {data['error']['message']}")
                elif data['error']['status'] and data['error']['code']:
                    failmsg = (f"Status Code {data['error']['status']}: {data['error']['code']}")
                    print(failmsg)
                else:
                    print('failed here')
                raise TypeError(f"API Failed with reason: {failmsg} - on API {url}")
        return data


def buildBasicClient(data):
    global client_info
    global clientsWithNoData
    global wiredClients
    for client in data['data']:
        clid = client['clientId']
        if clid in client_info:
            logging.error(f"Client {clid} is already in client_info dictionary. Adding with override existing values \nFirst\n starttime: {client_info[clid]['startTime']}\n {client_info[clid]['endTime']} \nNow\n starttime: {client['startTime']}\n {client['endTime']}")
        if 'WIRED' in client['connectionType']:
            logging.info(f"Client {clid} is {client['connectionType']} device. So wont be tracked.")
            wiredClients += 1
            continue
        if client['usage'] > 1:
            client_info[clid] = {}
            client_info[clid]['userName'] = client['userName']
            #client_info[clid]['userName'] = client['hostName']
            client_info[clid]['mac'] = client['clientMac']
            #logging.info(f"collected data for client {clid}")
        else:
            clientsWithNoData += 1
            logging.info(f"Client {clid} showed {client['networkHealth']} for its network health, with 0 usage.")

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def gatherClientInfo():
    global client_info
    global secondtry
    global wiredClients
    global clientsWithNoData

    #url = "{}/xapi/v1/monitor/clients?ownerId={}".format(baseurl, ownerId)
    url = "{}/xapi/v1/monitor/clients?ownerId={}&startTime={}&endTime={}".format(baseurl, ownerId, startTime, endTime)
    # default values for next while loop
    pageCount = 0
    success = 0 
    for count in range(1, totalretries):
        print(f"Initial API call attempt {count} of {totalretries}", end=': ')		
        try:
            data = get_api_call(url)
        except TypeError as e:
            logging.error(f"API failed attempt {count} of {totalretries} with error {e}")
            print("Failed - see log file for details")
        except HTTPError as e:
            logging.error(f"API failed attempt {count} of {totalretries} with error {e}")
            print("Failed - see log file for details")		
        except:
            logging.error(f"API failed attempt {count} of {totalretries} with unknown API error:\n 	{url}")
            print("Failed - see log file for details")		
        else:
            print("Successful Connection")
            success = 1
            break
    if success != 1:
        logging.warning(f"API call has failed more than {totalretries} times: {url}\n")
        logging.info(f"No data was collected for {startTime}\n")
        print(f"Skipping {startTime}")
        exit()	
    
    # gets total count of clients and the count of clients in the initial call
    totalCount = data['pagination']['totalCount']
    countInPage = data['pagination']['countInPage']
    print(f"Total number of clients that should be collected {totalCount}")
    buildBasicClient(data)
    
    # checks to see if client info is missing from initial call
    if countInPage < totalCount:
        # calculates the number of pages needed to get all client info (rounded up)
        pageCount = math.ceil(int(totalCount)/int(countInPage))
        for page in range(1, int(pageCount)):
            pagedurl = '{}&page={}'.format(url, page)
            try:
                data = get_api_call(pagedurl,page=page,pageCount=pageCount)
            except TypeError as e:
                logging.error(f"API failed with error {e}")
                print(f"Failed page {page} - see log file for details")		
                secondtry.append(pagedurl)
                continue
            except HTTPError as e:
                logging.error(f"API failed with error {e}")
                print(f"Failed page {page}- see log file for details")		
                secondtry.append(pagedurl)
                continue
            except:
                logging.error(f"API failed with unknown API error:\n 	{pagedurl}")
                print(f"Failed page {page} - see log file for details")		
                secondtry.append(pagedurl)
                continue
            print("successful")
            buildBasicClient(data)

    # checks if there are any API calls to try again
    if secondtry:
        retrysuccess = 0
        for retrycount in range(1, totalretries):
            removelist = []
            print(f"\nThere were {len(secondtry)} API calls that failed {retrycount} times(s)\n")
            apicallcount = 1
            for url in secondtry:
                print(f"Attempting retry {apicallcount} of {len(secondtry)}",end=": ")
                try:
                    data = get_api_call(url)
                except TypeError as e:
                    apicallcount+=1
                    logging.error(f"API failed retry attempt with error {e}:\n	{url}")
                    print("Failed - see log file for details")
                except HTTPError as e:
                    apicallcount+=1
                    logging.error(f"API failed retry attempt with error {e}:\n	{url}")
                    print("Failed - see log file for details")
                except:
                    apicallcount+=1
                    logging.error(f"API failed attempt {count} of {totalretries} with unknown API error:\n 	{url}")
                    print("Failed - see log file for details")
                else:
                    apicallcount+=1
                    removelist.append(url)
                    buildBasicClient(data)
                    print(f"Successful")
                    retrysuccess = 1

            for item in removelist:
                secondtry.remove(item) 
            if not secondtry:	
                break
        if retrysuccess != 1:
            print(f"There were {len(secondtry)} APIs that failed {retrycount} times. Check logs for details")
            logging.warning(f"These are the {len(secondtry)} APIs that failed {retrycount} times:\n")

            for url in secondtry:
                logging.info("  {url}")
    
    print(f"Total Clients collected: {len(client_info)}\nClient Count for Wired Clients: {wiredClients}\nWireless Client Count With No Data: {clientsWithNoData}")


def main():

    global client_info
    global filename
    gatherClientInfo()
    clientcount = 1
    for client in client_info:
        print(f'Client {clientcount} of {len(client_info)}', end=': ')
        url = "{}/xapi/v1/monitor/clients/{}?ownerId={}&startTime={}&endTime={}".format(baseurl, client, ownerId, startTime, endTime)
        clientcount += 1
        for count in range(1, totalretries):
            if count > 1:
                print(f"\nAPI call attempt {count} of {totalretries}", end=': ')		
            try:
                data = get_api_call(url)
            except TypeError as e:
                logging.error(f"API failed attempt {count} of {totalretries} with error {e}")
                print("Failed - see log file for details")		
            except HTTPError as e:
                logging.error(f"API failed attempt {count} of {totalretries} with error {e}")
                print("Failed - see log file for details")		
            except:
                logging.error(f"API failed attempt {count} of {totalretries} with unknown API error:\n 	{url}")
                print("Failed - see log file for details")		
            else:
                print("Successful Connection")
                success = 1
                break
        if success != 1:
            logging.warning(f"API call has failed more than {totalretries} times: {url}\n")
            logging.info(f"No data was collected for {client}\n")
            print(f"Skipping {client}")
            exit()
        #for findapp in findapps:
        if any(x in d['appName'] for d in data['data']['appUsages'] for x in findapps):
            #if any(findapp for d in data['data']['appUsages'] for x in findapps):
                found_clients[client] = client_info[client]
                #found_clients[client]['app'] = findapp
                found_clients[client]['appusage'] = data['data']['appUsages']
    for client, details in found_clients.items():
        print(f"{client}: {details}")
            
            
if __name__ == '__main__':
    main()