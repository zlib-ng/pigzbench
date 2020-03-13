#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# python3 c_decompress.py        : test compression for files in folder 'corpus'
# python3 c_decompress.py indir  : test compression for files in folder 'indir'

import sys
import os
import sys
import stat
import ntpath
import shutil
import subprocess
import time
import filecmp


def compress_corpus(
    exe,
    indir,
    tmpdir,
    ext='.gz',
    opts=' -q -f -k -',
    max_level=9,
    ):
    """
    compress all files  in folder 'indir' using 'exe' and save to folder 'tmpdir'
    
    Parameters
    ----------
    exe : str
        name of compression executable
    indir : str
        folder with files to compress
    tmpdir : str
        folder where compressed files are saved
    ext : str
        folder with input files to compress        
    opts : str
        command line options for executable (default, ' -f -k -')         
    max_level : int
        maximum compression level to test (default 9)
        
    """

    size = 0
    for lvl in range(1, max_level + 1):
        for f in os.listdir(indir):
            if not os.path.isfile(os.path.join(indir, f)):
                continue
            if f.startswith('.'):
                continue
            if not f.endswith('.zst') and not f.endswith('.gz') \
                and not f.endswith('.bz2'):
                fnm = os.path.join(indir, f)
                size = size + os.stat(fnm).st_size
                cmd = exe + ' -q -f -k -' + str(lvl) + ' "' + fnm + '"'
                subprocess.call(cmd, shell=True)
                outnm = ntpath.basename(fnm)
                fnm = fnm + ext
                if not os.path.isfile(fnm):
                    sys.exit('Unable to find ' + fnm)
                outnm = os.path.join(tmpdir, str(lvl) + '_' + outnm
                        + ext)
                shutil.move(fnm, outnm)
    bytes_per_mb = 1000000
    return size / bytes_per_mb


def decompress_corpus(
    exe,
    tmpdir,
    mb,
    ext='.gz',
    opts=' -q -f -k -d ',
    ):
    """
    decompress all files  in folder 'tmpdir' using 'exe' and save to folder 'tmpdir'
    
    Parameters
    ----------
    exe : str
        name of compression executable
    tmpdir : str
        folder with files to decompress
    ext : str
        folder with files to decompress        
    opts : str
        command line options for executable (default, ' -f -k -d ')         
        
    """

    print('Method\tms\tmb/s')
    meth = ntpath.basename(exe)
    t0 = time.time()
    for f in os.listdir(tmpdir):
        if not os.path.isfile(os.path.join(tmpdir, f)):
            continue
        if f.startswith('.'):
            continue
        if f.endswith(ext):
            fnm = os.path.join(tmpdir, f)
            cmd = exe + ' ' + opts + ' "' + fnm + '"'
            subprocess.call(cmd, shell=True)
    seconds = time.time() - t0
    speed = mb / seconds
    print('{}\t{:.0f}\t{:.2f}'.format(meth, seconds * 1000, speed))


def tst_alt(indir='./corpus', exe='pbzip2'):
    """
    time decompression for all files  in folder 'indir' using 'exe'
    
    Parameters
    ----------
    exe : str
        name of compression executable
    indir : str
        folder with files to compress/decompress      
        
    """

    if not os.path.exists(exe) and not shutil.which(exe):
        print('Skipping test: Unable to find "' + exe + '"')
        return ()
    executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
    if not os.path.isdir(indir):
        sys.exit('Run a_compile.py before running this script: Unable to find '
                  + indir)
    tmpdir = './temp'
    if os.path.isdir(tmpdir):
        shutil.rmtree(tmpdir)
    try:
        os.mkdir(tmpdir)
    except OSError:
        print('Unable to create folder "' + tmpdir + '"')
    if exe == 'pbzip2':
        mb = compress_corpus(exe, indir, tmpdir, '.bz2')
        decompress_corpus(exe, tmpdir, mb, '.bz2')
    elif exe == 'zstd':
        mb = compress_corpus(
            exe,
            indir,
            tmpdir,
            '.zst',
            ' -T0 -q -f -k -',
            19,
            )
        decompress_corpus(exe, tmpdir, mb, '.zst', ' -T0 -q -f -k -d ')
    else:
        print('Skipping test: Unknown compressor "' + exe + '"')
        return ()


def compress_corpus_gz(methods, indir, tmpdir):
    """
    compress all files  in folder 'indir' using each method
    
    Parameters
    ----------
    methods : list of str
        names of compression executables
    indir : str
        folder with files to compress/decompress      
    tmpdir : str
        temporary folder for storing files compress/decompress      
        
    """

    size = 0
    for method in methods:
        meth = ntpath.basename(method)
        for lvl in range(2, 10):
            for f in os.listdir(indir):
                if not os.path.isfile(os.path.join(indir, f)):
                    continue
                if f.startswith('.'):
                    continue
                if not f.endswith('.zst') and not f.endswith('.gz') \
                    and not f.endswith('.bz2'):
                    fnm = os.path.join(indir, f)
                    size = size + os.stat(fnm).st_size
                    cmd = method + ' -f -k -' + str(lvl) + ' "' + fnm \
                        + '"'
                    subprocess.call(cmd, shell=True)

                    # outnm=os.path.splitext(ntpath.basename(fnm))[0]

                    outnm = ntpath.basename(fnm)
                    fnm = fnm + '.gz'
                    if not os.path.isfile(fnm):
                        sys.exit('Unable to find ' + fnm)
                    outnm = os.path.join(tmpdir, meth + str(lvl) + '_'
                            + outnm + '.gz')
                    shutil.move(fnm, outnm)
    bytes_per_mb = 1000000
    return size / bytes_per_mb


def decompress_corpus_gz(methods, tmpdir, mb):
    """
    decompress all files  in folder 'tmpdir' using each method
    
    Parameters
    ----------
    methods : list of str
        names of compression executables
    tmpdir : str
        folder with files to decompress      
        
    """

    print('Method\tms\tmb/s')
    for method in methods:
        meth = ntpath.basename(method)
        t0 = time.time()
        for f in os.listdir(tmpdir):
            if not os.path.isfile(os.path.join(tmpdir, f)):
                continue
            if f.startswith('.'):
                continue
            if f.endswith('.gz'):
                fnm = os.path.join(tmpdir, f)
                cmd = method + ' -d -k -f -N "' + fnm + '"'
                subprocess.call(cmd, shell=True)
        seconds = time.time() - t0
        speed = mb / seconds
        print('{}\t{:.0f}\t{:.2f}'.format(meth, seconds * 1000, speed))


def decompress_corpus_validation_gz(methods, indir, tmpdir):
    """
    ensure compression/decompress of files does not corrupt data
    
    Parameters
    ----------
    methods : list of str
        names of compression executables
    indir : str
        folder with accurately uncompressed files      
    tmpdir : str
        temporary folder for files to compress/decompress      
        
    """

    err = 0
    for exe in methods:
        meth = ntpath.basename(exe)
        for f in os.listdir(tmpdir):
            if not os.path.isfile(os.path.join(tmpdir, f)):
                continue
            if f.startswith('.'):
                continue
            if f.endswith('.gz'):
                fnm = os.path.join(tmpdir, f)
                cmd = exe + ' -d -k -f -N "' + fnm + '"'
                subprocess.call(cmd, shell=True)
                fbase = os.path.splitext(f)[0]
                fbase = fbase.split('_', 1)[1]
                orignm = os.path.join(indir, fbase)
                decompnm = os.path.join(tmpdir, fbase)
                try:
                    if not filecmp.cmp(orignm, decompnm):
                        err = err + 1
                        print(meth + ' files do not match: ' + orignm \
                            + ' != ' + decompnm)
                except:
                    err = err + 1
                    print(meth + ' files do not exist: ' + orignm \
                        + ' != ' + decompnm)
    if err < 1:
        print('no errors detected during validation')


def tst_gz(indir='./corpus'):
    """
    test decompression speed and accuracy of files in folder indir
    
    Parameters
    ----------
    indir : str
        folder with uncompressed files to test (default, './corpus')     
        
    """

    methods = []
    if os.path.exists('gzip') or shutil.which('gzip'):
        methods.append('gzip')
    executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
    exedir = './exe'
    if not os.path.isdir(exedir):
        sys.exit('Run a_compile.py before running this script: Unable to find '
                  + exedir)
    tmpdir = './temp'
    if os.path.isdir(tmpdir):
        shutil.rmtree(tmpdir)
    try:
        os.mkdir(tmpdir)
    except OSError:
        print('Unable to create folder "' + tmpdir + '"')
    for exeName in os.listdir(exedir):
        exeName = os.path.join(exedir, exeName)
        if os.path.isfile(exeName):
            st = os.stat(exeName)
            mode = st.st_mode
            if mode & executable:
                exeName = os.path.abspath(exeName)
                methods.append(exeName)
    mb = compress_corpus_gz(methods, indir, tmpdir)
    decompress_corpus_gz(methods, tmpdir, mb)
    decompress_corpus_validation_gz(methods, indir, tmpdir)


if __name__ == '__main__':
    indir = './corpus'
    if len(sys.argv) > 1:
        indir = sys.argv[1]
    if not os.path.isdir(indir):
        sys.exit('Run 1compile.py before running this script: Unable to find '
                  + indir)
    tst_gz(indir)
    tst_alt(indir, 'zstd')
    tst_alt(indir, 'pbzip2')
