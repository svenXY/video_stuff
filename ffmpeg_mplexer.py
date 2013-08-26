#!/usr/bin/env python
'''
ffmpeg can be used to multiplex and encode in one pass
but the syntax is quite crude.

After cutting and demultiplexing with ProjectX, you usually end up with files
ending in

m2v - the video
ac3 - the audio in AC3
mp2 (and sometines also -02.mp2) - audio in MPEG-2 - one for each language

If you want  to multiplex them all into one nice matroska container while at the
same time reenosing m2v to h264 and mp2 to aac, this will do it for you.

this is how it's supposed to look like:
ffmpeg -i my_movie.m2v -i my_movie.ac3 -i my_movie.mp2 -i my_movie-02.mp2 -vcodec libx264 -acodec:1 copy bla.mkv -acodec:2 libfaac -newaudio -acodec:3 libfaac -newaudio -map 0:0 -map 1:0 -map 2:0 -map 3:0
'''

import sys
import os.path
from subprocess import call

try:
    m2v_complete = sys.argv[1]
except IndexError:
    print "Usage: %s mvie.m2v" % sys.argv[0]
    sys.exit(1)

encoders = { 
    '.m2v':'libx264',
    '.mp2':'libfaac',
    '.ac3':'copy'
}

(path, m2v) = os.path.split(m2v_complete)

movie = os.path.splitext(m2v)[0]

map_num = 1
maps = [ '-map', '0:0' ]
encodes = [ '-vcodec', 'libx264' ]
inputs = [ '-i', m2v_complete ]


for ext in ['.ac3', '.mp2', '-02.mp2']:
    if os.path.exists(os.path.join(path, movie+ext)):
          realext = os.path.splitext(os.path.join(path, movie+ext))[1]
          inputs.append('-i')
          inputs.append(os.path.join(path, movie+ext))
          encodes.append("-acodec:%d" % map_num)
          encodes.append(encoders[realext])
          map_num>1 and  encodes.append('-newaudio')
          maps.append("-map")
          maps.append(str(map_num))
          map_num += 1

cmd = ['ffmpeg']
cmd.extend(inputs)
cmd.extend(encodes[0:2])
cmd.append(os.path.join(path, movie + '.mkv'))
cmd.extend(encodes[2:])
cmd.extend(maps)

print "Running the following command:"
print ' '.join(cmd)

ret = call(cmd)
sys.exit(ret)

