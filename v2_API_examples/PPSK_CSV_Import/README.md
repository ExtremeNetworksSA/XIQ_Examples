# XIQ - Add PPSK users from a CSV file
## XIQ_PPSK_CSV_Importer.py
### Purpose
This script will import a CSV file of PPSK Users and create these users on the entered the user group. Any PPSK users in the user group that is not listed in the CSV file will be removed from the user group. 

## User Input Data
##### lines 18-19
```
#XIQ_username = "enter your ExtremeCloudIQ Username"
#XIQ_password = "enter your ExtremeCLoudIQ password"
```
or 
##### line 22
```
XIQ_token = "****"
```
A token can be generated using the POST /auth/apitoken with the "enduser" permissions set in the body. This can be done from the [Swagger page](https://api.extremecloudiq.com/swagger-ui/index.html?configUrl=/openapi/swagger-config&layout=BaseLayout#/Authorization/generateApiToken).

##### line 24
```
usergroupID = "enter the user group id"
```
Each XIQ User Group will be assigned a unique ID when it gets created. This is something that gets used by the backend systems and not seen in the GUI. The easiest way to get the ID is from the [Swagger page](https://api.extremecloudiq.com/swagger-ui/index.html?configUrl=/openapi/swagger-config&layout=BaseLayout#/Configuration%20-%20User%20Management/listUserGroups). 

### Optional
##### line 26
```
filename = "PPSK_Users.csv"
```
The file name can be changed if needed.

## Log file
upon running the script a XIQ_PPSK_CSV_Importer.log file will be create. This will be a log file of all users created and deleted from the user group.

## Requirements
The following modules will need to be installed in order for the script to run.
```
requests
pandas
```