#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# python3 d_speed_size.py        : test speed/compression for folder 'corpus'
# python3 d_speed_size.py indir  : test speed/compression for folder 'indir'

import os
import sys
import stat
import time
import shutil
import ntpath
import subprocess
import pandas as pd


def _cmp(
    exe,
    fnm,
    lvl,
    opts=' -f -k -',
    ):
    """
    compress file 'fnm' using executable 'exe'
    
    Parameters
    ----------
    exe : str
        name of compression executable
    fnm : str
        name of file to be compressed
    lvl : int
        compression level
    opts : str
        command line options for executable (default, ' -f -k -')                
    """

    env = os.environ
    cmd = exe + opts + str(lvl) + ' "' + fnm + '"'
    subprocess.call(cmd, shell=True)


def test_cmp(
    exe='gzip',
    indir='',
    repeats=1,
    ext='.gz',
    opts=' -q -f -k -',
    max_level=9,
    ):
    """
    compress all files in folder 'indir' using executable 'exe'
    
    Parameters
    ----------
    exe : str
        name of compression executable
    indir : str
        name of folder with files to compress
    repeats : int
        how many times is each file compressed. More is slower but better timing accuracy
    ext : str
        extension for files created by exe (default, '.gz')
    opts : str
        command line options for executable (default, ' -f -k -')
    max_level : int
        maximum compression level to test (default 9)            
    """

    if not os.path.exists(exe) and not shutil.which(exe):
        print('Skipping test: Unable to find "' + exe + '"')
        return ()
    if len(indir) < 1:
        indir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'corpus')
    if not os.path.isdir(indir):
        print('Run a_compile.py first: Unable to find "' + indir +'"')
        sys.exit()
    meth = ntpath.basename(exe)
    print('Method\tLevel\tms\tmb/s\t%')
    for lvl in range(2, max_level + 1):
        t0 = time.time()
        size = 0
        nsize = 0
        for rep in range(repeats):
            for f in os.listdir(indir):
                if not os.path.isfile(os.path.join(indir, f)):
                    continue
                if f.startswith('.'):
                    continue
                if not f.endswith('.zst') and not f.endswith('.gz') \
                    and not f.endswith('.bz2'):
                    fnm = os.path.join(indir, f)
                    _cmp(exe, fnm, lvl, opts)
                    if rep > 0:
                        continue
                    size = size + os.stat(fnm).st_size
                    nsize = nsize + os.stat(fnm + ext).st_size
        size = size * repeats
        nsize = nsize * repeats
        seconds = time.time() - t0

      # bytes_per_mb = 1024**2

        bytes_per_mb = 1000000
        speed = size / bytes_per_mb / seconds
        print('{}\t{}\t{:.0f}\t{:.0f}\t{:.2f}'.format(meth, lvl,
                seconds * 1000, speed, nsize / size * 100))
        row_df = pd.DataFrame([[meth, nsize / size * 100, speed, lvl]])
        row_df.columns = ['exe', 'size %', 'speed mb/s', 'level']
        try:
            df = pd.read_pickle('speed_size.pkl')
            df = pd.concat([row_df, df], ignore_index=True)
        except (OSError, IOError) as e:
            df = row_df
        df.to_pickle('speed_size.pkl')

    # clean up

    for f in os.listdir(indir):
        if not os.path.isfile(os.path.join(indir, f)):
            continue
        if f.endswith('.zst') or f.endswith('.gz') or f.endswith('.bz2'
                ):
            fnm = os.path.join(indir, f)
            os.remove(fnm)


def plot(resultsFile):
    """line-plot showing how compression level impacts file size and conpression speed

    Parameters
    ----------
    resultsFile : str
        name of pickle format file to plot  
    """

    if os.name == 'posix' and 'DISPLAY' not in os.environ:
        print('Plot the results on a machine with a graphical display')
        exit()
    import seaborn as sns
    import matplotlib.pyplot as plt
    df = pd.read_pickle(resultsFile)
    sns.set()
    ax = sns.lineplot(x='speed mb/s', y='size %', hue='exe', data=df)
    plt.show()


if __name__ == '__main__':
    """Compare speed and size for different compression tools

    Parameters
    ----------
    indir : str
        folder with files to compress (default './corpus')
    repeats : int
     how many times is each file compressed. More (default 1)    
    """

    indir = ''
    if len(sys.argv) > 1:
        indir = sys.argv[1]
    repeats = 1
    if len(sys.argv) > 2:
        repeats = int(sys.argv[2])
    resultsFile = 'speed_size.pkl'
    if os.path.exists(resultsFile):
        os.remove(resultsFile)
    test_cmp('pbzip2', indir, repeats, '.bz2')
    test_cmp(
        'zstd',
        indir,
        repeats,
        '.zst',
        ' -T0 -q -f -k -',
        19,
        )
    test_cmp('gzip', indir, repeats)

    # test pigz variants

    executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
    exeDir = './exe'
    for exe in os.listdir(exeDir):
        exe = os.path.join(exeDir, exe)
        if os.path.isfile(exe):
            st = os.stat(exe)
            mode = st.st_mode
            if mode & executable:
                exe = os.path.abspath(exe)
                test_cmp(exe, indir, repeats)
    plot(resultsFile)
