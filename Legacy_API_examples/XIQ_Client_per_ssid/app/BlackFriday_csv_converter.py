#!/usr/bin/env python3
import json
import os
import pandas
import argparse
import re

# Create Sheets - these will be unique per ssid
sheets = []

def clientinfoperssid(data):
	msg="Client Mac/,/Start Time/,/End Time/,/Iteration Time\n"
	for client in data:
		msg += (f"{data[client]['clientmac']}/,/{data[client]['sessionStart']}/,/{data[client]['sessionEnd']}/,/{data[client]['iteration']}\n")
	return(msg)

def jsontoexcel(data, PATH, excelfilename):
	global sheets
	pandadic = {}
	for ssid in data:
		sheets.append(ssid)
		pandadic[ssid] = {}
		clientinfo_msg = clientinfoperssid(data[ssid])
		pandadic[ssid]['clientinfo_data'] = pandas.DataFrame([sub.split("/,/") for sub in clientinfo_msg.splitlines()])
	
	# Create a Pandas Excel writer using XlsxWriter as the engine
	writer = pandas.ExcelWriter('{}/{}'.format(PATH, excelfilename), engine='xlsxwriter')
	for ssidcount in range(len(sheets)):
		# Write each dataframe to a different worksheet
		try:
		#if 'BLOOMINGDALESFREEWIFI' in sheets[ssidcount]:
			pandadic[sheets[ssidcount]]['clientinfo_data'].to_excel(writer, sheet_name=sheets[ssidcount], index=False, header=False)
			print(f"Successfully wrote client info for SSID {sheets[ssidcount]}")
		except NameError:
			print(f"There was no SSID info for {sheet[ssidcount]}")
		except:
			print(f"Clients per SSID incountered an Unknown error for SSID {sheets[ssidcount]}")
	
	# Close the Pandas Excel writer and output the Excel file
	writer.save()
	print(f"Successfully wrote data to {excelfilename}")