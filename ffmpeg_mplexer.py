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
import os.path
from subprocess import call

try:
    m2v_complete = sys.argv[1]
except IndexError:
    print "Usage: %s movie.m2v" % sys.argv[0]
    sys.exit(1)

encoders = { 
    '.m2v':'libx264',
    '.mp2':'libfdk_aac',
    '.ac3':'copy'
}

tags = {
    '.mp2':'AAC',
    '.ac3':'AC3'
}

(path, m2v) = os.path.split(m2v_complete)

movie = os.path.splitext(m2v)[0]
movie_name = ' '.join( fields.capitalize() for fields in movie.split('_' )) 

map_num = 1
maps = [ '-map', '0:0' ]
encodes = [ '-c:v:0', 'libx264', '-preset', 'slow', '-crf', '20', '-vf',
           'yadif=0:-1:0,scale=1024:576,setsar=1/1']
inputs = [ '-i', m2v_complete ]
tag_cmd = ['mkvpropedit', 
           "%s.mkv" % os.path.join(path, movie),
           '--edit',
           'info',
           '--set',
           "title='%s'" % movie_name
          ]

for ext in ['.ac3', '.mp2', '-02.mp2']:
   if os.path.exists(os.path.join(path, movie+ext)):
         realext = os.path.splitext(os.path.join(path, movie+ext))[1]
         inputs.append('-i')
         inputs.append(os.path.join(path, movie+ext))
         encodes.append("-c:a:%d" % (map_num-1))
         encodes.append(encoders[realext])
         # map_num>1 and  encodes.append('-newaudio')
         maps.append("-map")
         maps.append("%d:0" % map_num)
         tag_cmd.append("--edit") 
         tag_cmd.append("track:a%d" % map_num)
         if map_num==2:
             tag_cmd.extend(['--set', 'flag-default=1'])
         else:
             tag_cmd.extend(['--set', 'flag-default=0'])
         tag_cmd.append("--set") 
         tag_cmd.append("name=%s" % tags[realext]) 
         tag_cmd.append("--set") 
         tag_cmd.append("language=%s" % 'ger') 
         map_num += 1

cmd = ['ffmpeg']
cmd.extend(inputs)
cmd.extend(maps)
cmd.extend(encodes)
cmd.append(os.path.join(path, movie + '.mkv'))

print "Running the following ffmpeg command to reencode and mux in one go:"
print ' '.join(cmd)

ret = call(cmd)

if ret == 0:
    print "Tagging Matroska file with mkvpropedit"
    print ' '.join(tag_cmd)
    ret = call(tag_cmd)

sys.exit(ret)

