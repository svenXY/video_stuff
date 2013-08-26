#!/usr/bin/env python

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

#ffmpeg -i short_11MB.m2v -i short_11MB.ac3 -i short_11MB.mp2 -i short_11MB-02.mp2 -vcodec libx264 -acodec:1 copy bla.mkv -acodec:2 libfaac -newaudio -acodec:3 libfaac -newaudio -map 0:0 -map 1:0 -map 2:0 -map 3:0
