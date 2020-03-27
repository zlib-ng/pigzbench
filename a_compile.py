#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import stat
import shutil
import subprocess
import platform
import zipfile
from distutils.dir_util import copy_tree

def rmtree(top):
    """Delete folder and contents: shutil.rmtree has issues with read-only files on Windows"""

    for (root, dirs, files) in os.walk(top, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR)
            os.remove(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)

def install_silesia_corpus():
    """Install popular Silesia corpus"""

    basedir = os.getcwd()
    corpusdir = os.path.join(basedir, 'silesia')
    if os.path.isdir(corpusdir):
        rmtree(corpusdir)
    try:
        os.mkdir(corpusdir)
    except OSError:
        print('Creation of the directory {} failed' .format(corpusdir) )
    cmd = 'git clone https://github.com/MiloszKrajewski/SilesiaCorpus silesia'
    print("Installing "+corpusdir);
    subprocess.call(cmd, shell=True)
    os.chdir(corpusdir)
    fnm = 'README.md'
    if os.path.isfile(fnm):
        os.remove(fnm)
    ext = '.zip'
    for item in os.listdir(corpusdir):  # loop through items in dir
        print("+"+item)
        if item.endswith(ext):  # check for ".zip" extension
            file_name = os.path.abspath(item)  # get full path of files
            print(file_name)
            zip_ref = zipfile.ZipFile(file_name)  # create zipfile object
            zip_ref.extractall(corpusdir)  # extract file to dir
            zip_ref.close()  # close file
            os.remove(file_name)  # delete zipped file
    os.chdir(basedir)

def install_neuro_corpus():
    """Install neuroimaging corpus"""

    basedir = os.getcwd()
    corpusdir = os.path.join(basedir, 'corpus')
    if os.path.isdir(corpusdir):
        rmtree(corpusdir)
    try:
        os.mkdir(corpusdir)
    except OSError:
        print('Creation of the directory {} failed' .format(exedir) )
    cmd = 'git clone https://github.com/neurolabusc/zlib-bench.git'
    subprocess.call(cmd, shell=True)
    indir = os.path.join(basedir, 'zlib-bench', 'corpus')
    tmpfile = os.path.join(indir, 'README')
    if os.path.isfile(tmpfile):
        os.remove(tmpfile)
    copy_tree(indir, corpusdir)
    indir = os.path.join(basedir, 'zlib-bench')
    rmtree(indir)

def compile_pigz():
    """compile variants of pigz"""

    methods = ['Cloudflare', 'System', 'ng']
    if platform.system() == 'Windows':
        methods = ['Cloudflare', 'ng']
    basedir = os.getcwd()
    exedir = os.path.join(basedir, 'exe')
    if os.path.isdir(exedir):
        rmtree(exedir)
    try:
        os.mkdir(exedir)
    except OSError:
        print ("Creation of the directory {} failed" .format(exedir) )
    pigzdir = './pigz'
    if os.path.isdir(pigzdir):
        rmtree(pigzdir)
    cmd = 'git clone https://github.com/neurolabusc/pigz'
    subprocess.call(cmd, shell=True)
    pigzdir = os.path.join(basedir, 'pigz', 'build')
    pigzexe = os.path.join(pigzdir, 'bin', 'pigz')
    ext = ''
    if platform.system() == 'Windows':
        ext = '.exe'
    pigzexe = pigzexe + ext
    for method in methods:
        os.chdir(basedir)
        if os.path.isdir(pigzdir):
            rmtree(pigzdir)
        os.mkdir(pigzdir)
        os.chdir(pigzdir)
        cmd = 'cmake -DZLIB_IMPLEMENTATION=' + method + ' ..'
        subprocess.call(cmd, shell=True)
        cmd = 'make'
        if platform.system() == 'Windows':
            cmd = 'cmake --build . --config Release'
        subprocess.call(cmd, shell=True)
        outnm = os.path.join(exedir, 'pigz' + method + ext)
        print (pigzexe + '->' + outnm)
        shutil.move(pigzexe, outnm)


if __name__ == '__main__':
    """compile variants of pigz and sample compression corpus"""

    install_neuro_corpus()
    install_silesia_corpus()
    compile_pigz()
