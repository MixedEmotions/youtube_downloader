#!/usr/bin/env python
#Author: Stepan Vrsa  
#Email: xvrsas00@stud.fit.vutbr.cz
#Author: Filip Conka
#Email: xconka00@stud.fit.vutbr.cz
#Author: Jakub Debef
#Email: xdebef01@stud.fit.vutbr.cz
#Last update: 2016-01-10
from __future__ import unicode_literals

import json,argparse,sys,io
from apiclient.discovery import build
import youtube_dl

#main fucntion that parse arguments, authenticate and construct service and get a list of public activities of user 
#it also stores informations about activities(videos) in dictionary
def main(argv):
    
    #parse arguments, programm requires argument profile_id
    #profile_id is ID of user/site on Google+
    parser = argparse.ArgumentParser(description='Social_networks_download',add_help=True)
    parser.add_argument('--id',action = 'store', dest='profile_id')
    parser.add_argument('--username',action = 'store', dest='username')
    parser.add_argument('--search',action = 'store', dest='search')
    parser.add_argument('--videoId',action = 'store', dest='videoId')
    parser.add_argument('--date',action = 'store', dest='date')
    parser.add_argument('--update_file',action = 'store', dest='update_file')
    parser.add_argument('--fetch',action = 'store_true', dest='fetch')
    parser.add_argument('--fetchallformats',action = 'store_true', dest='fetchallformats')
    parser.add_argument('--outputdir',action = 'store', dest='outputdir', default="/tmp/youtube_output/")
    parser.add_argument('--outputtemplate',action = 'store', dest='outputtemplate', default="%(id)s_%(format)s.%(ext)s")
    parser.add_argument('--quiet',action = 'store_true', dest='quiet')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    
    #parse arguments
    args = parser.parse_args()
    
    #Authenticate and construct service, authentization is not using oauth2 as it needs
    # to log in at browser
    try:
        service = build('youtube', 'v3', developerKey='AIzaSyCWs69ECTAVG9Il0A_beBk6xbfFnzom5Pg')
    except:
        sys.stderr.write('Error: Couldnt authenticate and construct service\n')
        exit(1)
    # Retrieve the contentDetails and snippet part of the channel resource for the
    # authenticated user's channel.
    if args.profile_id:
        channel_resource = service.channels()
        channel_request = channel_resource.list ( part = 'snippet, statistics', id = args.profile_id, maxResults = 1)
        try:
            channel = channel_request.execute()
        except:
            sys.stderr.write('Error: Wrong username - or 404 request error\n')
            exit(1)
    # videoId download mode
    elif args.videoId:  
        #make new dictionary
        json_dictionary = dict()
        json_dictionary['video'] = list()
        #calling function that iterate over list and get video information (number of likes, dislikes etc..)
        json_dictionary.update(videoID_download(args.videoId, service, json_dictionary, args))

        #printing output to stdout
        sys.stdout.write(json.dumps(json_dictionary, ensure_ascii=False).encode('utf-8'))
        #exit succesfuly
        exit(0)
    # search mode enabled
    elif args.search:  
        #default date 
        date = '2015-01-01T00:00:00Z'
        if args.date:
            date = args.date   
        
        #preparing service for searching video by keyword
        
        #make new dictionary
        json_dictionary = dict()
        json_dictionary['keyword'] = args.search
        json_dictionary['date'] = date
        json_dictionary['videos'] = list()
        #calling function that iterate over list and get video information (number of likes, dislikes etc..)
        json_dictionary.update(search_video( service, json_dictionary, date, args))

        #printing output to stdout
        sys.stdout.write(json.dumps(json_dictionary, ensure_ascii=False).encode('utf-8'))
        #exit succesfuly
        exit(0)
    #when we cant get id of channel manualy, we can use username of channel
    #this will search channel information by username and we will get id of channel
    elif args.username:
        channel_resource = service.channels()
        channel_request = channel_resource.list ( part = 'snippet, statistics', forUsername = args.username, maxResults = 1)
        try:
            channel = channel_request.execute()
        except:
            sys.stderr.write('Error: Wrong username - or 404 request error\n')
            exit(1)
       
        activities_list_resource = service.activities()
        try:
            activities_list_request = activities_list_resource.list(
            channelId = channel['items'][0]['id'],
            part = 'snippet,contentDetails', maxResults = 50)
        except:
            sys.stderr.write('Error: Non-existent channel name \n')
            exit(1)
        
    #update mode -> script will open file that we want to be updated
    #it loads data into json format, than it updates channel informations like video count, subscriber count etc..    
    elif args.update_file:
        with open(args.update_file) as data_file:    
            data = json.load(data_file)
            
        channel_resource = service.channels()
        channel_request = channel_resource.list ( part = 'snippet, statistics', id = data['channel_id'], maxResults = 1)
        try:
            channel = channel_request.execute()
        except:
            sys.stderr.write('Error: Wrong username - or 404 request error\n')
            exit(1)
        #updating channel data
        data['view_count'] = channel['items'][0]['statistics']['viewCount'] 
        data['subscriber_count'] = channel['items'][0]['statistics']['subscriberCount'] 
        data['video_count'] = channel['items'][0]['statistics']['videoCount'] 
        #calling function that updates activities and update old dictionary
        data.update(update_activities(data['channel_id'], service, data, args))

        #script updated data, now we can write it back
        #writing updated data to the old file
        with io.open(args.update_file, 'w', encoding='utf-8') as f:
            f.seek(0)
            f.write(unicode(json.dumps(data, ensure_ascii=False)))
        exit(0)
        
    #wrong argument
    else:
        sys.stderr.write('Error: Need --id or --username argument!\n')
        exit(1)
        
    # now we can get channel information
    json_dictionary = dict()
    try:
        json_dictionary['channel_id'] = channel['items'][0]['id'] 
    except:
        sys.stderr.write('Error: Non-existent channel id \n')
        exit(1)
    
    json_dictionary['name'] = channel['items'][0]['snippet']['title'] 
    json_dictionary['view_count'] = channel['items'][0]['statistics']['viewCount'] 
    json_dictionary['subscriber_count'] = channel['items'][0]['statistics']['subscriberCount'] 
    json_dictionary['video_count'] = channel['items'][0]['statistics']['videoCount'] 
    json_dictionary['activities'] = list()
    json_dictionary.update(get_list_of_activities(json_dictionary['channel_id'], service, json_dictionary, args))
    
    #printing output to stdout
    sys.stdout.write(json.dumps(json_dictionary, ensure_ascii=False).encode('utf-8'))


def getVideoIds(videoDict):
    videoIds = list()
    for video in videoDict:
        videoIds.append(video["video_id"])
    return videoIds

#------------------------------------------------------------------------------
#-------------------------------VIDEOID MODE------------------------------------     
#------------------------------------------------------------------------------ 

#function that download informations of video by ID given by argument --videoId
def videoID_download(videoId, service, json_dictionary, args):
    #
    rating_resource = service.videos()
    rating_request = rating_resource.list( part = 'snippet,statistics', id = videoId)

    video_dictionary=dict()
    try:
        rating_list = rating_request.execute()
    except:
        sys.stderr.write('Error: Can\'t get rating of video  - or 404 request error\n')
        exit(1)

    video_dictionary['comments'] = list()
    video_dictionary.update(get_list_of_comments_threads(videoId, service, video_dictionary))
    #add path to video file (only if exist --fetch)
    if args.fetch:
        video_dictionary['video'] = download_video(videoId, args.fetchallformats, args.outputdir, args.outputtemplate, args.quiet)

    for rating in rating_list['items']:
        video_dictionary['title'] = rating['snippet']['title']
        video_dictionary['videoId'] = rating['id']
        video_dictionary['description'] = rating['snippet']['description']
        video_dictionary['channelId'] = rating['snippet']['channelId']
        video_dictionary['publishedAt'] = rating['snippet']['publishedAt']
        video_dictionary['channelTitle'] = rating['snippet']['channelTitle']
        video_dictionary['view_count'] = rating['statistics']['viewCount']
        video_dictionary['like_count'] = rating['statistics']['likeCount'] if 'likeCount' in rating['statistics'] else -1
        video_dictionary['dislike_count'] = rating['statistics']['dislikeCount'] if 'dislikeCount' in rating['statistics'] else -1

    
    json_dictionary['video'].append(video_dictionary)
    return json_dictionary


#------------------------------------------------------------------------------
#-------------------------------SEARCH MODE------------------------------------     
#------------------------------------------------------------------------------ 

#fucntion that search for videos by keyword given by argument --search, it searchs videos after given date by argument date or by
#default 2015-01-01T00:00:00Z
def search_video( service, json_dictionary, date, args):
    next_page_token = True
    search_resource = service.search()
    search_request = search_resource.list ( part = 'snippet', maxResults = 50, publishedAfter = date, q = args.search, type = 'video')
    #iterating while there is next page
    while next_page_token:
        try:
            search_list = search_request.execute()
        except:
            sys.stderr.write('Error: Wrong ID/username - or 404 request error\n')
            exit(1)
        if 'nextPageToken' in search_list.keys():
            next_page_token = search_list['nextPageToken']
        else:
            next_page_token = False
        #checking if video list has valuable informations
        if search_list.get('items') is not None:
            #iterating over videos list
            for video in search_list['items']:
                #new dictionary
                video_dictionary=dict()
                #filling dictionary with data
                video_dictionary['video_id'] = video['id']['videoId']
                video_dictionary['published'] = video['snippet']['publishedAt']
                video_dictionary['title'] = video['snippet']['title']
                video_dictionary['description'] = video['snippet']['description']
                video_dictionary['channel_id'] = video['snippet']['channelId']
                #add path to video file (only if exist --fetch)
                if args.fetch:
                    video_dictionary['video'] = download_video(video_dictionary['video_id'], args.fetchallformats, args.outputdir, args.outputtemplate, args.quiet)
                # need to get aditional information about rating, likes etc..
                rating_resource = service.videos()
                rating_request = rating_resource.list ( part = 'statistics',
                id = video['id']['videoId'])
                try:
                    rating_list = rating_request.execute()
                except:
                    sys.stderr.write('Error: Can\'t get rating of video  - or 404 request error\n')
                    exit(1)
                #iterating over rating details of video
                for rating in rating_list['items']:
                    video_dictionary['view_count'] = rating['statistics']['viewCount']
                    video_dictionary['like_count'] = rating['statistics']['likeCount'] if 'likeCount' in rating['statistics'] else -1
                    video_dictionary['dislike_count'] = rating['statistics']['dislikeCount'] if 'dislikeCount' in rating['statistics'] else -1
                #calling function that collects all comments of an activity
                video_dictionary['comments'] = list()
                video_dictionary.update(get_list_of_comments_threads(video['id']['videoId'],
                service, video_dictionary))
                
                json_dictionary['videos'].append(video_dictionary)
                
        #getting next page of results
        search_request = search_resource.list ( part = 'snippet', maxResults = 50, publishedAfter = date, q = args.search, type = 'video', pageToken = next_page_token )
    return json_dictionary    
#------------------------------------------------------------------------------
#-------------------------------UPDATE MODE------------------------------------     
#------------------------------------------------------------------------------  

#function that updates old data and add new one( if there are any)
def update_activities(channel_id, service, json_dictionary, args):
    #need index for iterating over lists
    #one for new list and one for old from file 
    index_old = 0
    index_new = 0
    #get list of activities of user
    activities_list_resource=service.activities()
    activities_list_request=activities_list_resource.list( channelId = channel_id,
    part = 'snippet,contentDetails', maxResults = 50)  
    #iterate over list until there is no activity
    while activities_list_request is not None:
        try:
            activities_list = activities_list_request.execute()
        except:
            sys.stderr.write('Error: Wrong ID of user/site - or 404 request error\n')
            exit(1)
        if activities_list.get('items') is not None:
            #iterating over list of activities
            for activity in activities_list['items']:
                #ignoring activity like and adding video to playlist
                if 'upload' != activity['snippet']['type']:
                    index_new += 1
                    continue
                #checking if video ids are the same, if yes we can update data like view count, likes..etc
                elif activities_list['items'][index_new]['contentDetails']['upload']['videoId'] == json_dictionary['activities'][index_old]['video_id']:
                    rating_resource = service.videos()
                    rating_request = rating_resource.list ( part = 'statistics',
                    id = json_dictionary['activities'][index_old]['video_id'])
                    try:
                        rating_list = rating_request.execute()
                    except:
                        sys.stderr.write('Error: Can\'t get rating of video  - or 404 request error\n')
                        exit(1)
                    #iterating over rating details of video
                    for rating in rating_list['items']:
                        json_dictionary['activities'][index_old]['view_count'] = rating['statistics']['viewCount']
                        json_dictionary['activities'][index_old]['like_count'] = rating['statistics']['likeCount'] if 'likeCount' in rating['statistics'] else -1
                        json_dictionary['activities'][index_old]['dislike_count'] = rating['statistics']['dislikeCount'] if 'dislikeCount' in rating['statistics'] else -1
                    #updating commentThreads
                    #if there are any replies, we need to update them too
                    if len(json_dictionary['activities'][index_old]['comments']) !=0:
                        json_dictionary.update(update_comments_threads(json_dictionary['activities'][index_old]['video_id'], service, json_dictionary, index_old))
                    index_old += 1
                    index_new += 1
                    continue
               
                # ids arent equal -> there is new activity, need to add it to the dictionary
                else:
                    activities_dictionary=dict()
                    #filling dictionary with data
                    activities_dictionary['activity_id'] = activity['id']
                    activities_dictionary['published'] = activity['snippet']['publishedAt']
                    activities_dictionary['title'] = activity['snippet']['title']
                    activities_dictionary['description'] = activity['snippet']['description']
                    activities_dictionary['video_id'] = activity['contentDetails']['upload']['videoId']
                    #add path to video file (only if exist --fetch)
                    if args.fetch:
                        activities_dictionary['video'] = download_video(activities_dictionary['video_id'], args.fetchallformats, args.outputdir, args.outputtemplate, args.quiet)
                    # need to get aditional information about rating, likes etc..
                    rating_resource = service.videos()
                    rating_request = rating_resource.list ( part = 'statistics',
                    id = activity['contentDetails']['upload']['videoId'])
                    try:
                        rating_list = rating_request.execute()
                    except:
                        sys.stderr.write('Error: Can\'t get rating of video  - or 404 request error\n')
                        exit(1)
                    #iterating over rating details of video
                    for rating in rating_list['items']:
                        activities_dictionary['view_count'] = rating['statistics']['viewCount']
                        activities_dictionary['like_count'] = rating['statistics']['likeCount'] if 'likeCount' in rating['statistics'] else -1
                        activities_dictionary['dislike_count'] = rating['statistics']['dislikeCount'] if 'dislikeCount' in rating['statistics'] else -1
                    #calling function that collects all comments of an activity
                    activities_dictionary['comments'] = list()
                    activities_dictionary.update(get_list_of_comments_threads(activity['contentDetails']['upload']['videoId'],
                    service, activities_dictionary))
                    
                    #index specify position of the new activity
                    json_dictionary['activities'].insert(index_old,activities_dictionary)
                    index_old += 1
                    index_new += 1

        #new page of activities  
        index_new = 0
        activities_list_request = activities_list_resource.list_next(activities_list_request, activities_list)
    return json_dictionary
    
#function that check if comment threads are up to date and it also adds new threads that are not saved
def update_comments_threads(video_id, service, json_dictionary, activity_index):
    # this variable is needed as condition at while cycle, its contains information about next page token
    index = 0
    comment_count = len(json_dictionary['activities'][activity_index]['comments'])
    next_page_token = True
    #getting list of comments of an activity, maximum 100 comments of activity in one request
    comments_threads_list_resource=service.commentThreads()
    comments_threads_list_request=comments_threads_list_resource.list( part = 'snippet',
    maxResults = 100,  videoId = video_id, textFormat = 'plainText')
    #same algorithm as getting list of activities
    while next_page_token:
        try:
            comments_threads_list = comments_threads_list_request.execute()
        except:
            break
        #saving next page token
        if 'nextPageToken' in comments_threads_list.keys():
            next_page_token = comments_threads_list['nextPageToken']
        else:
             next_page_token = False
             
        if comments_threads_list.get('items') is not None:
            for comment in comments_threads_list['items']:
                if index + 1 <= comment_count:
                    #checking if comment thread was edited, updating like count
                    if comment['snippet']['topLevelComment']['snippet']['updatedAt'] == json_dictionary['activities'][activity_index]['comments'][index]['updated']:
                        json_dictionary['activities'][activity_index]['comments'][index]['like_count'] = comment['snippet']['topLevelComment']['snippet']['likeCount']
                    # it was edited, so it updates text and number of likes
                    else:
                        json_dictionary['activities'][activity_index]['comments'][index]['text'] = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                        json_dictionary['activities'][activity_index]['comments'][index]['like_count'] = comment['snippet']['topLevelComment']['snippet']['likeCount']
                    #checking if comment has reply
                    if comment['snippet']['totalReplyCount'] is not 0:
                        json_dictionary.update(update_comments(json_dictionary['activities'][activity_index]['comments'][index]['id'], service, json_dictionary, activity_index, index))
                    index += 1  
                # there is new comment, need to add  it to the dictionary
                else:
                    comments_dictionary = dict()
                    #storing all needed informations about comment threads
                    comments_dictionary['video_id'] = comment['snippet']['videoId']
                    comments_dictionary['id'] = comment['snippet']['topLevelComment']['id']
                    comments_dictionary['text'] = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                    comments_dictionary['author'] = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
                    comments_dictionary['like_count'] = comment['snippet']['topLevelComment']['snippet']['likeCount']
                    comments_dictionary['published'] = comment['snippet']['topLevelComment']['snippet']['publishedAt']
                    comments_dictionary['updated'] = comment['snippet']['topLevelComment']['snippet']['updatedAt']
                    comments_dictionary['replies'] = list()
                    # if there are any replies to the comment we need to call get_list_of_comments function
                    if comment['snippet']['totalReplyCount'] is not 0:
                       comments_dictionary.update(get_list_of_comments(comment['id'], service,
                       comments_dictionary))
                
                    json_dictionary['activities'][activity_index]['comments'].append(comments_dictionary)
        #getting a next page of results        
        comments_threads_list_request = comments_threads_list_resource.list( part = 'snippet',
        maxResults = 100,  videoId = video_id, 
        textFormat = 'plainText', pageToken = next_page_token ) 
    return json_dictionary
 
#fucntion that checks if replies are up to date, if not it will update them or add new replies
def update_comments(comment_thread_id, service, json_dictionary, activity_index, comment_index):
    #again we need to save next page token for while condition
    next_page_token = True
    index = 0 
    comment_count = len(json_dictionary['activities'][activity_index]['comments'][comment_index]['replies'])
    comments_list_resource=service.comments()
    comments_list_request=comments_list_resource.list( part = 'snippet', maxResults = 100,  parentId = comment_thread_id,
    textFormat = 'plainText')
    # main cycle
    while next_page_token:
        try:
            comments_list = comments_list_request.execute()
        except:
            sys.stderr.write('Error: Wrong ID of comment_list- or 404 request error- or dont have permision\\n')
            exit(1)
        # checking if there is nextPageToken,
        if 'nextPageToken' in comments_list.keys():
            next_page_token = comments_list['nextPageToken']
        else:
            next_page_token = False
             
        if comments_list.get('items') is not None:
            #iterating over replies
            for comment in comments_list['items']:
                if index + 1 <= comment_count:
                    #checking if comment wasnt edited
                    if comment['snippet']['updatedAt'] == json_dictionary['activities'][activity_index]['comments'][comment_index]['replies'][index]['updated']:
                        json_dictionary['activities'][activity_index]['comments'][comment_index]['replies'][index]['like_count'] = comment['snippet']['likeCount']
                        index += 1
                    # it was edited, so it updates text and number of likes
                    else:
                        json_dictionary['activities'][activity_index]['comments'][comment_index]['replies'][index]['text'] = comment['snippet']['textDisplay']
                        json_dictionary['activities'][activity_index]['comments'][comment_index]['replies'][index]['like_count'] = comment['snippet']['likeCount']
                        index += 1
                #there is new reply, need to add it to the dictionary
                else:
                    comments_replies_dictionary = dict()
                    comments_replies_dictionary['id'] = comment['id']
                    comments_replies_dictionary['text'] = comment['snippet']['textDisplay']
                    comments_replies_dictionary['parent_id'] = comment['snippet']['parentId']
                    comments_replies_dictionary['author'] = comment['snippet']['authorDisplayName']
                    comments_replies_dictionary['like_count'] = comment['snippet']['likeCount']
                    comments_replies_dictionary['published'] = comment['snippet']['publishedAt']
                    comments_replies_dictionary['updated'] = comment['snippet']['updatedAt']
                    json_dictionary['activities'][activity_index]['comments'][comment_index]['replies'].append(comments_replies_dictionary)
        comments_list_request = comments_list_resource.list( part = 'snippet', maxResults = 100,  parentId = comment_thread_id, 
        textFormat = 'plainText', pageToken = next_page_token )    
    #return dictionary filled with replies datas
    return json_dictionary 
    
#------------------------------------------------------------------------------
#-------------------------------NORMAL MODE------------------------------------     
#------------------------------------------------------------------------------   

#this function collects all channel activities        
def get_list_of_activities(channel_id, service, json_dictionary, args):
    activities_list_resource = service.activities()
    activities_list_request = activities_list_resource.list(
    channelId = channel_id,
    part = 'snippet,contentDetails', maxResults = 50)  
    
    while activities_list_request is not None:
        try:
            activities_list = activities_list_request.execute()
        except:
            sys.stderr.write('Error: Wrong ID/username - or 404 request error\n')
            exit(1)
        #checking if activity has valuable informations
        if activities_list.get('items') is not None:
            #iterating over activities list
            for activity in activities_list['items']:
                #ignoring like activity
                if 'upload' != activity['snippet']['type']:
                    continue
                #new dictionary
                activities_dictionary=dict()
                #filling dictionary with data
                activities_dictionary['activity_id'] = activity['id']
                activities_dictionary['published'] = activity['snippet']['publishedAt']
                activities_dictionary['title'] = activity['snippet']['title']
                activities_dictionary['description'] = activity['snippet']['description']
                activities_dictionary['video_id'] = activity['contentDetails']['upload']['videoId']
                # need to get aditional information about rating, likes etc..
                rating_resource = service.videos()
                rating_request = rating_resource.list ( part = 'statistics',
                id = activity['contentDetails']['upload']['videoId'])
                try:
                    rating_list = rating_request.execute()
                except:
                    sys.stderr.write('Error: Can\'t get rating of video  - or 404 request error\n')
                    exit(1)
                #iterating over rating details of video
                for rating in rating_list['items']:
                    activities_dictionary['view_count'] = rating['statistics']['viewCount']
                    # there is a possibility that liking and disliking is not allowed over activity
                    activities_dictionary['like_count'] = rating['statistics']['likeCount'] if 'likeCount' in rating['statistics'] else -1
                    activities_dictionary['dislike_count'] = rating['statistics']['dislikeCount'] if 'dislikeCount' in rating['statistics'] else -1
                #add path to video file (only if exist --fetch)
                if args.fetch:
                    activities_dictionary['video'] = download_video(activities_dictionary['video_id'], args.fetchallformats, args.outputdir, args.outputtemplate, args.quiet)
                #calling function that collects all comments of an activity
                activities_dictionary['comments'] = list()
                activities_dictionary.update(get_list_of_comments_threads(activity['contentDetails']['upload']['videoId'],
                service, activities_dictionary))
                
                json_dictionary['activities'].append(activities_dictionary)
                
        #getting next page of results
        activities_list_request = activities_list_resource.list_next(activities_list_request, activities_list)
    return json_dictionary
#this functions parse all comment threads
def get_list_of_comments_threads(video_id, service, json_dictionary):
    # this variable is needed as condition at while cycle, its contains information about next page token
    next_page_token = True
    #getting list of comments of an activity, maximum 100 comments of activity in one request
    comments_threads_list_resource=service.commentThreads()
    comments_threads_list_request=comments_threads_list_resource.list( part = 'snippet',
    maxResults = 100,  videoId = video_id, textFormat = 'plainText')
    #same algorithm as getting list of activities
    while next_page_token:
        try:
            comments_threads_list = comments_threads_list_request.execute()
        except:
            break
        #saving next page token
        if 'nextPageToken' in comments_threads_list.keys():
            next_page_token = comments_threads_list['nextPageToken']
        else:
            next_page_token = False
             
        if comments_threads_list.get('items') is not None:
            for comment in comments_threads_list['items']:
                comments_dictionary = dict()
                #storing all needed informations about comment threads
                comments_dictionary['video_id'] = comment['snippet']['videoId']
                comments_dictionary['id'] = comment['snippet']['topLevelComment']['id']
                comments_dictionary['text'] = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                comments_dictionary['author'] = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
                comments_dictionary['like_count'] = comment['snippet']['topLevelComment']['snippet']['likeCount']
                comments_dictionary['published'] = comment['snippet']['topLevelComment']['snippet']['publishedAt']
                comments_dictionary['updated'] = comment['snippet']['topLevelComment']['snippet']['updatedAt']
                comments_dictionary['replies'] = list()
                # if there are any replies to the comment we need to call get_list_of_comments function
                if comment['snippet']['totalReplyCount'] is not 0:
                   comments_dictionary.update(get_list_of_comments(comment['id'], service,
                   comments_dictionary))
                
                json_dictionary['comments'].append(comments_dictionary)
        #getting a next page of results        
        comments_threads_list_request = comments_threads_list_resource.list( part = 'snippet',
        maxResults = 100,  videoId = video_id, 
        textFormat = 'plainText', pageToken = next_page_token ) 
    return json_dictionary
    
    
#this function collects datas from replies   
def get_list_of_comments(comment_thread_id, service, comments_dictionary):
    #again we need to save next page token for while condition
    next_page_token = True
    comments_list_resource=service.comments()
    comments_list_request=comments_list_resource.list( part = 'snippet', maxResults = 100,  parentId = comment_thread_id,
    textFormat = 'plainText')
    # main cycle
    while next_page_token:
        try:
            comments_list = comments_list_request.execute()
        except:
            sys.stderr.write('Error: Wrong ID of comment_list- or 404 request error- or dont have permision\n')
            exit(1)
        # checking if there is nextPageToken,
        if 'nextPageToken' in comments_list.keys():
            next_page_token = comments_list['nextPageToken']
        else:
            next_page_token = False
             
        if comments_list.get('items') is not None:
            #iterating over replies
            for comment in comments_list['items']:
                comments_replies_dictionary = dict()
                comments_replies_dictionary['id'] = comment['id']
                comments_replies_dictionary['text'] = comment['snippet']['textDisplay']
                comments_replies_dictionary['parent_id'] = comment['snippet']['parentId']
                comments_replies_dictionary['author'] = comment['snippet']['authorDisplayName']
                comments_replies_dictionary['like_count'] = comment['snippet']['likeCount']
                comments_replies_dictionary['published'] = comment['snippet']['publishedAt']
                comments_replies_dictionary['updated'] = comment['snippet']['updatedAt']
                comments_dictionary['replies'].append(comments_replies_dictionary)
        comments_list_request = comments_list_resource.list( part = 'snippet', maxResults = 100,  parentId = comment_thread_id, 
        textFormat = 'plainText', pageToken = next_page_token )    
    #return dictionary filled with replies datas
    return comments_dictionary

#this class is for getting path and name download video
class getNameAndPath(object):
    def __init__(self):
        self.tmp = list()

    def update(self, d):
        if d['status'] == 'finished':
            self.tmp.append(d['filename'])

    def get(self):
        return self.tmp

#function download video
def download_video(videoId, fetchAllFormats, outputdir="/tmp/youtube_output/", outputtemplate="%(id)s_%(format)s.%(ext)s", quiet=False):
    nameAndPath = getNameAndPath()

    ydl_opts = {
        "logtostderr" : 1,
        "format" : "best",
        "outtmpl" : outputdir + outputtemplate,
        "progress_hooks" : [nameAndPath.update]
    }

    if fetchAllFormats:
        ydl_opts["format"] = "all"

    if quiet:
        ydl_opts["quiet"] = 1
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([videoId])
        except youtube_dl.utils.DownloadError as e:
            sys.stderr.write("Youtube download error exception. Original message -> " + e.message + "\n")

    return nameAndPath.get()
    
if __name__ == '__main__':
    main(sys.argv)
