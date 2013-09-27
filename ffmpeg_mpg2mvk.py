#!/usr/bin/env python
'''
Encode, mux and tag a matroska container video 

ffmpeg can be used to multiplex and encode in one pass
but the syntax is quite crude.

After cutting and demultiplexing with ProjectX, you usually end up with files
ending in

m2v - the video (anamorphic 720x576 and probably interlaced)
ac3 - the audio in AC3
mp2 (and sometimes also -02.mp2) - audio in MPEG-2

If you want  to multiplex them all into one nice matroska container while at the
same time reencoding m2v to h264 and mp2 to aac (ac3 will be kept as it is), this will do it for you.

At the same time it will deinterlace if necessary (yadif) and remove anamorphism
(scale).

It will also try to tag the matroska container with title, audio format and
language
'''

import sys
import argparse
import logging
import os.path
from subprocess import call
#import pprint
from ffprobe_json import FFProbe

# create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s', '%H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)

parser = argparse.ArgumentParser()
parser.add_argument('--file', '-f', metavar='FILENAME', required=True, dest='infile', help='the path of the mkv video')
parser.add_argument('--directory', '-D', metavar='Destination Dir', dest='outdir', help='an optional directory for the resulting files')

args = parser.parse_args()

mpg_orig = args.infile

logger.info("Converting %s" % mpg_orig)

ffp = FFProbe(mpg_orig)

v_idx = int(ffp.get_video_stream()['index'])
a_idx = [int(stream['index']) for stream in ffp.get_audio_streams()]

encoders = { 
    'video':'libx264',
    'mp2':'libfdk_aac',
    'ac3':'copy'
}

tags = {
    'mp2':'AAC',
    'ac3':'AC3'
}

(path, mpg) = os.path.split(mpg_orig)

movie = os.path.splitext(mpg)[0]
movie_name = ' '.join( fields.capitalize() for fields in movie.split('_' )) 

maps = [ '-map', '0:%d'%v_idx ]
encodes = [ '-c:v:0', 'libx264', '-preset', 'slow', '-crf', '20', '-vf',
           'yadif=0:-1:0,scale=1024:576,setsar=1/1']
inputs = [ '-i', mpg_orig ]
tag_cmd = ['mkvpropedit', 
           "%s_1024x576.mkv" % os.path.join(path, movie),
           '--edit',
           'info',
           '--set',
           "title='%s'" % movie_name
          ]

loop_nr = 0
for stream_idx in a_idx:
    codec = ffp.get_codec(stream_idx)
    encodec = encoders[codec]
    encodes.append("-c:a:%d" % loop_nr)
    encodes.append(encodec)
    encodes.append("-b:a:%d" % loop_nr)
    encodes.append(ffp.get_bitrate(stream_idx))
    maps.append("-map")
    maps.append("0:%d" % stream_idx)
    tag_cmd.append("--edit") 
    tag_cmd.append("track:a%d" % (loop_nr+1,))
    if loop_nr==1:
        tag_cmd.extend(['--set', 'flag-default=1'])
    else:
        tag_cmd.extend(['--set', 'flag-default=0'])
    tag_cmd.append("--set") 
    tag_cmd.append("name=%s" % tags[codec]) 
    tag_cmd.append("--set") 
    tag_cmd.append("language=%s" % 'ger') 
    loop_nr += 1

cmd = ['ffmpeg']
cmd.extend(inputs)
cmd.extend(maps)
cmd.extend(encodes)
cmd.append(os.path.join(path, movie + '_1024x576.mkv'))

logger.info("Running the following ffmpeg command to convert mpg to mkv")
logger.info(' '.join(cmd))

ret = call(cmd)

if ret == 0:
    logger.debug("Tagging Matroska file with mkvpropedit")
    logger.debug(' '.join(tag_cmd))
    ret = call(tag_cmd)

sys.exit(ret)

