# XIQ Collecting Client Count per SSID
## XIQ_Clients_per_SSID_capture.py
### Purpose
This script will collect the number of clients connected to each SSID per hour over the last 24 hours. The amount of times data is collected can be adjusted but default is set to collect every hour. This data is stored in a json file. The script also exports the data to an excel file.
### User Input Data
interation_hours (default 1 hour). This is how frequently the script will pull data

totalretries (default 5). This is how many times the API calls will retry before skipping

###### lines 23-24
```
iteration_hours = 1
totalretries = 5
```
API info.

###### lines 27-32
```
CLIENTID = 'e4aac13f'
SECRET = '6593120f5e4360af47918d70c8df9924'
REDIRECT_URI = 'https://bmatwifi.com'
TOKEN = '7FKFvMHIWvOa2IEceBrNJ_RC_b01-k1pe4aac13f'
ownerId = '10100'
DATACENTER = 'ava'
```
#### Optional: 
pagesize (default is ''). This allows the page size of the API call to be adjusted from the default 500 clients. Added desired number between the ''. (ie '100' for 100 clients per call)

###### line 48
```
pagesize = ''
```

### More information
This script will use the current UTC time and collect client counts per SSID over the last 24 hours. collection is done every hour but this can be adjusted by changing the iteration_hours variable. 

The output of the script will be a *_data.json file. The file name will include the current data and time. so for example if the script was ran on Nov 23, 2020 at 5pm the file name would be 112320_1700_data.json.

in addition to client info the initial API call will return the total number of clients as well as how many clients were included in this AP call. The default will only return the first 500 clients but that can be adjusted (preferably lower) with the pagesize variable. Using the total number of clients from this AP call this script will calculate how many pages of API calls will need to be made to collect all the client information. API urls are built and the information collected. 

At the end of each iteration the script will write all data collected to the json file. So iteration 2 will write over the json file at the end of iteration 2 and will include all data from iteration 1 and 2. 


### API Collection and Errors
Any API call that fails will log an error message on a log file XIQ_CPS_Capture.log. 
```
2020-11-24 11:34: root - ERROR - 2020-11-24_1600 - API failed with unknown API error:
 	https://ava.extremecloudiq.com/xapi/v1/monitor/clients?ownerId=94009&startTime=2020-11-23T16:00:00.000Z&endTime=2020-11-23T17:00:00.000Z&page=2
```

If the script tries and fails 5 times during the intial call of a time iteration the script will bypass that time iteration and move to the next. 
```
2020-11-24 11:34: root - ERROR - 2020-11-24_1600 - API failed attempt 4 of 5 with unknown API error:
 	https://ava.extremecloudiq.com/xapi/v1/monitor/clients?ownerId=94009&startTime=2020-11-24T05:00:00.000Z&endTime=2020-11-24T06:00:00.000Z
2020-11-24 11:34: root - WARNING - API call has failed more than 5 times: https://ava.extremecloudiq.com/xapi/v1/monitor/clients?ownerId=94009&startTime=2020-11-24T05:00:00.000Z&endTime=2020-11-24T06:00:00.000Z
```

If the script fails on one of the pagination API calls the script will automatically try after all other pages of the iteration have finished. These failed API calls will try again for the configured number of times in the totalretries
```
There were 6 API calls that failed 1 times(s)

Attempting retry 1 of 6: Failed - see log file for details
Attempting retry 2 of 6: Successful
Attempting retry 3 of 6: Successful
```


## Historical_XIQ_Clients_per_SSID_capture.py
This script is located in the Historical Data folder
### Purpose
This script will collect the number of clients connected to each SSID per hour over a user defined beginning and end time. The amount of times data is collected can be adjusted but default is set to collect every hour. This data is stored in a json file. The script also exports the data to an excel file.
### User Input Data
API_start_time (Zulu format). Set the time to start collecting data

API_end_time (Zulu format). Set the time to end collecting data

interation_hours (default 1 hour). This is how frequently the script will pull data

totalretries (default 5). This is how many times the API calls will retry before skipping

###### lines 15-16
```
API_start_time = '2020-11-1T18:00:00.000Z'
API_end_time = '2020-11-20T18:00:00.000Z'
```
###### lines 23-24
```
iteration_hours = 1
totalretries = 5
```
API info.

###### lines 27-32
```
CLIENTID = 'e4aac13f'
SECRET = '6593120f5e4360af47918d70c8df9924'
REDIRECT_URI = 'https://bmatwifi.com'
TOKEN = '7FKFvMHIWvOa2IEceBrNJ_RC_b01-k1pe4aac13f'
ownerId = '10100'
DATACENTER = 'ava'
```
#### Optional: 
pagesize (default is ''). This allows the page size of the API call to be adjusted from the default 500 clients. Added desired number between the ''. (ie '100' for 100 clients per call)

###### line 48
```
pagesize = ''
```

## XIQ_json_to_csv.py <filename>
This script loads a json file generated by one of the XIQ scripts above and converts it to an excel sheet
### Purpose
Converts the json file to an easy human readable excel file

### User Input Data
For this script user input is added as an arguement when running the script. When calling the script the json file needs to be added.
```
python XIQ_json_to_csv.py 2020-11-24_1600_data.json
```
### More information
When the script runs it will look for that file in the same folder the script is in. If it cannot find that file it will print a message and exit out. If the file is found the data will be parsed and printed to an excel sheet. The excel file will be saved with the same name as the json file but will have the .xlsx extension