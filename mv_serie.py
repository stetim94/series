#!/usr/bin/env python
import shutil
import json
import os
import re
serie_folder='/mnt/hdd2/series'
os.chdir(serie_folder)
video_files = ['.mp4', '.mov', '.flv', '.mpg', '.wmv', '.avi', '.asf', '.srt', '.mkv', '.mpeg', '.rm', '.vob', '.3gp', '.3g2']
#tr_dir = os.environ['TR_TORRENT_DIR']
#tr_fil = os.environ['TR_TORRENT_NAME']
#f = open('workfile', 'w')
#f.write(tr_dir + '\n')
#f.write(tr_fil + '\n')
#f.close()
#location=os.path.join(tr_dir,tr_fil)
with open('workfile') as f:
        mylist = f.read().splitlines() 
with open('to_download') as data_file:    
        data = json.load(data_file)

location=os.path.join(mylist[0],mylist[1])
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
                to_move=os.path.join(serie_folder,j[-1],'season_'+str(j[2]) + '/')
                if not os.path.exists(to_move):
                    os.makedirs(os.path.join(to_move))
                print(check_file,to_move)
                shutil.move(check_file,to_move)
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
                to_move=os.path.join(serie_folder,j[-1],'season_'+str(j[2]) + '/')
                if not os.path.exists(to_move):
                    os.makedirs(os.path.join(to_move))
                shutil.move(location,to_move)
                os.system('/home/steven/bin/subtitle-downloader.py '+ to_move + location )
move_time()
