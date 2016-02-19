#!/usr/bin/env python
import logging
import os
import urllib.request
import json
output_path='/var/lib/transmission/'
serie_dir='/mnt/hdd2/series/'
logging.basicConfig(filename=output_path+'series.log', level=logging.INFO)
series=[]
found_series=[]
for f in os.listdir(serie_dir):
    print(os.path.isdir(f))
    if not f.startswith('.') and os.path.isdir(serie_dir+f):
        series.append(f)
print(series)
for f in series:
        r = str.replace(f,"_","%20")
        seq = ('http://www.omdbapi.com/?s=',r,'&type=series')
        request = "".join(seq)
        response = urllib.request.urlopen(request)
        str_response = response.read().decode('utf-8')
        obj = json.loads(str_response)
        if obj['Response'] == "True" and len(obj['Search'][0]['Year']) == 5:
                obj['Search'][0]['Directory'] = f
                found_series.append(obj['Search'][0])
                logging.info("serie found: " + f)
        else:
                logging.info(f+" not found or no longer running")
with open(output_path + 'outputfile', 'w') as fout:
    json.dump(found_series, fout)
