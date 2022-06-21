# XIQ - Replace AP
## XIQ_Replace_AP.py
### Purpose
First this script will copy the name, location info, and network policy from an AP. Next it will onboard a new AP, apply the name, location info, and network policy from the old AP. Lastly, it will remove the old AP from XIQ

## User Input Data
##### line 11
```
Old_AP_Name = 'Enter the name of the old AP'
```
Enter the name of the AP you would like to replace
##### line 13
```
new_AP_SN = 'Enter serial number of the new AP'
```
Enter the serial number of the new AP
##### line 19
```
XIQ_token = "****"
```
A token can be generated using the POST /auth/apitoken with the "device" and "device:list" permissions set in the body. This can be done from the [Swagger page](https://api.extremecloudiq.com/swagger-ui/index.html?configUrl=/openapi/swagger-config&layout=BaseLayout#/Authorization/generateApiToken).

Documentation on generating tokens can be found on [Extreme Portal](https://extremeportal.force.com/ExtrArticleDetail?an=000102173)

## Notes
 - This script will not pull any device template overrides that may be applied to a device. 
 - This script will stop if there are more than 1 device with the same name
 - This script will stop if the device type of the new AP doesn't match the old device
 - If any of the API's fail to apply to the new device the old device will not be deleted and may have to be deleted manually

## Requirements
The following modules will need to be installed in order for the script to run.
```
requests
```