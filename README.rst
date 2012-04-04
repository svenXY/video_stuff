=============
mpg_shrink.py
=============
:Info: See `github <https://github.com/svenXY/video_stuff>`_ for the latest source.
:Author: Sven Hergenhahn <svenxy@gmx.net>

About
=====
When recording TV stuff, I usually end up with .ts files that I pull off my dreambox.

Sometimes those files are just too large to fit onto a single layer DVD, sometimes you want to burn a couple of movies (e.g. episodes) to one DVD. In any case you need to resize them. 

I'm doing most of my authoring work with tovid, but made bad experience with the mpeg reencoding part, mainly because the files are already DVD compliant. Anyway, in my toolchain I was missing a proper shrinker and here it is.

 
Usually, I tend to cut out ads and trim beginning and end. I usually do this with projectx, so I end up with an m2v file and it's friends (mp2 and ac3, ...).
Sometimes I already have a dvd compliant mpeg2-file.
Thus, the script either takes the path to the m2v-file or an mpeg2 file.

Using
-----

    # mpg_shrink.py [-h] -f FILE [-s SizeMB] [-v] [-k]
    
    Shrink a DVD-compliant mpeg2 file
    
    optional arguments:
      -h, --help            show this help message and exit
      -f FILE, --file FILE  The source mpeg2 or m2v file
      -s SizeMB, --size SizeMB
                            The desired size in MB (default: 4450)
      -v, --verbose         Be verbosive
      -k, --keep            Keep temporary files (out.*)

The resulting file will have "_shrinked" appended.

Requirements
------------

- tcrequant from transcode
- projectx

