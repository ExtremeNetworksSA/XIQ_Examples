# XIQ Device Inventory
### XIQ_Device_Inventory.py
## Purpose
This script will collect all API device info and save it to a csv file. This can be scheduled as a cron job and ran as frequently as needed. The CSV file will contain the date in the name of the file.

## User Input Data
##### lines 9-10
uncomment, enter XIQ credentials, and comment line 13
```
#XIQ_username = "enter your ExtremeCloudIQ Username"
#XIQ_password = "enter your ExtremeCLoudIQ password"
```
or 
##### line 13
change to a valid token
```
XIQ_token = "****"
```
A token can be generated using the POST /auth/apitoken with the "device:list" permissions set in the body. This can be done from the [Swagger page](https://api.extremecloudiq.com/swagger-ui/index.html?configUrl=/openapi/swagger-config&layout=BaseLayout#/Authorization/generateApiToken).

More information can be found in this [Getting Started Guide](https://extremeportal.force.com/ExtrArticleDetail?an=000102173).


## Running the script
open the terminal to the location of the script and run this command.

```
python XIQ_Device_Inventory.py
```
## CSV file
upon running the script a csv file file will be created with the current date in the name followed by _XIQ_Inventory.csv. ie. 2023_01_05_XIQ_Inventory.csv. If a csv file already exists with that name if will be written over.

## Log file
upon running the script a XIQ-Inventory.log file will be create. This log file will contain the amount of devices discovered each run. It will also contain information about any errors that may occur. Once the file is created by the script, the script will append to it for any additional runs.

## Requirements
The following modules will need to be installed in order for the script to run.
```
requests
pandas
```
