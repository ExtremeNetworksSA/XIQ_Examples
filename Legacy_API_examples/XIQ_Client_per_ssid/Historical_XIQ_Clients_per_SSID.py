#!/usr/bin/env python3
import requests
import json
import math
import time
import os
import datetime
import pytz
import logging
from pytz import timezone
from requests.exceptions import HTTPError
from app.XIQ_csv_converter import jsontoexcel

UTC = pytz.utc
timzoneadjust = timezone('US/Eastern')

PATH = os.path.dirname(os.path.abspath(__file__))

# Used to setting times in API call
# Please enter time in Zulu format
API_start_time = '2020-11-1T18:00:00.000Z'
API_end_time = '2020-11-2T18:00:00.000Z'

#converting time string into time format
API_start_time = datetime.datetime.strptime(API_start_time, '%Y-%m-%dT%H:%M:%S.000Z').replace(tzinfo=UTC)
API_end_time = datetime.datetime.strptime(API_end_time, '%Y-%m-%dT%H:%M:%S.000Z').replace(tzinfo=UTC)

# User variables
iteration_hours = 1
totalretries = 5

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


# Global Objects
ssidlist = {}
secondtry = []
pagesize = '' #Value can be added to set page size. If nothing in quotes default value will be used (500)

# logging for any API ERRORs
logging.basicConfig(
	filename='{}/Historical_XIQ_CPS_Capture.log'.format(PATH),
	filemode='a',
	level=os.environ.get("LOGLEVEL", "INFO"),
	format= '{}: %(name)s - %(levelname)s - %(message)s'.format(time.strftime("%Y-%m-%d %H:%M"))
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
				failmsg = (f"Status Code {data['error']['status']}: {data['error']['message']}")
				raise TypeError(f"API Failed with reason: {failmsg} - on API {url}")
		return data

#builds a dictionary of SSIDs with a list of connected clientId. This is then later used to get the count of clients connected to the SSID
def clientCount(data):
	global ssidlist
	for client in data['data']:
		if client['ssid'] not in ssidlist:
			ssidlist[client['ssid']]=[]
		if client['clientId'] not in ssidlist[client['ssid']]:
			ssidlist[client['ssid']].append(client['clientId'])
		
	
def main():
	global today
	global API_start_time
	global secondtry
	global ssidlist


	filenamedate = timzoneadjust.normalize(API_start_time)
	filenamedate = filenamedate.strftime('%Y-%m-%d_%H00')
	
	ssid_dic = {}
	
	# loops until API_start_time (current time - 1 day) equals current time. At the end of the loop 1 hour is added to API_start_time
	while API_end_time > API_start_time:
		# gets the startTime in correct format to be added to the API call
		startTime = API_start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
		# adjusts time for user readable timezone - line 14
		adjustedtime = timzoneadjust.normalize(API_start_time)
		adjustedtime = adjustedtime.strftime('%Y-%m-%d %H:%M:%S %Z%z')
		# gets the endTime in correct format to be added to the API call
		endTime = API_start_time + datetime.timedelta (hours=iteration_hours)
		endTime = endTime.strftime('%Y-%m-%dT%H:%M:%S.000Z')
		print(f"collecting client data for {adjustedtime}")
		# adds the base url info as well as the startTime and endTime to the url
		url = "{}/xapi/v1/monitor/clients?ownerId={}&startTime={}&endTime={}".format(baseurl, ownerId, startTime, endTime)

		# default values for next while loop
		pageCount = 0
		success = 0 
		
		# initial API call will try 5 times and if fails script will terminate.
		for count in range(1, totalretries):
			print(f"Initial API call attempt {count} of {totalretries}", end=': ')		
			try:
				data = get_api_call(url)
			except TypeError as e:
				logging.error(f"{filenamedate} - API failed attempt {count} of {totalretries} with error {e}")
				print("Failed - see log file for details")
				count+=1		
			except HTTPError as e:
				logging.error(f"{filenamedate} - API failed attempt {count} of {totalretries} with error {e}")
				print("Failed - see log file for details")		
				count+=1
			except:
				logging.error(f"{filenamedate} - API failed attempt {count} of {totalretries} with unknown API error:\n 	{url}")
				print("Failed - see log file for details")		
				count+=1
			else:
				print("Successful Connection")
				success = 1
				break

		if success != 1:
			logging.warning(f"API call has failed more than {totalretries} times: {url}\n")
			logging.info(f"No data was collected for {API_start_time}\n")
			print(f"Skipping {API_start_time}")
			API_start_time = API_start_time + datetime.timedelta (hours=iteration_hours)
			continue
		
		# gets total count of clients and the count of clients in the initial call
		totalCount = data['pagination']['totalCount']
		countInPage = data['pagination']['countInPage']
		clientCount(data)
		# checks to see if client info is missing from initial call
		if countInPage < totalCount:
			# calculates the number of pages needed to get all client info (rounded up)
			pageCount = math.ceil(int(totalCount)/int(countInPage))
			for page in range(1, int(pageCount)):
				pagedurl = '{}&page={}'.format(url, page)
				try:
					data = get_api_call(pagedurl,page=page,pageCount=pageCount)
				except TypeError as e:
					logging.error(f"{filenamedate} - API failed with error {e}")
					print(f"Failed page {page} - see log file for details")		
					secondtry.append(pagedurl)
					continue
				except HTTPError as e:
					logging.error(f"{filenamedate} - API failed with error {e}")
					print(f"Failed page {page}- see log file for details")		
					secondtry.append(pagedurl)
					continue
				except:
					logging.error(f"{filenamedate} - API failed with unknown API error:\n 	{pagedurl}")
					print(f"Failed page {page} - see log file for details")		
					secondtry.append(pagedurl)
					continue
				print("successful")
				clientCount(data)
		
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
						logging.error(f"{filenamedate} - API failed retry attempt with error {e}:\n	{url}")
						print("Failed - see log file for details")
					except HTTPError as e:
						apicallcount+=1
						logging.error(f"{filenamedate} - API failed retry attempt with error {e}:\n	{url}")
						print("Failed - see log file for details")
					except:
						apicallcount+=1
						logging.error(f"{filenamedate} - API failed attempt {count} of {totalretries} with unknown API error:\n 	{url}")
						print("Failed - see log file for details")
					else:
						apicallcount+=1
						removelist.append(url)
						clientCount(data)
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


		# adds a dictionary inside of ssid_dic with the value of the startTime
		ssid_dic[adjustedtime]={}
		for ssid in ssidlist:
			# adds each ssid and the count of clients into the startTime dictionary
			ssid_dic[adjustedtime][ssid]= len(ssidlist[ssid])
 
		# over writes the json file with the collected data which includes:
		### all data from previous API_start_time values while the script has been running
		### current API_start_time data
		with open('{}/{}_data.json'.format(PATH,filenamedate), 'w') as f:
			json.dump(ssid_dic, f)

		print(f"completed capture at {adjustedtime}\n")
		
		# adds hour iteration to the API_start_time for the next loop
		API_start_time = API_start_time + datetime.timedelta (hours=iteration_hours)
		# empties the secondtry list for the next loop
		secondtry = []
		ssidlist = {}

	#print(ssid_dic)
	#Export data to excel file
	excelfilename = (f'{filenamedate}_data.xlsx')
	jsontoexcel(ssid_dic, PATH, excelfilename)

if __name__ == '__main__':
	main()
