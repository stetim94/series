#!/usr/bin/env python
import shutil
import json
import os
import re
import logging
import sys
from setting import serie_dir,output_path
try:
    #output_path='/var/lib/transmission/'
    #serie_dir='/mnt/hdd2/series'
    logging.basicConfig(filename=output_path+'moving.log', level=logging.INFO)
    video_files = ['.mp4', '.mov', '.flv', '.mpg', '.wmv', '.avi', '.asf', '.srt', '.mkv', '.mpeg', '.rm', '.vob', '.3gp', '.3g2']
    try:
        tr_dir = os.environ['TR_TORRENT_DIR']
        tr_fil = os.environ['TR_TORRENT_NAME']
    except KeyError:
        print("Oops, transmission didn't provide torrent data")
        logging.error("Transmission didn't provide torrent data")
    #f = open('workfile', 'w')
    #f.write(tr_dir + '\n')
    #f.write(tr_fil + '\n')
    #f.close()
    location=os.path.join(tr_dir,tr_fil)
    #with open(output_path+'workfile') as f:
    #        mylist = f.read().splitlines() 
    if not os.path.isfile(output_path+'to_download'):
        print("Oops, no data on what to move")
        logging.error("No to_download file, unable to move files")
    try:
        with open(output_path+'to_download') as data_file:    
            data = json.load(data_file)
    except:
        print("something went wrong opening data-file")
        logging.error("something went wrong openind data file")
    #location=os.path.join(mylist[0],mylist[1])
    print(location)
    def move_time():
        if  os.path.isdir(location):
            #print(data)
            for i in os.listdir(location):
                check_file = location + "/" + i 
                #print(check_file)
                filename,file_extension = os.path.splitext(i.lower())
                #print(filename,file_extension)
                if file_extension in video_files:
                    for j in data:
                        regex=re.findall(r"[\w]+",j[1])
                        #print(regex)
                        for x in regex: 
                            if x.lower() not in filename:
                                print("no match")
                                return False
                    to_move=os.path.join(serie_dir,j[-1],'season_'+str(j[2]) + '/')
                    if not os.path.exists(to_move):
                        os.makedirs(os.path.join(to_move))
                    print(check_file,to_move)
                    try:
                        shutil.move(check_file,to_move)
                        logging.info("moved " + i + " to "+ to_move)
                    except:
                        loggin.error("failed to move file")
                    os.system('/home/steven/bin/subtitle-downloader.py '+ to_move + i )
                    shutil.rmtree(location, ignore_errors=True)
                    os.system('/home/steven/bin/subtitle-downloader.py ' + to_move + i)

        else:
            filename,file_extension = os.path.splitext(location)
            if file_extension.lower() in video_files:
                for j in data:
                    regex=re.findall(r"[\w]+",j[1])
                    for x in regex:        
                        if x.lower() not in filename:
                            print("no match")
                            return False
                    to_move=os.path.join(serie_dir,j[-1],'season_'+str(j[2]) + '/')
                    if not os.path.exists(to_move):
                        os.makedirs(os.path.join(to_move))
                    shutil.move(location,to_move)
                    os.system('/home/steven/bin/subtitle-downloader.py '+ to_move + location )
    move_time()
except:
    logging.error("program had an error: "+ str(sys.exc_info()))
