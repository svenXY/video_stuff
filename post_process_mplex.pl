#!/usr/bin/perl

my $args = join(' ', @ARGV);
my (@files) = ($args =~ /"([^"]+)"/g);

my $outfile = $files[0];
$outfile =~ s/(\....)$/_new.mpg/;

open(my $log, '>', '/tmp/postproc.log');
print $log "arg: $_\n" for @files;
my $cmd = "/usr/bin/mplex -f8 -o '$outfile' " . join(' ', map{"'$_'"} @files);
print $log $cmd;
system $cmd;
close $log;



