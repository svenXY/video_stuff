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
#from pprint import pprint
import logging


class FFProbe(object):
    def __init__(self,video_file):
        self.logger = logging.getLogger('FFProbe')
        self.logger.debug("FFProbing %s" % video_file)
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

    def get_video_stream(self):
        for stream in self.streams:
            if stream['codec_type'] == 'video': 
                return stream 

    def get_audio_streams(self):
        return [ stream for stream in self.streams if stream['codec_type'] == 'audio']

    def get_attribute(self, stream_idx, attribute):
        for stream in self.streams:
            if stream['index'] == stream_idx: 
                try:
                    return str(stream[attribute])
                except KeyError:
                    self.logger.warn("Invalid attribute: %s" % attribute)
                    return ''
    
    def get_bitrate(self, idx):
        return "%dk" % ((int(self.get_attribute(idx, 'bit_rate'))/1000),)

    def get_codec(self, idx):
        return self.get_attribute(idx, 'codec_name')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ffp = FFProbe(sys.argv[1])
    print "All streams:"
    print "\n".join(["Stream %d: %s, %s, %s" % stream for stream in
                     ffp.summary()])
    print "Video streams:"
    print "\n".join(["Stream %d: %s, %s, %s" % stream for stream in
                     ffp.summary('video')])

    print len(ffp.streams)
    for a_str in ffp.streams[1:]:
        print a_str['index']
        print a_str['codec_name']
        print a_str['codec_long_name']


    print "Attribut bit_rate von Stream 2: %s" % str(ffp.get_attribute(2, 'bit_rate'))
    print "Attribut bit_rate von Stream 1: %s" % str(ffp.get_attribute(1, 'bit_rate'))
    print "Bitrate von Stream 2: %s" % ffp.get_bitrate(2)
    print "Bitrate von Stream 3: %s" % ffp.get_bitrate(3)
