#!/usr/bin/env python3
import json
import os
import pandas
import argparse
import re


def clientperssid(data):
	ssidlist = []
	for timestamp in data:
		for ssid in data[timestamp]:
			if ssid not in ssidlist:
				ssidlist.append(str(ssid))
	if ssidlist:
		ssidlist.sort()
		msg='TIME'
		for ssid in ssidlist:
			msg += (f"/,/ {ssid}")
		msg += ("\n")
		for timestamp in data:
			msg += (f"{timestamp}")
			for ssid in ssidlist:
				if ssid in data[timestamp]:
					msg += (f"/,/ {int(data[timestamp][ssid])}")
				else:
					msg += ("/,/ ")
			msg += ("\n")
		return(msg)
	else:
		print("Failed to load data in Excel converter")
		exit()
def jsontoexcel(data, PATH, excelfilename):

	cpssid_msg = clientperssid(data)
	cpssid_data = pandas.DataFrame([sub.split("/,/") for sub in cpssid_msg.splitlines()])
	
	# Create a Pandas Excel writer using XlsxWriter as the engine
	writer = pandas.ExcelWriter('{}/{}'.format(PATH, excelfilename), engine='xlsxwriter')
	
	# Create Sheets
	sheets = ['Clients per SSID']
	# Write each dataframe to a different worksheet
	try:
		cpssid_data.to_excel(writer, sheet_name=sheets[0], index=False, header=False)
	except NameError:
		print("There was no SSID info")
	except:
		print("Clients per SSID incountered an Unknown error")
	
	# Close the Pandas Excel writer and output the Excel file
	writer.save()
	print(f"Successfully wrote data to {excelfilename}")
