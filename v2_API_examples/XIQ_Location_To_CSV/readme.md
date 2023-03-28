# XIQ Location Tree to CSV
### xiq_location_export_to_csv.py

## Purpose

This script can be used to export location information to a csv file. This file is for reference only! You will not be able to import this location information to a VIQ with any current scripts. If this is something that you are interested please submit a feature request and an import script can be created.
Each line of the csv will contain a unique location element. The included information will be the id of the location, created time, updated time, org id, the id of the parent location, the name of the location, the unique XIQ name of the location, the type of location (location, building, or floor), and the address of the location.

## Running the script

When running the script, a prompt will display asking for XIQ user credentials. 
```
Enter your XIQ login credentials
Email: tismith+api@extremenetworks.com
Password: 
Logged in and Got access token
```
After logging in with your XIQ credentials the script will check if the user has access to any external accounts. If the user has access to external account the script will give a numeric option of each of the XIQ instances the user has access to. Choose the one you would like to use.

```
Which VIQ would you like to export the location tree from?
   0. BMAT_JP_Lab
   1. BMAT_va2_Lab
   2. SCS
   3. BMAT_TIM_Lab (This is Your main account)

Please enter 0 - 3: 
```
> NOTE: The user must have Administrator or Operator role in the logged in VIQ to be able to switch to another account. If you attempt with a user of a different role you will receive an Access Denied message, even tho the user has been granted external access

If the user does not have any external access the script will continue using the users VIQ.

The script will begin to collect all of the location information for the selected VIQ. 
A message will appear
```
Gathering Locations...
```
with .'s continuing until all location elements are collected. The larger the location tree the longer this process will take.
Once all the location elements are collected, the a new message will appear.
```
...Completed
```

At this point the script will create the CSV file. The CSV file's name will be derived from the name configured for the Global view.

For example if the name is 'Tim LAB' the file name will be 'Tim LAB_export.csv'

## requirements

There are additional modules that need to be installed in order for this script to function. They are listed in the requirements.txt file and can be installed with the command 'pip install -r requirements.txt' if using pip.