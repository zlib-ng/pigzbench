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
import filecmp
import subprocess
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def _cmp(
    exe,
    fnm,
    lvl,
    opts=' -f -k -'):
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
    exts=['.gz', '.zstd']
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
    print('CompressMethod\tLevel\tms\tmb/s\t%')
    for lvl in range(2, max_level + 1):
        size = 0
        nsize = 0
        seconds = float("inf")
        for rep in range(repeats):
            rep_seconds = time.time()
            for f in os.listdir(indir):
                if not os.path.isfile(os.path.join(indir, f)):
                    continue
                if f.startswith('.'):
                    continue
                if f.endswith(tuple(exts)):
                    continue
                fnm = os.path.join(indir, f)
                _cmp(exe, fnm, lvl, opts)
                if rep > 0:
                    continue
                size = size + os.stat(fnm).st_size
                nsize = nsize + os.stat(fnm + ext).st_size
            rep_seconds = time.time() - rep_seconds
            seconds = min(seconds, rep_seconds)
        size = size
        nsize = nsize
      # bytes_per_mb = 1024**2

        bytes_per_mb = 1000000
        speed = size / bytes_per_mb / seconds
        print('{}\t{}\t{:.0f}\t{:.0f}\t{:.2f}'.format(meth, lvl,
                seconds * 1000, speed, nsize / size * 100))
        row_df = pd.DataFrame([[meth, nsize / size * 100, speed, lvl]])
        row_df.columns = ['exe', 'size %', 'speed mb/s', 'level']
        results_file = ntpath.basename(indir)+'_speed_size.pkl'
        try:
            df = pd.read_pickle(results_file)
            df = pd.concat([row_df, df], ignore_index=True)
        except (OSError, IOError) as e:
            df = row_df
        df.to_pickle(results_file)
    # clean up
    for f in os.listdir(indir):
        if not os.path.isfile(os.path.join(indir, f)):
            continue
        if f.endswith(tuple(exts)):
            fnm = os.path.join(indir, f)
            os.remove(fnm)

def plot(results_file):
    """line-plot showing how compression level impacts file size and conpression speed

    Parameters
    ----------
    results_file : str
        name of pickle format file to plot  
    """

    #if os.name == 'posix' and 'DISPLAY' not in os.environ:
    #    print('Plot the results on a machine with a graphical display')
    #    exit()
    df = pd.read_pickle(results_file)
    sns.set()
    sns_plot = sns.lineplot(x='speed mb/s', y='size %', hue='exe', data=df)
    #plt.show()
    plt.savefig(results_file.replace('.pkl', '.png'))

def validate_decompress_corpus(exe, indir, tmpdir):
    """
    time decompression of all files in folder 'indir'
    
    Parameters
    ----------
    exe : dictionary
       'exe' : str, exectuable name, e.g. 'zstd'
       'uncompress': str, arguments, e.g.  ' -T0 -q -f -k -d '
       'compress': str, arguemnt for compression, e.g. ' -T0 -q -f -k -' 
       'max_level': int, maximum supported compression level, eg 19, 
       'ext': extension used by this compressor, e.g. '.zst'
    indir : str
        folder with refence copies of uncompressed files 
    tmpdir : str
        folder with files to decompress 
     
    size_mb : float
        uncompressed size for all files in indir
    repeats : int
        number of times each item is decompressed

    """

    method = exe['exe']
    ext = exe['ext']
    opt = exe['uncompress']
    meth = ntpath.basename(method)
    if not os.path.exists(method) and not shutil.which(method):
        print('Skipping test: Unable to find "' + method + '"')
        return ()
    for f in os.listdir(tmpdir):
        if not os.path.isfile(os.path.join(tmpdir, f)):
            continue
        if f.startswith('.'):
            continue
        if f.endswith(ext):
            fnm = os.path.join(tmpdir, f)
            cmd = method + ' ' + opt + ' "' + fnm + '"'
            subprocess.call(cmd, shell=True)
            fbase = os.path.splitext(f)[0]
            decompnm = os.path.join(tmpdir, fbase)
            if not os.path.isfile(decompnm):
                sys.exit('Unable to find decompressed ' + decompnm)
            fbase = fbase.split('_', 1)[1]
            orignm = os.path.join(indir, fbase)
            if not os.path.isfile(orignm):
                sys.exit('Unable to find reference ' + orignm)
            if not filecmp.cmp(orignm, decompnm):
                sys.exit('Files differ "{}":{}'.format(orignm, decompnm))

def decompress_corpus(exe, indir, size_mb, repeats):
    """
    time decompression of all files in folder 'indir'
    
    Parameters
    ----------
    exe : dictionary
       'exe' : str, exectuable name, e.g. 'zstd'
       'uncompress': str, arguments, e.g.  ' -T0 -q -f -k -d '
       'compress': str, arguemnt for compression, e.g. ' -T0 -q -f -k -' 
       'max_level': int, maximum supported compression level, eg 19, 
       'ext': extension used by this compressor, e.g. '.zst'
    indir : str
        folder with files to decompress      
    size_mb : float
        uncompressed size for all files in indir
    repeats : int
        number of times each item is decompressed

    """

    method = exe['exe']
    ext = exe['ext']
    opt = exe['uncompress']
    meth = ntpath.basename(method)
    if not os.path.exists(method) and not shutil.which(method):
        print('Skipping test: Unable to find "' + method + '"')
        return ()
    seconds = float("inf")
    for r in range(repeats):
        rep_seconds = time.time()
        for f in os.listdir(indir):
            if not os.path.isfile(os.path.join(indir, f)):
                continue
            if f.startswith('.'):
                continue
            if f.endswith(ext):
                fnm = os.path.join(indir, f)
                cmd = method + ' ' + opt + ' "' + fnm + '"'
                subprocess.call(cmd, shell=True)
        rep_seconds = time.time() - rep_seconds
        seconds = min(seconds, rep_seconds)
    speed = (size_mb) / seconds
    print('{}\t{:.0f}\t{:.2f}'.format(meth, seconds * 1000, speed))

def compress_all_levels(exe, indir, tmpdir, exts):
    """
    compress all files in folder 'indir' and copy to 'tmpdir'
    
    Parameters
    ----------
    exe : dictionary
       'exe' : str, exectuable name, e.g. 'zstd'
       'uncompress': str, arguments, e.g.  ' -T0 -q -f -k -d '
       'compress': str, arguemnt for compression, e.g. ' -T0 -q -f -k -' 
       'max_level': int, maximum supported compression level, eg 19, 
       'ext': extension used by this compressor, e.g. '.zst'
    indir : str
        folder with files to compress      
    tmpdir : str
        temporary folder for storing files compress/decompress      
    tmpdir : list of str
        all possible comrpession extensions ['.zst', '.gz']     

    """

    size = 0
    method = exe['exe']
    ext = exe['ext']
    opt = exe['compress']
    max_level = exe['max_level']
    meth = ntpath.basename(method)
    if not os.path.exists(method) and not shutil.which(method):
        print('Skipping test: Unable to find "' + method + '"')
        return 0
    for lvl in range(2, max_level+1):
        for f in os.listdir(indir):
            if not os.path.isfile(os.path.join(indir, f)):
                continue
            if f.startswith('.'):
                continue
            if f.endswith(tuple(exts)):
                continue
            fnm = os.path.join(indir, f)
            size = size + os.stat(fnm).st_size
            cmd = method + opt + str(lvl) + ' "' + fnm + '"'
            subprocess.call(cmd, shell=True)
            outnm = ntpath.basename(fnm)
            fnm = fnm + ext
            if not os.path.isfile(fnm):
                sys.exit('Unable to find ' + fnm)
            outnm = os.path.join(tmpdir, meth + str(lvl) + '_' + outnm + ext)
            shutil.move(fnm, outnm)
    bytes_per_mb = 1000000
    return size / bytes_per_mb

def test_decomp(exes, indir, exts, repeats):
    """
    test decompression speed for all files in folder 'indir' using each exes
    
    Parameters
    ----------
    exes : dictionary where each entry has following properties
       'exe' : str, exectuable name, e.g. 'zstd'
       'uncompress': str, arguments, e.g.  ' -T0 -q -f -k -d '
       'compress': str, arguemnt for compression, e.g. ' -T0 -q -f -k -' 
       'max_level': int, maximum supported compression level, eg 19, 
       'ext': extension used by this compressor, e.g. '.zst'
    indir : str
        folder with files to compress/decompress      
    tmpdir : str
        temporary folder for storing files compress/decompress      
    tmpdir : list of str
        all possible comrpession extensions ['.zst', '.gz']     
    repeats : int
        number of times each item is decompressed
        performance estimate based on fastest run
        
    """

    tmpdir = './temp'
    if os.path.isdir(tmpdir):
        shutil.rmtree(tmpdir)
    try:
        os.mkdir(tmpdir)
    except OSError:
        sys.exit('Unable to create folder "' + tmpdir + '"')
    size_mb = 0;
    for  i in range(len(exes)) :
        size_mb += compress_all_levels(exes[i], indir, tmpdir, exts)
    print('DecompressMethod\tms\tmb/s')
    for  i in range(len(exes)) :
        decompress_corpus(exes[i], tmpdir, size_mb, repeats)
    for  i in range(len(exes)) :
        validate_decompress_corpus(exes[i], indir, tmpdir)
    
if __name__ == '__main__':
    """Compare speed and size for different compression tools

    Parameters
    ----------
    indir : str
        folder with files to compress (default './corpus')
    repeats : int
     how many times is each file compressed (default 3)    
    """

    indir = ''
    if len(sys.argv) > 1:
        indir = sys.argv[1]
    if len(indir) < 1:
        indir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'corpus')
    if not os.path.isdir(indir):
        print('Run a_compile.py first: Unable to find "' + indir +'"')
        sys.exit()
    repeats = 3
    if len(sys.argv) > 2:
        repeats = int(sys.argv[2])
    results_file = ntpath.basename(indir)+'_speed_size.pkl'
    if os.path.exists(results_file):
        os.remove(results_file)
    exes = []
    exes.append({'exe': 'zstd', 'uncompress': ' -T0 -q -f -k -d ', 'compress': ' -T0 -q -f -k -', 'max_level': 19, 'ext': '.zst' })
    #exes.append({'exe': 'pbzip2', 'uncompress': ' -q -f -k -d ', 'compress':  ' -q -f -k -', 'max_level': 9, 'ext': '.bz2' })
    exes.append({'exe': 'lbzip2', 'uncompress': ' -q -f -k -d ', 'compress':  ' -q -f -k -', 'max_level': 9, 'ext': '.bz2' })
    #exes.append({'exe': 'lz4', 'uncompress': ' -q -f -k -d ', 'compress':  ' -q -f -k -', 'max_level': 9, 'ext': '.lz4' })
    #exes.append({'exe': 'xz', 'uncompress': ' -T0 -q -f -k -d ', 'compress':  ' -T0 -q -f -k -', 'max_level': 9, 'ext': '.xz' })
    exes.append({'exe': 'gzip', 'uncompress': ' -q -f -k -d ', 'compress': ' -q -f -k -', 'max_level': 9, 'ext': '.gz' })
    executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
    exeDir = './exe'
    if not os.path.isdir(exeDir):
        print('Run a_compile.py first: Unable to find "' + exeDir +'"')
    else:
        for exe in os.listdir(exeDir):
            exe = os.path.join(exeDir, exe)
            if os.path.isfile(exe):
                st = os.stat(exe)
                mode = st.st_mode
                if mode & executable:
                    exe = os.path.abspath(exe)
                    exes.append({'exe': exe, 'uncompress': ' -q -f -k -d ', 'compress':  ' -q -f -k -', 'max_level': 9, 'ext': '.gz' })
    exts = []
    for  i in range(len(exes)) :
        ext = exes[i]['ext']
        if ext not in exts:
            exts.append(ext)
    for  i in range(len(exes)) :
        test_cmp(
            exes[i]['exe'],
            indir,
            repeats,
            exes[i]['ext'],
            exes[i]['compress'],
            exes[i]['max_level'],
            exts)
    plot(results_file)
    for  i in range(len(exts)) :
        ext = exts[i]
        exes2 = []
        for  i in range(len(exes)) :
            if exes[i]['ext'] == ext :
                exes2.append(exes[i])
        test_decomp(exes2, indir, exts, repeats)
