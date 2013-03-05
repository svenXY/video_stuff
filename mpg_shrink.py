#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Name          : resize_mpg.py	
# Description   : A script to resize DVD-compliant mpeg2 files to a certain size	
# Author        : Sven Hergenhahn
#
# $Id$
# 
###################################################

import os
import os.path
import sys
import argparse
import re
from subprocess import Popen, call, PIPE, STDOUT
from shutil     import rmtree
from time       import time
import logging

global logger
logging.basicConfig(level=logging.INFO, format="%(levelname)s: [%(name)s] %(message)s")
logger = logging.getLogger('mpg_shrink')

if sys.version_info < (2, 7):
    print "Only works with 2.7 or higher"
    sys.exit(1)

# helpers
px    = '~/bin/projectx -out %s %s'
m2vrequant = '/usr/bin/M2VRequantiser %f %i'
mplex = '/usr/bin/mplex -f8 %s -o %s' 

def main():
    start = time()

    parser = argparse.ArgumentParser(
        description='Shrink a DVD-compliant mpeg2 file', 
        epilog='The resulting file will have "_shrinked" appended')

    parser.add_argument('-f', '--file', metavar='FILE', dest="source", 
                        type=str, required=True, help='The source mpeg2 or m2v file')
    parser.add_argument('-s', '--size', metavar='SizeMB', dest='size', 
                        default=4450, type=int, 
                        help='The desired size in MB (default: 4450)')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', 
                        default=False, help='Be verbosive')
    parser.add_argument('-k', '--keep', dest='keep', action='store_true', 
                        default=False, help='Keep temporary files (out.*)')

    global args
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    global source
    source = args.source
    
    global filesize
    filesize = args.size*1024*1024

    # actually do something 
    v = Video(source, filesize)
    ret = v.resize_video()
    if ret:
        logger.warn('resizing returned with %d' % ret)
    v.multiplex()

    logger.debug("Processing complete. It took %d seconds" % (int(time() - start)))


class Video:
    '''
    Class containing the methods to demultiplex, resize and multiplex an mpeg2
    file. The file is first split into Tracks (see below)
    '''

    def __init__(self, source, filesize):
        self.source = source
        self.filesize = filesize
        self.tracks = []
        path, filename = os.path.split(self.source)
        root, ext = os.path.splitext(filename)
        outfile = ''.join([root, '_shrinked.mpg'])
        if ext == '.m2v':
            self.destination = os.path.normpath(
                os.path.join(path, "..", outfile)
            )
            self.tempdir = path
        else:
            self.destination = os.path.join(path, outfile)
            self.tempdir = os.path.join(path, root) 
            self.demultiplex()
        self._get_tracks()

    def demultiplex(self):
        try:
            logger.debug("Demultiplexing %s into %s" % (self.source, self.tempdir))
            try:
                os.mkdir(self.tempdir)
            except OSError, e:
                if e.errno == 17:
                    pass
            cmd = px % (self.tempdir, self.source)
            run(cmd, args.verbose)
        except AttributeError:
            print "File does probably not exist"
            sys.exit(1)

    def resize_video(self):
        self.calc_factor()
        video = [track for track 
                       in self.tracks 
                       if track.type == 'm2v']
        video[0].resize(self.factor, self.tempdir)

    def _get_tracks(self):        
        for file in os.listdir(self.tempdir):
            if not re.match('.*\.(m2v|mp2|ac3|mp3)$', file):
                continue
            if re.search('_requant', file):
                continue
            t = Track(self.tempdir, file)
            self.tracks.append(t)

    def calc_factor(self):
        audio_bytes = sum([track.size for track 
                                      in self.tracks 
                                      if track.type != 'm2v'
                          ]) 
        video_bytes = sum([track.size for track 
                                      in self.tracks 
                                      if track.type == 'm2v'
                          ]) 
        self.factor = round((float(video_bytes)/(self.filesize - audio_bytes)) * 1.04, 2)
        logger.debug("Factor is %f" % self.factor)
        

    def multiplex(self):
        logger.debug("Multiplexing to destination file %s" % self.destination)
        cmd = mplex % ( ' '.join([os.path.join(self.tempdir,track.filename) for track in self.tracks]), 
                       self.destination) 
        if run(cmd, args.verbose) == 0:
            logger.info("You should have a nice movie in %s" % self.destination )
            self.cleanup()
        else:
            logger.error("Something went wrong. Leavin tmp files for inspection" )

    def cleanup(self):
        if args.keep is False:
            rmtree(self.tempdir)


class Track:
    '''
    Class containing a stream (here called track). Tracks are either video or
    audio tracks. They together form a Video()
    '''

    def __init__(self, dir, filename):
        root, ext = os.path.splitext(filename)
        self.type = ext[1:]
        self.size = os.stat(os.path.join(dir, filename)).st_size
        self.filename = filename
        logger.debug("Track found: %s, %d bytes" % (self.filename, self.size))


    def resize(self, factor, dir):
        assert self.type == 'm2v'
        infile = self.filename
        size = os.path.getsize(os.path.join(dir, infile))
        outfile = re.sub('\.', '_requant.', infile)
        self.filename = outfile
        cmd = m2vrequant % (factor, size)
        logger.debug("Resizing Video track with factor %f" % factor)

        return comm(cmd, os.path.join(dir, infile), os.path.join(dir, outfile), args.verbose)


def run(cmd, loud=False):
    cmds = cmd.split()
    logger.debug(cmd)
    if loud:
        return call(cmds)
    else:
        return call(cmds, stdout=PIPE, stderr=STDOUT, shell=True)

def comm(cmd, In, Out, loud=False):
    cmds = cmd.split()
    logger.debug(cmd)
    out = open(Out, 'w');
    process = Popen(cmds, stdout=out, stdin=open(In),
                    close_fds=True)
    (stdoutdata, stderrdata) = process.communicate()
    return process.returncode

if __name__ == '__main__':
    main()


