#!/usr/bin/env python3

import os       
import gzip
import shutil
from glob import glob
import time
import mgzip
import sys
#import gzip

def _cmp(fnm, lvl):
    #print('>>>'+fnm)
    fh = open(fnm, "rb")
    #gh = mgzip.open(fnm + ".gz", "wb", compresslevel=lvl)
    #thread=8, blocksize=2*10**8
    #gh = gzip.open(fnm + ".gz", "wb", compresslevel=lvl)
    gh = mgzip.open(fnm + ".gz", "wb", compresslevel=lvl, blocksize=10**6)
    data = fh.read()
    gh.write(data)
    gh.close()

indir = os.path.join((os.path.dirname(os.path.realpath(__file__))), "corpus")
if (len(sys.argv) > 1):
    indir = sys.argv[1]
if (not os.path.isdir(indir)):
    print("Unable to find "+indir)
    sys.exit()
print('Method\tLevel\tms\tmb/s\t%')
for i in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
  t0 = time.time()
  size = 0
  nsize = 0
  for f in os.listdir(indir):
    if not os.path.isfile(os.path.join(indir, f)):
        continue;
    if f.startswith('.'):
        continue;
    if not f.endswith(".gz"):
        fnm = os.path.join(indir, f)
        _cmp(fnm, i)
        size = size + os.stat(fnm).st_size
        nsize = nsize + os.stat(fnm + ".gz").st_size
  seconds = time.time() - t0
  #bytesPerMb = 1024**2
  bytesPerMb = 1000000
  speed = (size / bytesPerMb)/seconds
  print("mgzip\t{}\t{:.0f}\t{:.0f}\t{:.2f}".format(i, seconds*1000, speed, nsize/size*100))
   
  #print("Compressed {:.2f} MB data in {:.2f} S, Speed: {:.2f} MB/s, Rate: {:.2f} %".format(size / bytesPerMb, seconds, speed, nsize/size*100))
            


