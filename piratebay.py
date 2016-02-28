#!/usr/bin/env python
from io import BytesIO
import gzip
import logging
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
from setting import serie_dir,output_path
#change this to correct directory
logging.basicConfig(filename=output_path+'download.log', level=logging.INFO)

#get current date in strong format
current_date=strftime("%Y-%m-%d", gmtime())
today =current_date.split('-')
today[-1] = str(int(today[-1])-1)
today = '-'.join(today)

#check if outputfile exist:
if not os.path.isfile(output_path+'outputfile'):
    print("outputfile doesn't exist!")
    logging.error("output file doesn't exist")
    exit(1)
#outputfile contains serie python script
with open(output_path+'outputfile') as data_file:    
    data = json.load(data_file)
if not os.path.isfile(output_path+'series.db'):
    print("series database doesn't exist")
    logging.error("series database doesn't exist")
    exit(1)

conn = sqlite3.connect(output_path+'series.db')
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
    logging.info("no series to download, date: " + current_date)
    exit(1)
for item in range(0,len(store)):
    for location in data:
        if store[item][1] == location['Title']:
            store[item] = store[item] + (location['Directory'],)
with open(output_path+'to_download', 'a') as fout:
    json.dump(store, fout)

for i in store:
    def magnet_url():
        search_query = i[1]
        r = urllib.request.urlopen("https://thepiratebay.se/search/"+search_query+"/0/99/200").read()
        soup = BeautifulSoup(r,'lxml')
        for x,y in zip(soup.find_all("a",class_="detLink"),soup.find_all("a",title="Download this torrent using magnet")):
            x = x.get_text()
            output = [int(s) for s in re.findall(r'[1-9]+', x)]
            if output[0] == i[2] and output[1] == i[3]:
                print("match found: %s" % x)
                return(y['href'])
        search_query= re.sub(r"\s+", '%20', search_query)
        request = urllib.request.Request('https://kat.cr/usearch/'+search_query+'/')
        request.add_header('Accept-encoding', 'gzip')
        response = urllib.request.urlopen(request)
        if response.info().get('Content-Encoding') == 'gzip':
            buf = BytesIO( response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        soup = BeautifulSoup(data,'lxml')
        for x,y in zip(soup.find_all("a",class_="cellMainLink"),soup.find_all("a",title="Download torrent file")):
            x = x.get_text()
            print("i get here too")
            output = [int(s) for s in re.findall(r'[1-9]+', x)]
            if output[0] == i[2] and output[1] == i[3]:
                print("match found on kickass: %s" % x)
                logging.info("match found on kickass: %s" % x)
                print(y['href'].split('.torrent')[0]+'.torrent')
                return("http:"+y['href'].split('.torrent')[0]+'.torrent')
        return None
    magnet = magnet_url()
    if magnet == None:
        print("download %s not available on thepiratebay" % i[1])
        logging.info("download %s not available on the TPB" % i[1])
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
            #print("Answer: " + content)
            print("No 'success' here!")
#re.findall(r'\d+', x)
#[int(s) for s in re.findall(r'\d+', x)]

