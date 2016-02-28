#!/usr/bin/env python
from bs4 import BeautifulSoup
import os
import sys
import urllib.request
import json
import sqlite3
import logging
from setting import serie_dir,output_path
#output_path='/var/lib/transmission/'
#serie_dir='/mnt/hdd2/series/'
logging.basicConfig(filename=output_path+'database.log', level=logging.INFO)
#dict to convert monts to number
dates = {"Jan":"1","Feb":"2","Mar":"3","Apr":"4","May":"5","Jun":"6","Jul":"7","Aug":"8","Sep":"9","Oct":"10","Nov":"11","Dec":"12"}
with open(output_path+'outputfile') as data_file:    
    data = json.load(data_file)
conn = sqlite3.connect(output_path+'series.db')
c = conn.cursor()
sql = 'drop table series'
c.execute(sql)
sql='create table if not exists series (id integer primary key autoincrement,serie text, season integer, episode integer, date text)'
c.execute(sql)
for j in data:
	serie_store = j["Title"]
	imdb_key = j['imdbID']
	r = urllib.request.urlopen('http://imdb.com/title/' + imdb_key).read()
	soup = BeautifulSoup(r,'lxml')
	#print(type(soup))
	
	store = []
	letters = soup.find_all("div", class_="seasons-and-year-nav")
	#print(letters[0].a["href"] + " " + letters[0].a.get_text())
	#print(len(letters[0].find_all('a')))
	#	print(link['href'])
	#	print(link.get_text())
	for link in letters[0].find_all('a'):
		if link.get_text().isdigit():
			if int(link.get_text()) < 50:
				store.insert(0,int(link.get_text()))

	
	while store[0] > 1:
		store.insert(0,store[0]-1)
	#for i in store:
	#	print("http://www.imdb.com/title/tt0944947/episodes?season="+str(i)+"&ref_=tt_eps_sn_" + str(i))
	
	for i in store:
		
		r = "http://www.imdb.com/title/"+imdb_key+"/episodes?season="+str(i)+"&ref_=tt_eps_sn_" + str(i)
		#print(r)
		r = urllib.request.urlopen(r).read()
		soup = BeautifulSoup(r,'lxml')

		for x in soup.find_all("div",class_="info"):
			for episode,j in zip(x.find_all('meta'),x.find_all("div",class_="airdate")):
					if episode == "":
						episode = ""
					else:
						episode = int(episode['content'])
					if len(j.get_text('',1).replace(".","").split(" ")) == 1:
						correct_date = ""
					else:
						correct_date = j.get_text('',1).replace(".","").split(" ")
						if len(correct_date) == 3:
							correct_date[1] = dates.get(correct_date[1])
							correct_date.reverse()
							for x in range(0,len(correct_date)):
								if int(x) < 50 and len(correct_date[x]) == 1:
									correct_date[x] = "0"+correct_date[x]

							correct_date = "-".join(correct_date)
						else:
							correct_date = "-".join(correct_date)
					#print(serie_store + " season " + str(i) + " episode " + str(counter)  + " date " + correct_date)
					c.execute("insert into series (serie, season, episode, date) values (?,?,?,?)",(serie_store,i,episode,correct_date))
					#print(i.get_text())
conn.commit()
conn.close()
logging.info("database succesfull updated/created")
#from time import gmtime, strftime
#store=strftime("%Y-%m-%d", gmtime())
#for row in c.execute("SELECT * FROM series WHERE date > '%s' ORDER BY date ASC" % store):
#	print(row)

#bash
#for i in `find . -type d`; do j=`echo $i|tr '[A-Z]' '[a-z]'|sed 's/season_0/season_/g'`; mv $i $j; done
