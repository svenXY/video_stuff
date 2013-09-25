#!/usr/bin/env python
'''
Encode, mux and tag a matroska container video 

ffmpeg can be used to multiplex and encode in one pass
but the syntax is quite crude.

After cutting and demultiplexing with ProjectX, you usually end up with files
ending in

mkv - the video
ac3 - the audio in AC3
mp2 (and sometines also -02.mp2) - audio in MPEG-2 - one for each language

If you want  to multiplex them all into one nice matroska container while at the
same time reenosing mkv to h264 and mp2 to aac, this will do it for you.

this is how it's supposed to look like:
ffmpeg -i my_movie.mkv -i my_movie.ac3 -i my_movie.mp2 -i my_movie-02.mp2 \
        -vcodec libx264 -acodec:1 copy bla.mkv -acodec:2 libfaac -newaudio \
        -acodec:3 libfaac -newaudio -map 0:0 -map 1:0 -map 2:0 -map 3:0

It will also try to tag the matroska container with title, audio format and
language like so:
mkvpropedit my_movie.mkv --edit info --set "title=My Movie" \
        --edit track:a1 --set flag-default=0 --set name='AC3' --set language=ger \
        --edit track:a2 --set flag-default=1 --set name='AAC' --set language=ger \
        --edit track:a3 --set flag-default=0 --set name='AAC' --set language=ger
'''

import sys
import argparse
import os.path
from subprocess import call
from ffprobe_json import FFProbe

parser = argparse.ArgumentParser()
parser.add_argument('--file', '-f', metavar='FILENAME', required=True, dest='infile', help='the path of the mkv video')
parser.add_argument('--directory', '-D', metavar='Destination Dir', dest='outdir', help='an optional directory for the resulting files')

args = parser.parse_args()
mkv_orig = args.infile

out_scale = '_1024x576.mkv'

ffp = FFProbe(mkv_orig)

audio_streams = len(ffp.streams) - 1

(path, mkv) = os.path.split(mkv_orig)

movie = os.path.splitext(mkv)[0]
movie_name = ' '.join( fields.capitalize() for fields in movie.split('_' )) 

if args.outdir:
    outpath = os.path.join(args.outdir, movie + out_scale)
else:
    outpath = os.path.join(path, movie + out_scale)

maps = [ '-map', '0:0' ]
encodes = [ '-c:v:0', 'libx264', '-q:v', '0', '-vf',
           'scale=1024:576,setsar=1/1']
inputs = [ '-i', mkv_orig ]
tag_cmd = ['mkvpropedit', 
           outpath,
           '--edit',
           'info',
           '--set',
           "title='%s'" % movie_name
          ]

for a_stream in ffp.streams[1:]:
    idx = a_stream['index']
    encodes.append("-c:a:%d" % (idx-1))
    encodes.append('copy')
    maps.append("-map")
    maps.append("0:%d" % idx)
    tag_cmd.append("--edit") 
    tag_cmd.append("track:a%d" % idx)
    if idx==2:
        tag_cmd.extend(['--set', 'flag-default=1'])
    else:
        tag_cmd.extend(['--set', 'flag-default=0'])
    tag_cmd.append("--set") 
    tag_cmd.append("name=%s" % a_stream['codec_name']) 
    tag_cmd.append("--set") 
    tag_cmd.append("language=%s" % 'ger') 

cmd = ['ffmpeg']
cmd.extend(inputs)
cmd.extend(maps)
cmd.extend(encodes)
cmd.append(outpath)

print "Running the following ffmpeg command to reencode and mux in one go:"
print ' '.join(cmd)

ret = call(cmd)

if ret == 0:
    print "Tagging Matroska file with mkvpropedit"
    print ' '.join(tag_cmd)
    ret = call(tag_cmd)

sys.exit(ret)

