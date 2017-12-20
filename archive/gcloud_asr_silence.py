
# coding: utf-8

import os
import argparse
import base64
import json
import time
import sys
import traceback

from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials

import math 
import numpy as np
import os
import tempfile as tmpf
import shutil
from pydub import AudioSegment
import subprocess as sp

from pydub.silence import detect_nonsilent
import math

from pydub.effects import normalize
from collections import Counter



#####Start of code based on the Google api sample######
DISCOVERY_URL = ('https://{api}.googleapis.com/$discovery/rest?'
                 'version={apiVersion}')

def get_speech_service():
	credentials = GoogleCredentials.get_application_default().create_scoped(['https://www.googleapis.com/auth/cloud-platform'])
	http = httplib2.Http()
	credentials.authorize(http)
	return discovery.build('speech', 'v1beta1', http=http, discoveryServiceUrl=DISCOVERY_URL)

def processResponse(response):
	output = ''
	if ("results" in response.keys()) \
	and (len(response['results']) != 0) \
	and ("alternatives" in response['results'][0].keys()) \
	and (len(response['results'][0]['alternatives']) != 0) \
	and ("transcript" in response['results'][0]['alternatives'][0].keys()):
		output = response['results'][0]['alternatives'][0]['transcript']
	else:
		print "Empty ASR output: ",response	
	return output

def transcribe_chunk(fpath,fr):
    #os.system('export GOOGLE_APPLICATION_CREDENTIALS='+gcloud_credentials_fpath)
    #execute_command(command_to_export(gcloud_credentials_fpath))
    with open(fpath, 'rb') as speech:
        speech_content = base64.b64encode(speech.read()) # Base64 encode the binary audio file for inclusion in the JSON request.
    
    service = get_speech_service()
    service_request = service.speech().syncrecognize(
        body={
            'config': {
                'encoding': 'flac',  # raw 16-bit signed LE samples
                'sampleRate': fr,  # 16 khz.
                'languageCode': 'en-US',  # a BCP-47 language tag
            },
            'audio': {
                'content': speech_content.decode('UTF-8')
                }
            })
    response = service_request.execute()
    output_result = processResponse(response)
    return output_result 
#####end of code based on the Google api sample######

def get_formatted_time(time_ms):
	a_min = 60 #secs
	a_hour = 60 #mins
	temp = time_ms / 1000
	time_ms = time_ms % 1000
	time_secs = temp % a_min
	temp /= a_min
	time_mins = temp % a_hour
	temp /= a_hour
	time_hrs = temp
	return str(time_hrs).zfill(2)+":"+str(time_mins).zfill(2)+":"+str(time_secs).zfill(2)+","+str(time_ms).zfill(3)

def update_srt_file(chunk_transcript,i,start,end,srt_file_path):
	srt_file_path.write(i)
	srt_file_path.write("\n")
	#time
	start_ftime = get_formatted_time(start)
	end_ftime = get_formatted_time(end)
	srt_file_path.write(start_ftime+" --> "+end_ftime)
	srt_file_path.write("\n")
	#text
	srt_file_path.write(chunk_transcript)
	srt_file_path.write("\n")
	srt_file_path.write("\n")

def command_to_convert_mp4_to_flac(fpath_in,fpath_out):
	cmd = "ffmpeg -i '"+fpath_in+"' -ac 1 '"+fpath_out+"'"
	return cmd

def execute_command(command):
	p = sp.Popen(command,
				bufsize=2048,
				shell=True,
				stdin=sp.PIPE,
				stdout=sp.PIPE,
				stderr=sp.PIPE,
				close_fds=(sys.platform != 'win32'))
	output = p.communicate()
	print("Executed : " + command)

#generates srt file for the given mp4 file
def generate_srt(fpath,part_len=5000):
	max_retries = 10
	wait_time = 60 #secs
	srt_file = None
	tmp_dir = None
	try:
		#load the input mp4 file
		#full_sound_wav = AudioSegment.from_file(fpath, format="mp4")
		#temp dir to hold all chunks 
		tmp_dir = os.path.dirname(fpath)+os.sep+"tmp" #tmpf.mkdtemp()
		if not os.path.exists(tmp_dir):
			os.makedirs(tmp_dir)
		#export mp4 to flac
		temp_fpath_splits = fpath.split(".")[0].split(os.sep)
		flac_file_name = temp_fpath_splits[len(temp_fpath_splits)-1]+".flac"
		flac_file_path = tmp_dir+os.sep+flac_file_name
		#full_sound_wav.export(flac_file_path,format="flac")
		execute_command(command_to_convert_mp4_to_flac(fpath,flac_file_path))
		#load the flac file
		full_sound_flac = normalize(AudioSegment.from_file(flac_file_path, format="flac"))
		full_sound_flac_len = full_sound_flac.__len__()
		#range selection params
		part_len = 3*1000 #ms
		fixed_part_len = 5*1000 #ms
		max_part_len = 5*1000
		num_parts = int(math.ceil(full_sound_flac_len / part_len))
		#mim silence duration
		msl = 500
		#silence threshold
		loudness_ms_list = []
		for ms_chunk in full_sound_flac:
			loudness_ms_list.append(round(ms_chunk.dBFS))
		loudness_ms_count = Counter(loudness_ms_list) 
		st = loudness_ms_count.most_common(1)[0][0] #Assuming that the max # of ms will be silence/lowest normalized loudness in a video
		#bookeeping params
		count = 0
		max_count = 25
		#
		is_found = True
		ranges = detect_nonsilent(full_sound_flac,min_silence_len=msl,silence_thresh=st)
		n = len(ranges)
		#
		# is_found = False
		# #find right params
		# print "Parameter search - start."
		# while not is_found:
		# 	count+=1
		# 	print "count: ",count," required_num_parts: ",num_parts
		# 	if count > max_count:
		# 		print "Unabel to find right params." 
		# 		break
		# 	ranges = detect_nonsilent(full_sound_flac,min_silence_len=msl,silence_thresh=st)
		# 	n = len(ranges)
		# 	print "n: ",n
		# 	if n < num_parts:
		# 		print "st old: ",st
		# 		st = st + (st*0.1)
		# 		print "st new: ",st
		# 	else:
		# 		is_found = True
		# 		print "found"
		# 	print "---"
		# print "Parameter search - end."
		if is_found:
			print "Found apt parameters."
			print "Adjusting the boundaried so that no words are missed."
			print "Ranges - start"
			range_count = 0
			prev = ranges[0]
			processed_ranges = []
			for cur_range in ranges[-(n-1):]:
				start = prev[0]
				if (cur_range[0] - start) <= max_part_len:
					end = cur_range[0]
					range_count+=1
					processed_ranges.append([start,end])
					print range_count," - ",[start,end]
				else:
					end = prev[1]
					processed_ranges.append([start,end])
					range_count+=1
					print range_count," - ",[start,end]
					processed_ranges.append([end,cur_range[0]])
					range_count+=1
					print range_count," - ",[end,cur_range[0]]
				prev = cur_range
			processed_ranges.append(prev)
			range_count+=1
			print range_count," - ",prev
			print "Ranges - end"			
			print "Aggregating short ranges..."
			#Aggregate very short ranges
			#Assumption: after aggregation, the segments > part_len will still contain voice content ~ part_len (not always true - TBD)
			aggr_ranges = []
			temp_range = processed_ranges[0]
			count = 0
			temp_range_duration = 0
			n_processed = len(processed_ranges)
			print "#processed ranges: ",n_processed
			for cur_range in processed_ranges[-(n_processed-1):]:
				count+=1
				print "count: ",count
				temp_range_duration = temp_range[1]-temp_range[0]
				if temp_range_duration >= part_len:
					if temp_range_duration <= max_part_len:
						print "Added to aggr. list: ",(temp_range_duration/1000.0)," : ",temp_range
						aggr_ranges.append(temp_range)
					else:
						temp_start = temp_range[0]
						temp_n = math.floor(temp_range_duration/fixed_part_len)
						print "Longer than permitted. ",(temp_range_duration/1000.0)," : ",temp_range 
						print "Splitting to ",temp_n," fixed length chunks of length ",fixed_part_len
						print "----"
						for temp_i in np.arange(temp_n-1):
							temp_end = temp_start + fixed_part_len
							aggr_ranges.append([temp_start,temp_end])
							print temp_i," : ",[temp_start,temp_end]
							temp_start = temp_end
						aggr_ranges.append([temp_start,temp_range[1]])
						temp_i+=1
						print temp_i," : ",[temp_start,temp_range[1]]
						print "----"
					temp_range = cur_range
				else:
					if cur_range[1]-temp_range[0] < max_part_len: 
						temp_range[1] = cur_range[1] #temp_range_end <- cur_range_end
						print "Added to prev chunk. ",(temp_range_duration/1000.0),", ",temp_range
					else:
						print "Cound not add to prev chunk. Adding separately. ",(temp_range_duration/1000.0)," : ",temp_range
						aggr_ranges.append(temp_range)
						temp_range = cur_range
				print "---"
			#generate srt
			srt_file_path = fpath.split(".")[0]+".srt"
			srt_file = open(srt_file_path,"w")
			print "Generating SRT: ",srt_file_path
			print "Total aggr_ranges: ",len(aggr_ranges)
			count = 0
			larger_chunk = 0
			for cur_range in aggr_ranges:
				count+=1
				#update indices
				start = cur_range[0]
				end = cur_range[1] 
				if cur_range[0] != 0 and (end-start) > 200:
					start_chunk = cur_range[0] - 200
				else:
					start_chunk = start
				print "Segment ",count,": ",start," to ",end, " (ms). Duration ",(end-start)/1000.0," secs."
				#reset retry count
				retry_count = 0
				#create temp chunk file
				chunk_transcript = ''
				cur_chunk_fname = "chunk_"+str(start)+"_"+str(end)+".flac"
				cur_chunk_fpath = tmp_dir + "/" + cur_chunk_fname
				full_sound_flac[start_chunk:end].export(cur_chunk_fpath,format="flac")
				if (end-start) <= max_part_len:
					#transcribe this chunk
					fr = full_sound_flac.frame_rate
					while True:
						try:
							stime = time.time()
							chunk_transcript = transcribe_chunk(cur_chunk_fpath,fr)
							etime = time.time()
							print "Took ",(etime-stime)," secs."
							print "chunk_transcript: ",chunk_transcript
						except Exception as e:
							print e
							traceback.print_exc()
							retry_count+=1
							if retry_count < max_retries:
								time.sleep(wait_time)
								print "Waited "+str(wait_time)+" secs. Retrying...(",str(retry_count),")"
								continue
						break 
				else:
					print "Chunk larger than allowed limit. ",(end-start)/1000.0," secs."
					larger_chunk+=1
				#update the srt file
				update_srt_file(chunk_transcript,str(count),start,end,srt_file)
		else:
			print "Apt Paramters could not be found. Exiting."
		print "-----"
		print "Total larger_chunk: ",larger_chunk
		print "Total chunks: ",len(aggr_ranges)
		print "-----"
	except Exception as e:
		print "Fatal Error occurred."    
		print e
	finally:
		#cleaning up
		if srt_file != None:
			srt_file.close()
		#shutil.rmtree(tmp_dir)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print 'Usage: python gcloud_asr.py path_to_mp4'
		sys.exit(0)
	fpath = sys.argv[1]
	generate_srt(fpath)
