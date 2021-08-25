#!/usr/bin/env python3
import json
import os
import pandas
import argparse
import re
from app.XIQ_csv_converter import jsontoexcel


PATH = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser() 
parser.add_argument('jsonfile')
args = parser.parse_args()
filename = "{0}".format(args.jsonfile)

def main():
	if not os.path.exists(filename):
		print(f"failed to open file {filename}")
		exit()
	else:
		with open('{}/{}'.format(PATH, filename), 'r') as f:
			try:
				data = json.load(f)
			except ValueError:
				data = {}
	excelfilename = filename.replace('json', 'xlsx')
	jsontoexcel(data, PATH, excelfilename)

if __name__ == '__main__':
	main()