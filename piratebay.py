#!/usr/bin/env python
from bs4 import BeautifulSoup
from time import gmtime, strftime
import os
import sqlite3
import urllib.request
import re
import json
from sys import exit
import httplib2
from json import dumps

#change this to correct directory
serie_directory='/mnt/hdd2/series/'

#get current date in strong format
today=strftime("%Y-%m-%d", gmtime())
today =today.split('-')
today[-1] = str(int(today[-1])-1)
today = '-'.join(today)

#change to right directory
os.chdir(serie_directory)
#check if outputfile exist:
if not os.path.isfile('outputfile'):
    print("outputfile doesn't exist!")
    exit(1)
#outputfile contains serie python script
with open('outputfile') as data_file:    
    data = json.load(data_file)
if not os.path.isfile('series.db'):
    print("series database doesn't exist")
    exit(1)

conn = sqlite3.connect('series.db')
c = conn.cursor()
#can't handle multiple series/episodes yet
#you can change this line if you want to run test for a certain date
#replace today with string date (YYYY-MM-DD)
store = []
for row in c.execute("SELECT * FROM series WHERE date='%s'" %  today):
    store.append(row)
conn.commit()
conn.close()
#check if there needs to be a download today, otherwise exit
if not store:
    print("no series today")
    exit(1)
for item in range(0,len(store)):
    for location in data:
        if store[item][1] == location['Title']:
            store[item] = store[item] + (location['Directory'],)
with open('to_download', 'a') as fout:
    json.dump(store, fout)

for i in store:
    search_query = i[1]
    r = urllib.request.urlopen("https://thepiratebay.se/search/"+search_query+"/0/99/200").read()
    soup = BeautifulSoup(r,'lxml')
    def magnet_url():
        for x,y in zip(soup.find_all("a",class_="detLink"),soup.find_all("a",title="Download this torrent using magnet")):
            x = x.get_text()
            output = [int(s) for s in re.findall(r'[1-9]+', x)]
            if output[0] == i[2] and output[1] == i[3]:
                print("match found: %s" % x)
                return(y['href'])
        return None
    magnet = magnet_url()
    if magnet == None:
        print("download %s not available on thepiratebay" % i[1])
    else:
        url = 'http://192.168.0.12:9091/transmission/rpc'
        h = httplib2.Http(".cache")
        resp, content = h.request(url, "GET")
        headers = { "X-Transmission-Session-Id": resp['x-transmission-session-id'] }
        body = dumps( { "method": "torrent-add",
                "arguments": { "filename": magnet } } )
        response, content = h.request(url, 'POST', headers=headers, body=body)
        if str(content).find("success") == -1:
            print("Magnet Link: " + magnet)
            print("Answer: " + content)
            print("No 'success' here!")
#re.findall(r'\d+', x)
#[int(s) for s in re.findall(r'\d+', x)]

