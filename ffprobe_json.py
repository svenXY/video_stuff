#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Name			:	
# Description	:	
# Author		: Sven Hergenhahn
#
# $Id$
# 
###################################################

import subprocess
import sys
import os
import json

class FFProbe(object):
    def __init__(self,video_file):
        self.video_file=video_file
        try:
            with open(os.devnull, 'w') as tempf:
                subprocess.check_call(["ffprobe","-h"],stdout=tempf,stderr=tempf)
        except:
            raise IOError('ffprobe not found.')
        if os.path.isfile(video_file):
            p = subprocess.Popen(["ffprobe","-show_streams", '-print_format', 'json',
                      '-loglevel', 'quiet', self.video_file],stdout=subprocess.PIPE,stderr=subprocess.PIPE)

            data = json.loads(''.join(p.stdout))
            self.streams = data['streams']
        else:
            raise IOError('No such media file '+self.video_file)

    def summary(self, stream_type=None):
        if stream_type:
            st = [ stream for stream in self.streams if
                       stream['codec_type'] == stream_type]
        else:
            st = self.streams

        return [ (s['index'], 
                  s['codec_type'],
                  s['codec_name'],
                  s['codec_long_name']) 
                for s in st if 'codec_name' in s
               ]

if __name__ == '__main__':
    ffp = FFProbe(sys.argv[1])
    print "All streams:"
    print "\n".join(["Stream %d: %s, %s, %s" % stream for stream in
                     ffp.summary()])
    print "Video streams:"
    print "\n".join(["Stream %d: %s, %s, %s" % stream for stream in
                     ffp.summary('video')])
