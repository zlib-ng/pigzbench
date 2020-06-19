#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# python3 2test.py          : compress files of folder 'corpus' at level 6
# python3 2test.py indir    : compress files of folder 'indir' at level 6
# python3 2test.py indir 2  : compress files of folder 'indir' at level 2

import os
import sys
import stat
import shutil
import pandas as pd
import psutil
import ntpath
import subprocess
import time
#import distutils.spawn

def _cmp(
    exe,
    fnm,
    lvl,
    threads,
    ):
    """Use executable 'exe' to compress file 'fnm' at level 'lvl' with 'threads' cores"""

    env = os.environ
    if threads < 1:
        cmd = exe + ' -f -k -' + str(lvl) + ' "' + fnm + '"'
    else:
        cmd = exe + ' -f -k -' + str(lvl) + ' -p ' + str(threads) \
            + ' "' + fnm + '"'
    subprocess.call(cmd, shell=True)


def test_cmp(exe='gzip', indir='', max_threads=0, repeats = 1, resultsFile = 'gz.pkl'):
    """Test compression of executable 'exe' for files in folder 'indir' up to 'max_threads' cores"""

    if len(indir) < 1:
        indir = \
            os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         'corpus')
    if not os.path.isdir(indir):
        print('Unable to find ' + indir)
        sys.exit()
    if not os.path.exists(exe) and not shutil.which(exe):
    #if not os.path.exists(exe) and not distutils.spawn.find_executable(exe):
        print('Skipping test: Unable to find "' + exe + '"')
        return ()
    meth = ntpath.basename(exe)
    print('exe\tlevel\tms\tmb/s\t%\tthreads')
    threads = 0
    while threads <= max_threads:
        for level in [3, 6, 9]:
            seconds = float("inf")
            size = 0
            nsize = 0
            for rep in range(repeats):
                t0 = time.time()
                for f in os.listdir(indir):
                    if not os.path.isfile(os.path.join(indir, f)):
                        continue
                    if f.startswith('.'):
                        continue
                    if not f.endswith('.zst') and not f.endswith('.gz') \
                        and not f.endswith('.bz2'):
                        fnm = os.path.join(indir, f)
                        _cmp(exe, fnm, level, threads)
                        if rep > 0:
                            continue
                        size = size + os.stat(fnm).st_size
                        fnmz = fnm + '.gz'
                        if os.path.isfile(fnmz):
                            nsize = nsize + os.stat(fnmz).st_size
                        else:
                            print('Error: missing "' + fnmz + '"')
                seconds = min(seconds, time.time() - t0)
            bytes_per_mb = 1000000
            speed = size / bytes_per_mb / seconds
            print('{}\t{}\t{:.0f}\t{:.0f}\t{:.2f}\t{}'.format(
                meth,
                level,
                seconds * 1000,
                speed,
                nsize / size * 100,
                threads,
                ))
            threads0 = threads
            if threads0 < 1:
                threads0 = max_threads + 1
            row_df = pd.DataFrame([[meth, nsize / size * 100, speed,
                                  level, threads0]])
            if threads < 1 and max_threads < 1:

                # for gzip we only test 1 thread, we need two points to show up on a line plot

                row_df0 = pd.DataFrame([[meth, nsize / size * 100,
                        speed, level, 0]])
                row_df = pd.concat([row_df, row_df0], ignore_index=True)
            row_df.columns = ['exe', 'size %', ' speed mb/s   ', 'level'
                              , 'threads']
            try:
                df = pd.read_pickle(resultsFile)
                df = pd.concat([row_df, df], ignore_index=True)
            except (OSError, IOError) as e:
                df = row_df
            df.to_pickle(resultsFile)
        inc = max(threads, 1)
        inc = min(inc, 4)
        threads = threads + inc
        # clean up
        for f in os.listdir(indir):
            if not os.path.isfile(os.path.join(indir, f)):
                continue
            if f.endswith('.zst') or f.endswith('.gz') \
                or f.endswith('.bz2'):
                fnm = os.path.join(indir, f)
                os.remove(fnm)


def plot(resultsFile):
    """Generate line-plot showing how compression speed increases with threads"""

    if not os.path.exists(resultsFile):
        print('No file named "' + resultsFile + '"')
        return ()
    if os.name == 'posix' and 'DISPLAY' not in os.environ:
        print('Plot the results on a machine with a graphical display')
        return ()
    import seaborn as sns
    import matplotlib.pyplot as plt
    df = pd.read_pickle(resultsFile)
    sns.set()
    ax = sns.lineplot(x=' speed mb/s   ', y='threads', hue='exe',
                      style='level', data=df, marker='o')
    ax.set_title('Parallel Compression Speed')
    #plt.show()
    plt.savefig(resultsFile.replace('.pkl', '.png'))


if __name__ == '__main__':
    """Compare speed and size for different compression tools

    Parameters
    ----------
    indir : str
        folder with files to compress (default './corpus')
    repeats : int
     how many times is each file compressed (default 3)    
    """

    indir = './silesia'
    if len(sys.argv) > 1:
        indir = sys.argv[1]
    if not os.path.isdir(indir):
        sys.exit('Run a_compile.py first: Unable to find ' + indir)
    repeats = 7
    if len(sys.argv) > 2:
        repeats = int(sys.argv[2])
    exedir = './exe'
    if not os.path.isdir(exedir):
        sys.exit('Run 1compile.py before first: Unable to find '+ exedir)
    resultsFile = ntpath.basename(indir)+'_speed_threads.pkl'
    if os.path.exists(resultsFile):
        os.remove(resultsFile)
    max_threads = psutil.cpu_count(logical = False)
    test_cmp('gzip', indir, 0, repeats, resultsFile)
    for exe in os.listdir(exedir):
        exe = os.path.join(exedir, exe)
        if os.path.isfile(exe):
            st = os.stat(exe)
            mode = st.st_mode
            executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
            if mode & executable:
                exe = os.path.abspath(exe)
                test_cmp(exe, indir, max_threads, repeats, resultsFile)
    plot(resultsFile)
