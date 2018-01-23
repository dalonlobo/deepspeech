from __future__ import print_function
import youtube_dl
import os
import json
import codecs
import pickle
import pandas as pd
import sys

ROOT_DIR_PATH = ''

def getVideoIdsFromPlaylist(youtube_link):

	ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s', 'ignoreerrors': True})

	#with ydl:
	result = ydl.extract_info(youtube_link, download=False)

	allVideoLinks = []
	allVideoIDs = []

	if result == None:
		return None, None

	if 'entries' in result:
		videoentries = result['entries']
		print("length of video object is : ", len(videoentries))

		for eachentry in videoentries:
			if eachentry == None:
				continue
				
			videolink = eachentry['webpage_url']
			print("Entry is : ", videolink)
			allVideoLinks.append(videolink)
			videoid = getVideoIDFromURL(videolink)
			allVideoIDs.append(videoid)

	else:
		videoentry = result
		videolink = videoentry['webpage_url']
		allVideoLinks.append(videolink)
		videoid = getVideoIDFromURL(videolink)
		allVideoIDs.append(videoid)

	
	return allVideoLinks, allVideoIDs


def getPlaylistIDFromURL(youtube_link):

	if 'list=' not in youtube_link:
		return 'temp_playlist'

	length = len(youtube_link)
	index = youtube_link.find('list=')
	playlistid = youtube_link[index+5:length]

	return playlistid

def getChannelIDFromURL(youtube_link):

	#https://www.youtube.com/channel/UC5ZAemhQUQuNqW3c9Jkw8ug/videos

	urlcomponents = youtube_link.split('/')

	channelid = urlcomponents[4].strip()

	return channelid

def getVideoIDFromURL(youtube_link):

	#https://www.youtube.com/watch?v=UzxYlbK2c7E
	if '?v=' not in youtube_link:
		return None

	length = len(youtube_link)
	index = youtube_link.find('?v=')
	videoid = youtube_link[index+3:length]

	return videoid

def createDirectories(playlistid, videoids):

	playlistdirpath = ROOT_DIR_PATH + playlistid

	if not os.path.exists(playlistdirpath):
		os.makedirs(playlistdirpath)
		print("meta directory created at : ", playlistdirpath)

	"""
	count = 0 
	for eachvideoid in videoids:

		videodirpath = playlistdirpath + "/" + eachvideoid

		if not os.path.exists(videodirpath):
			os.makedirs(videodirpath)
			count = count + 1

	print "Sub-directories succssfully created ", count
	"""

def command_to_download_mp4video_and_srt_from_youtube(youtube_id, path, output_file_name_without_ext):
	#youtube-dl -o 'rK4sXm_MPWo.%(ext)s' -f mp4 --write-sub --sub-lang "en" --convert-subs srt https://www.youtube.com/watch?v=rK4sXm_MPWo --write-auto-sub
	cmd = "youtube-dl" + " -o '" + path + output_file_name_without_ext + ".%(ext)s' -f mp4 --write-sub --sub-lang 'en' --convert-subs srt --write-auto-sub --write-info-json --prefer-ffmpeg" \
		  " https://www.youtube.com/watch?v=" + youtube_id
	print("Built cmd: ", cmd)
	return cmd

def command_to_download_srt_from_youtube(youtube_id, path, output_file_name_without_ext):

	cmd = "youtube-dl" + " -o '" + path + output_file_name_without_ext + ".%(ext)s' --skip-download --write-sub --sub-lang 'en' --convert-subs srt --write-auto-sub --write-info-json --prefer-ffmpeg" \
		  " https://www.youtube.com/watch?v=" + youtube_id
	print("Built cmd: ", cmd)
	return cmd

def command_to_download_human_srt_from_youtube(youtube_id, path, output_file_name_without_ext):

	cmd = "youtube-dl" + " -o '" + path + output_file_name_without_ext + ".%(ext)s' --skip-download --write-sub --sub-lang 'en' --convert-subs srt --write-info-json --prefer-ffmpeg" \
		  " https://www.youtube.com/watch?v=" + youtube_id
	print("Built cmd: ", cmd)
	return cmd


def ffmpeg_command_to_convert_srt(eachvideoid, videodirpath):

	cmd = "ffmpeg" + " -i " + videodirpath + eachvideoid + ".en.vtt " + videodirpath + eachvideoid + ".en.srt"  
	print("Built ffmpeg cmd: ", cmd)
	return cmd

def run_command(cmd):
	try:
 		os.system(cmd)
	except Exception as e:
 		print("exception caught ", str(e))


def downloadSRTs(playlistid, videoids):

	for eachvideoid in videoids:
		videodirpath = ROOT_DIR_PATH + playlistid + "/"           #+ eachvideoid + "/"

		if not os.path.exists(videodirpath):
			os.makedirs(videodirpath)

		srtfilepath = videodirpath + eachvideoid + ".en.srt"

		if os.path.exists(srtfilepath):
			print("SRT already downloaded")
			continue

		cmd = command_to_download_srt_from_youtube(eachvideoid, videodirpath, eachvideoid)
		run_command(cmd)
		print("download command started")

		srtfilepath = videodirpath + eachvideoid + ".en.srt"

		vttfilepath = videodirpath + eachvideoid + ".en.vtt"

		if os.path.exists(srtfilepath):
			continue

		if not os.path.exists(vttfilepath):
			print("No vtt file, skipping ffmpeg command")
			continue

		ffmpeg_cmd = ffmpeg_command_to_convert_srt(eachvideoid, videodirpath)
		run_command(ffmpeg_cmd)
		print("ffmpeg download command started")



"""
def downloadSingleVideowithSRT(youtube_link, PATH_TO_DOWNLOAD):

	videoid = getVideoIDFromURL(youtube_link)
"""

def downloadHumanSRTs(playlistid, videoids):

	for eachvideoid in videoids:
		videodirpath = ROOT_DIR_PATH + playlistid + "/"           #+ eachvideoid + "/"

		if not os.path.exists(videodirpath):
			os.makedirs(videodirpath)

		srtfilepath = videodirpath + eachvideoid + ".en.srt"

		if os.path.exists(srtfilepath):
			print("SRT already downloaded")
			continue

		cmd = command_to_download_human_srt_from_youtube(eachvideoid, videodirpath, eachvideoid)
		run_command(cmd)
		print("download command started")

		srtfilepath = videodirpath + eachvideoid + ".en.srt"

		vttfilepath = videodirpath + eachvideoid + ".en.vtt"

		if os.path.exists(srtfilepath):
			continue

		if not os.path.exists(vttfilepath):
			print("No vtt file, skipping ffmpeg command")
			continue

		ffmpeg_cmd = ffmpeg_command_to_convert_srt(eachvideoid, videodirpath)
		run_command(ffmpeg_cmd)
		print("ffmpeg download command started")



def downloadVideos(playlistid, videoids):

	for eachvideoid in videoids:
		videodirpath = ROOT_DIR_PATH + playlistid + "/" + eachvideoid + "/"

		if not os.path.exists(videodirpath):
			os.makedirs(videodirpath)

		cmd = command_to_download_mp4video_and_srt_from_youtube(eachvideoid, videodirpath, eachvideoid)
		run_command(cmd)
		print("download command started")


def writeInfoFile(playlistid, videourls, videoids):

	playlistdirpath = ROOT_DIR_PATH + playlistid

	infofile = playlistdirpath + "/" + "info.txt"

	with open(infofile, 'w') as f:
		for videourl, videoid in zip(videourls, videoids):
			f.write(str(videourl) + "," + str(videoid) + "\n")
	


#videoid = getVideoIDFromURL('https://www.youtube.com/watch?v=UzxYlbK2c7E')
#playlistid = getPlaylistIDFromURL('https://www.youtube.com/watch?v=UzxYlbK2c7E&list=PLA89DCFA6ADACE599')
#print "testing video id and playlist ", videoid, playlistid

#allVideoLinks = getVideoIdsFromPlaylist('https://www.youtube.com/watch?v=UzxYlbK2c7E&list=PLA89DCFA6ADACE599')
#print "all video links are : ", len(allVideoLinks), str(allVideoLinks)

#downloadVideos('https://www.youtube.com/watch?v=SaxjBYNg6fs&list=PLEI1TXdLd0MbPEhxOaUVrYfefSqcSHTdY')

#main('https://www.youtube.com/watch?v=s8B4A5ubw6c&index=7&list=PLA89DCFA6ADACE599')
#command_to_download_mp4video_and_srt_from_youtube('SaxjBYNg6fs', '/home/kuldeep/bookextraction/videos/PLEI1TXdLd0MbPEhxOaUVrYfefSqcSHTdY/SaxjBYNg6fs/', 'SaxjBYNg6fs')

def downloadCategoryVideos():

	categoryVideoIndexFile = '/home/kuldeep/bookextraction/videos/PL/PL_videolinks.txt'

	f = open(categoryVideoIndexFile)

	for line in f:
		line = line.strip()
		if len(line) == 0:
			continue

		if '#' in line:
			print("finished : ", line)
			continue

		main(line)

	print("all download finished and placed at : ", ROOT_DIR_PATH)



def dumpPlaylistorChannelInfo(youtube_link, options):	 

	 if 'list' in youtube_link:
		playlistid = getPlaylistIDFromURL(youtube_link)
	 elif 'channel' in youtube_link:
	 	channelid = getChannelIDFromURL(youtube_link)
	 	playlistid = channelid

	 print("Playlist ID is ", playlistid)

	 playlistpath = ROOT_DIR_PATH + playlistid

	 if not os.path.exists(playlistpath):
	 	os.makedirs(playlistpath)

	 picklepath = playlistpath + "/videoinfodict.p"

	 if os.path.exists(picklepath):
	 	print("Reading the pickle")
	 	videoinfodict = pickle.load( open( picklepath, "rb" ) )
	 	allvideolinks = videoinfodict['allvideolinks']
	 	allvideoids = videoinfodict['allvideoids']

	 	print("length of allvideolinks and allvideoids : ", len(allvideolinks), len(allvideoids))
	 else:
	 	allvideolinks, allvideoids = getVideoIdsFromPlaylist(youtube_link)	
 	 
	 if allvideolinks == None:
	 	return

	 if options == 'v':

	 	with open(ROOT_DIR_PATH + playlistid + ".csv", "w") as f:
	 		for videoid in allvideoids:
	 			f.write(videoid + "\n")

	 	print("Written video ids to the file : ", len(allvideoids))
	 	return


	 videoinfodict = { "allvideolinks": allvideolinks, "allvideoids" : allvideoids}
	 picklepath = playlistpath + "/" + playlistid + "_videoinfodict.p"
	 pickle.dump( videoinfodict, open(picklepath, "wb" ))

	 with open(playlistpath + "/" + playlistid + "_videoids.csv", "w") as f:

	 	for videoid, videolink in zip(allvideoids, allvideolinks):
	 		f.write (videoid + "," + videolink  + "\n")

	 createDirectories(playlistid, allvideoids)
 	 #writeInfoFile(playlistid, allvideolinks, allvideoids)
 	 #downloadVideos(playlistid, allvideoids)
	 downloadHumanSRTs(playlistid, allvideoids)

	 for videoid, videolink  in zip(allvideoids, allvideolinks):
	 	 #videodirpath = ROOT_DIR_PATH + playlistid + "/" 
	 	 videoinfojsonpath = playlistpath + "/" + videoid + ".info.json"

	 	 vid_title = None
	 	 duration = 0

	 	 try:
	 	 	vid_title = json.load(codecs.open(videoinfojsonpath,"r","utf-8"))['fulltitle'].encode('utf-8') 
	 	 	duration = json.load(codecs.open(videoinfojsonpath,"r","utf-8"))['duration'] 
	 	 except Exception as e:
	 	 	print("Error in extracting video title ", str(e))
	 	 	vid_title = 'None'

	 	 print("vid_title is ",vid_title, duration)

	 	 srtfilepath = playlistpath + "/" + videoid + ".en.srt"

	 	 srtExist = False
	 	 if os.path.exists(srtfilepath):
	 	 	srtExist = True

	 	 with open(ROOT_DIR_PATH + playlistid + "_info.csv", "a") as f:
	 	 	 f.write (videoid + "\t" + str(duration) + "\t" + videolink + "\t" + str(srtExist) + "\n")


	 
	 print("Finished processing")
	
def main(youtube_link):

	 playlistid = getPlaylistIDFromURL(youtube_link)
 	 
	 #try:
	 allvideolinks, allvideoids = getVideoIdsFromPlaylist(youtube_link)
	 #except:
	#	print "Error while downloading playlist info: ", playlistid
	#	
	#	with open(ROOT_DIR_PATH + 'failedDownloads.txt', 'a') as f:
	#		f.write ("Error while downloading playlist info: " +  playlistid + "\n")


	#	return

	 if allvideolinks == None:
	 	return

#	 playlistid = sys.argv[2]

	 #if playlistid != '':
	 createDirectories(playlistid, allvideoids)
 	 #writeInfoFile(playlistid, allvideolinks, allvideoids)
 	 downloadVideos(playlistid, allvideoids)
	 #downloadSRTs(playlistid, allvideoids)
	 #downloadHumanSRTs(playlistid, allvideoids)

#downloadCategoryVideos()

if __name__ == '__main__':

	
	print("Arguments are : ", str(sys.argv))
	# V for video IDs, 'vi' for video id and information 
	#dumpPlaylistorChannelInfo(sys.argv[1], 'vi')   #'v' for dumping only video ids 
#	main(sys.argv[1])	
	df = pd.read_table('single_ted_video.xlsx', header=None)
	for index, playlistid in df.iterrows():
		print("Reading this playlist id: ", playlistid[0])
		main(playlistid[0])
	#playlistid = 'tcsdigital'
	#videoids = ['mM98zGIkr8Q','gQahEqw99fo','tfYx5ec_tTg','16BfEjrNzr4','yDOy5UewRZM','HsLSP8F4DqU','3PjwojBtLm8','ntn0O9BCNQI','BpgnnS7mKKU','r43LhSUUGTQ']

	#downloadSRTs(playlistid, videoids)



