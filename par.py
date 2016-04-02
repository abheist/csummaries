import csv
import json
import re
import os
import sys
import SimpleHTTPServer
import SocketServer


# Parsing data to write in csv
def data_parser(text, dic):
	for i, j in dic.iteritems():
		text = text.replace(i,j)
	return text


# Download web pages
def get_page(url):
	try:
		import urllib
		return urllib.urlopen(url).read()
	except Exception, e:
		raise " "

fieldnames=["weather", "location", "year", "jan", "feb", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december", "winter", "spring", "summer", "autumn", "annual"]


# Get the next link from the page provided by get_all_links()
def get_next_link(page):
	start_link = page.find('<a href')
	if start_link == -1:
		return None, 0
	start_quote = page.find('"', start_link)
	end_quote = page.find('"', start_quote + 1)
	url = page[start_quote + 1 : end_quote]
	return url, end_quote


# Get all links from the web page provided
def get_all_links(page):
	links = []
	while True:
		url, endpos = get_next_link(page)
		if url:
			links.append(url)
			page = page[endpos:]
		else:
			break
	return links


# Get the full structured list
def get_full_list():
	full_page = get_page('http://www.metoffice.gov.uk/climate/uk/summaries/datasets')
	start_page = full_page.find('<a id="Yearorder"></a>')
	full_page = full_page[start_page:]
	all_links = get_all_links(full_page)
	all_region = [
				['uk', #0,0
					[['max'],['min'],['mean'],['sunshine'],['rainfall']] #0,1
				],
				['england', #1,0
					[['max'],['min'],['mean'],['sunshine'],['rainfall']] #1,1
				],
				['wales', #2,0
					[['max'],['min'],['mean'],['sunshine'],['rainfall']] #2,1
				],
				['scotland', #3,0
					[['max'],['min'],['mean'],['sunshine'],['rainfall']] #3,1
				]
		   	 ]
	i = 0
	j = 0
	k = 0
	while True:
		if k > 25:
			break
		if j < 5:
			all_region[i][1][j].append(all_links[k])
			k = k + 1
			j = j + 1
		else:
			k = k + 2
			i = i + 1
			j = 0

	return all_region


# Converts CSV file to json
def convert2json(filename):
	print "Generating weather.json from weather.csv"
  	csv_filename = filename
  	f=open(csv_filename, 'r')
  	csv_reader = csv.DictReader(f,fieldnames)
  	json_filename = csv_filename.split(".")[0]+".json"  
  	jsonf = open(json_filename,'w')
  	data = json.dumps([r for r in csv_reader])
  	jsonf.write(data)
  	f.close()
  	jsonf.close()
  	print "file generated"


# Writing data from txt file to csv
def each_file(input_file, output_file, weather_type, location, first_file):
	inputfile = open(input_file)
	outputfile = open(output_file, 'a+')

	reps = {'"NAN"':'N/A', '"':'', '0-':'0,','1-':'1,','2-':'2,','3-':'3,','4-':'4,','5-':'5,','6-':'6,','7-':'7,','8-':'8,','9-':'9,', ' ':',', ':':',' }
	if first_file == 0:
		for i in range(6): inputfile.next()
	else:
		for i in range(8): inputfile.next()
	count = 0
	for line in inputfile:
		line = re.sub(' +',' ',line)
		if count == 0 and first_file == 0:
			outputfile.writelines(data_parser(line, reps) + 'Weather, Location, ')
			count = count + 1
		else:
			outputfile.writelines(data_parser(line, reps) + weather_type + location)
	inputfile.close()
	outputfile.close()


# automate the task of making all txt files and csv file
def every_file_csv():
	# file_list = []
	if os.path.isfile("weather.csv"):
		os.remove("weather.csv")
	output_file = 'weather.csv'
	link_list = get_full_list()
	link_len = len(link_list)
	first_file = 0
	for x in range(link_len):
		for y in xrange(5):
			file_name = link_list[x][0]+"_"+link_list[x][1][y][0]+'.txt'
			print "- Downloading " + file_name
			open_file = open(file_name, 'w')
			web_string = get_page(link_list[x][1][y][1])
			open_file.write(web_string)
			print file_name + " downloaded"
			each_file(file_name, output_file, link_list[x][1][y][0]+',', link_list[x][0]+',', first_file)
			first_file = first_file + 1
			open_file.close()
	print "Weather.csv generated"


# Copying weather.json to angular's data directory for front-end use
def movejson():
	print "copying weather.json to climate/app/data for angularJS"
	input_file = open("weather.json")
	output_file = open("app/data/weather.json", "w")
	for line in input_file:
		output_file.writelines(line)
	input_file.close()
	output_file.close()
	print "file copied"


try:
	every_file_csv()
except Exception, e:
	raise "Please try after some time, at this particular period of time site is not working. Site is returning dataset file."
convert2json("weather.csv")
movejson()
print "Now run angularJS"
print "Now please, Run server in 'app' directory.."