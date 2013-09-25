#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
# Name			: preprocess_dreambox_ts_file.py	
# Description	: rename a ts and ts.meta file according to it's metadata
                  and place them in a properly named subdirectory for 
                  further processing	
# Author		: Sven Hergenhahn
'''

import os
import sys
import argparse

class ExistsError(Exception):
    def __init__(self, file):
        self.msg = "File exists already: %s" % file
    def __str__(self):
        return self.msg

        pass

def get_movie_name(meta_file):
    try:
        with open(meta_file) as meta:
            (name, description) = meta.readlines()[1:3]

    except IOError, e:
        print "Problem with meta file: %s" % e
        sys.exit(1)

    if name != description:
        name = name.rstrip() + '-' + description.rstrip()
    else:
        name = name.rstrip()
        
    name = name.replace(' ', '_')
    name = name.replace('/', '-')
    print "Movie name taken from meta file: %s" % name
    return name

def restructure(tsfile, meta_file, movie_name, force=False):
    try:
        os.mkdir(movie_name)
    except OSError, e:
        if e.errno == 17:
            print "Directory %s exists, continuing anyway" % movie_name
            pass
    try:
        for ext in ['.ts', '.ts.meta' ]:
            file = os.path.join(movie_name, movie_name + ext)
            if os.path.exists(file):
                raise ExistsError(file)

    except ExistsError, e:
        if force:
            print "--force is set, overwriting files"
        else:
            print e
            return

    os.rename(tsfile, os.path.join(movie_name, movie_name + '.ts'))
    os.rename(meta_file, os.path.join(movie_name, movie_name + '.ts.meta'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='%(prog)s [options] <movie.ts> [<movie2.ts>, ...]')
    parser.add_argument("--force", '-f', help="Overwrite files in destination directory", action="store_true")
    parser.add_argument("tsfile", help='one or more TS files', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.tsfile:
        parser.error('Missing TS file(s)')

    for tsfile in args.tsfile:
        if not tsfile.endswith('.ts'):
            parser.print_usage()
            print 'File %s is not a TS file. Skipping.' % tsfile
            continue

        print "## Processing %s" % tsfile

        meta_file = tsfile + '.meta'

        movie_name = get_movie_name(meta_file)
        restructure(tsfile, meta_file, movie_name, force=args.force)

