# XIQ List Open Switchports in CSV
## Open_Ports_CSV.py
### Purpose
This script will collect the current open switchports for all switches in your XIQ instance. This does require an API call per switch so the script can take longer to run if ran against a lot of switches. The script will output a CSV file listing the switch by name, model, a list the open port ranges, and a list of disabled port ranges.

### User Input Data

switch_model_list. The list of Switch Models to look for.

###### line 12 Example:
```
switch_model_list = ['X435_8P_4S','SR_2208P']
```
> Note: Only switch models SR_2148P, SR_2208P, and X435_8P_4S have been tested

totalretries (default is 5). This is the number of times each API call will retry for any failures
pagesize (default is ''). This allows the page size of the API call to be adjusted from the default 500 devices. Added desired number between the ''. (ie '100' for 100 devices per call). 
> Note: This is only used to go through all devices looking for devices that match a model in the list above.

###### lines 13-44
```
totalretries = 5
pagesize = ''
```

API info.

###### lines 17-22
```
CLIENTID = '***'
SECRET = '***'
REDIRECT_URI = '***'
TOKEN = '***'
ownerId = '***'
DATACENTER = '***'
```


### More information
This script will go through each device in the XIQ instance and build a list of devices that match a model in the user defined model list. Once that list is complete the script will make an API call per switch to get the open port ranges for each switch. The script will then build a CSV file with that information

### CSV Output

The script will output a CSV file named OpenPortList.csv. This file will list the switch by name, model, give a list the open port ranges, and then give a list of disabled port ranges.
```
Switch Name,Model,Status,Open Ports,Disabled Open Ports
SR2208P,SR_2208P,Online,5-7; 9,9
SW-X435-001,X435_8P_4S,Online,3-4; 6-7; 9-12,4
SW-X435-002,X435_8P_4S,Offline,1-7; 9-12,
```
Converted to a table would look like this.

 **Switch Name** | **Model**  | **Status** | **Open Ports** | **Disabled Open Ports** 
-----------------|------------|------------|----------------|-------------------------
 SR2208P         | SR_2208P   | Online     | 5-7; 9         | 9                       
 SW-X435-001     | X435_8P_4S | Online     | 3-4; 6-7; 9-12 | 4                       
 SW-X435-002     | X435_8P_4S | Offline    | 1-7; 9-12      |                         


