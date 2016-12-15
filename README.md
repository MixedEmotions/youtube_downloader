# Youtube Downloaded


## Overview
Collects data of activites and comments of youtube channels. Is also possible download video and audio.
All downloaded informations are stored in data.json file in json format and printed to the stdout. It also supports
update mod. Update mod updates all data given by file and also add new one (if there are any). There is third mode and its searching by keyword.
Search mode will search all videos related to keyword given by argument, but it can return maximum of 500 videos due to google DATA API limits.


## Important
Script using YouTube Data API for downlading youtube data. For using Data API is need create an google account and new application. Configuration file is in client_secrets.json. It's important for successful run script.

## Limits
Downloading data from youtube is limited. Overview is on page our application on youtube. Maximum limit can be increased. 
Defaults is 50 000 000 requests per day. (Operation write needs over 50 operations, read 10-20 operations).
The search can be obtained maximum 500 videos informations. 

## Installation

1. Install Docker
2. Check your installation by running: docker run hello-world
3. Clone the repository: git clone https://thermaltaker@bitbucket.org/knotgroups/youtube.git
4. Check if is installed python: docker run hello-world python --version
    If isn't installed run: docker pull python
    Else continue to step 5
5. Build image: docker build -t thermaltaker/youtube .
6. Now is possible run script

## Running
Script have one obligatory parameter `--id/--username` or `--update_file` or `--search` (with possible argument date). 
Where id/username is ID channel/user name. Update file is argument, who launches actualization mode on the file in this argument. Search allow searching by keywords. Searching by keywords serach all videos by certain date (default is 2015-07-15T00:00:00Z). Date is possible setup by next argument date (in RFC 3339 format).

### Example running:

    $ docker run thermaltaker/youtube python /youtube_downloader.py --username=skoda
    $ docker run thermaltaker/youtube python /youtube_downloader.py --username=cocacola
    $ docker run thermaltaker/youtube python /youtube_downloader.py --id=UCtxkCXCD8bWpE8Ea_l4tV2A 

### Update mode:

    $ docker run thermaltaker/youtube python /youtube_downloader.py --update_file=skoda.json
    $ docker run thermaltaker/youtube python /youtube_downloader.py --update_file=cocacola.json

### Searching mode:


    $ docker run thermaltaker/youtube python /youtube_downloader.py --search=grexit
    $ docker run thermaltaker/youtube python /youtube_downloader.py --search=grexit --date=2015-07-15T00:00:00Z
    $ docker run thermaltaker/youtube python /youtube_downloader.py --search='Samsung Galaxy S6'


## Output

Output is by default writing to stdout. It's recommended to redirect output to any file.

(Normal mode)

    {  
       `activities`:[ {  
             "view_count":"750",
             "activity_id":"VTE0MzY0MjcyNzkxMzk5NDk5MzYxMDEzOTI=",
             "description":"We understand that the road seems much longer if everyone is feeling dry and thirsty.\n\nThat’s why there’s a special space in the front door panel to store a full 1.5 litre bottle of water. It will sit there safely without getting squashed, ready for when you need it. \n\nLearn more about Simply Clever solutions here: http://goo.gl/rdup9g",
             "title":"ŠKODA Superb - 1.5 l Bottle Holder",
             "video_id":"BlZhtuG838w",
             "comments":[  
                {  
                   "updated":"2015-07-09T07:36:34.213Z",
                   "author":"ŠKODA",
                   "text":"",
                   "video_id":"BlZhtuG838w",
                   "like_count":3,
                   "replies":[  
                      {  
                         "updated":"2015-07-09T08:40:12.826Z",
                         "author":"Juan Mackie",
                         "text":"Any word on the Android Auto update for the current Octavia line up ?",
                         "parent_id":"z124gzvatyzxtjnjr04cf5kwikyov5e5554",
                         "like_count":0,
                         "likes":0,
                         "published":"2015-07-09T08:40:12.826Z",
                         "id":"z124gzvatyzxtjnjr04cf5kwikyov5e5554.1436431212826862"
                      }
                   ],
                   "id":"z124gzvatyzxtjnjr04cf5kwikyov5e5554",
                   "published":"2015-07-09T07:36:34.213Z"
                }
             ],
             "dislike_count":"0",
             "like_count":"12",
             "published":"2015-07-09T07:34:39.000Z"
          },..
        ],
       "video_count":"104",
       "name":"ŠKODA",
       "subscriber_count":"8533",
       "view_count":"2751779",
       "channel_id":"UCjG24cC7xIEkVtxKdhHDwtg"
    }
    
If is in video disabled like and dislike is `dislike_count` and `like_count` set to -1.
Output for searching mode is same. Missing only informations about channel, which is replaced attribute date and keyword.
(Search mode)

    {
       "date": "2015-07-15T00:00:00Z",
       "videos": [
          {
             "view_count": "1781",
             "description": "The Federal Reserve says it's “likely” to raise rates this year for the for time since the financial crisis. That's exactly what Federal Reserve Chairwoman Janet ...",
             "title": "[394] Yellin’ at Yellen, #Grexit spawns #Brexit talk",
             "video_id": "G9Pdf__oCRQ",
             "comments": [
                {
                   "updated": "2015-07-16T17:01:47.145Z",
                   "author": "anthony leviste",
                   "replies": [],
                   "text": "Ameera, just WOW to your guest Marin who is very enlightening, didn't know \nhe is the expert on the ground when it comes to market for oil quality. RT \nknows when and who to air, who among news online can do that, no one.﻿",
                   "video_id": "G9Pdf__oCRQ",
                   "like_count": 0,
                   "published": "2015-07-16T17:01:47.145Z",
                   "id": "z13tcbvbcxzgdjbm523pfpi5ami2whtyq04"
                },..
              ],
       "keyword": "grexit"
    }

## Downloading videos and audios from Youtube

For downloading videos and audios from youtube, we use youtube-dl (https://github.com/rg3/youtube-dl).
Downloading is possible in standard mode, actualization mode and searching mode.
		--fetch # allow download video (is downloading video only with best quality)
		--fetch --fetchallformats # download all available video formats, together must be with --fetch
		--outputdir DIR # output video folder, default is "/tmp/youtube_output"
		--outputtemplate TEMPLATE # output video name, default is "%(id)s_%(format)s.%(ext)s" (more in TEMPLATE in utilite youtubedl)

## Download video in all available formats by id:

    $ docker run thermaltaker/youtube python /youtube_downloader.py --id=UCkwlix5Fv0dg3cQJCz4dO4Q --fetch --fetchallformats

## Youtube-dl writing process on terminal.
 Activates quiet mode, avoiding many messages being written to the terminal.
    --quiet 

Example: 

    $ docker run thermaltaker/youtube python /youtube_downloader.py --username=skoda --fetch --quiet
    
    Output with parameters --fetch (parameter "-ti -v folder:folder:Z" tmp folder with downloaded video in container copy to host tmp folder)
    	$ docker run -ti -v /tmp/youtube_output:/tmp/youtube_output/:Z thermaltaker/youtube python /youtube_downloader.py --id=UCtxkCXCD8bWpE8Ea_l4tV2A --fetch
    
    	{
    	 "activities": [
    	   {
    	     "activity_id": "VTE0Njk2OTk3NjYxNDA2MzIwNDUwOTgyNTY=",
    	     "comments": [],
    	     "description": "Tôi đã tạo video này bằng Trình chỉnh sửa video của YouTube (http://www.youtube.com/editor)",
    	     "dislike_count": "3",
    	     "like_count": "0",
    	     "published": "2016-07-28T09:56:06.000Z",
    	     "title": "funny moments",
    	     "video": [
    	       "/tmp/youtube_output/eicfn-Hvn80_22 - 1280x720 (hd720).mp4"
    	     ],
    	     "video_id": "eicfn-Hvn80",
    	     "view_count": "3435"
    	   },
    	   {
    	     "activity_id": "VTE0Njk2OTk3MjkxNDA2Mjc1ODYzNzM1MjA=",
    	     "comments": [],
    	     "description": "Tôi đã tạo video này bằng Trình chỉnh sửa video của YouTube (http://www.youtube.com/editor)",
    	     "dislike_count": "1",
    	     "like_count": "0",
    	     "published": "2016-07-28T09:55:29.000Z",
    	     "title": "Fail army",
    	     "video": [
    	       "/tmp/youtube_output/EShBokxdNAU_22 - 1280x720 (hd720).mp4"
    	     ],
    	     "video_id": "EShBokxdNAU",
    	     "view_count": "551"
    	   }
    	 ],
    	 "channel_id": "UC-r_WlJAVk2kp7Q9ruZL1uA",
    	 "name": "Pik Tv",
    	 "subscriber_count": "2",
    	 "video_count": "2",
    	 "view_count": "3212"
    	}

## Output with parameters --fetchallformats


    $ docker run -ti -v /tmp/youtube_output:/tmp/youtube_output/:Z thermaltaker/youtube python /youtube_downloader.py --id=UCtxkCXCD8bWpE8Ea_l4tV2A --fetch --fetchallformats
    {
     "activities": [
       {
         "activity_id": "VTE0Njk2OTk3NjYxNDA3MTI0OTU3NjQzMDQ=",
         "comments": [],
         "description": "Tôi đã tạo video này bằng Trình chỉnh sửa video của YouTube (http://www.youtube.com/editor)",
         "dislike_count": "3",
         "like_count": "0",
         "published": "2016-07-28T09:56:06.000Z",
         "title": "funny moments",
         "video": [
           "/tmp/youtube_output/eicfn-Hvn80_249 - audio only (DASH audio).webm",
           "/tmp/youtube_output/eicfn-Hvn80_250 - audio only (DASH audio).webm",
           "/tmp/youtube_output/eicfn-Hvn80_251 - audio only (DASH audio).webm",
           "/tmp/youtube_output/eicfn-Hvn80_171 - audio only (DASH audio).webm",
           "/tmp/youtube_output/eicfn-Hvn80_140 - audio only (DASH audio).m4a",
           "/tmp/youtube_output/eicfn-Hvn80_278 - 256x144 (DASH video).webm",
           "/tmp/youtube_output/eicfn-Hvn80_160 - 256x144 (DASH video).mp4",
           "/tmp/youtube_output/eicfn-Hvn80_242 - 426x240 (DASH video).webm",
           "/tmp/youtube_output/eicfn-Hvn80_133 - 426x240 (DASH video).mp4",
           "/tmp/youtube_output/eicfn-Hvn80_134 - 640x360 (DASH video).mp4",
           "/tmp/youtube_output/eicfn-Hvn80_243 - 640x360 (DASH video).webm",
           "/tmp/youtube_output/eicfn-Hvn80_244 - 854x480 (DASH video).webm",
           "/tmp/youtube_output/eicfn-Hvn80_135 - 854x480 (DASH video).mp4",
           "/tmp/youtube_output/eicfn-Hvn80_247 - 1280x720 (DASH video).webm",
           "/tmp/youtube_output/eicfn-Hvn80_136 - 1280x720 (DASH video).mp4",
           "/tmp/youtube_output/eicfn-Hvn80_36 - 320x (small).3gp",
           "/tmp/youtube_output/eicfn-Hvn80_17 - 176x144 (small).3gp",
           "/tmp/youtube_output/eicfn-Hvn80_43 - 640x360 (medium).webm",
           "/tmp/youtube_output/eicfn-Hvn80_18 - 640x360 (medium).mp4",
           "/tmp/youtube_output/eicfn-Hvn80_22 - 1280x720 (hd720).mp4"
         ],
         "video_id": "eicfn-Hvn80",
         "view_count": "3435"
       },

# Credits
* Štěpán Vrša, xvrsas00@stud.fit.vutbr.cz
* Filip Čonka, xconka00@stud.fit.vutbr.cz
* Jakub Débef, xdebef01@stud.fit.vutbr.cz

# Acknowledgement

This orchestrator was developed by [Paradigma Digital](https://en.paradigmadigital.com/) as part of the MixedEmotions project. This development has been partially funded by the European Union through the MixedEmotions Project (project number H2020 655632), as part of the `RIA ICT 15 Big data and Open Data Innovation and take-up` programme.

![MixedEmotions](https://raw.githubusercontent.com/MixedEmotions/MixedEmotions/master/img/me.png) 

![EU](https://raw.githubusercontent.com/MixedEmotions/MixedEmotions/master/img/H2020-Web.png)

 http://ec.europa.eu/research/participants/portal/desktop/en/opportunities/index.html	
