#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import stat
import subprocess
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
    corpusdir = os.path.join(basedir, 'corpus')
    if os.path.isdir(corpusdir):
        rmtree(corpusdir)
    try:
        os.mkdir(corpusdir)
    except OSError:
        print('Creation of the directory {} failed' .format(corpusdir) )
    cmd = 'git clone https://github.com/MiloszKrajewski/SilesiaCorpus corpus'
    subprocess.call(cmd, shell=True)
    os.chdir(corpusdir)
    fnm = 'README.md'
    if os.path.isfile(fnm):
        os.remove(fnm)
    extension = '.zip'
    for item in os.listdir(corpusdir):  # loop through items in dir
        if item.endswith(extension):  # check for ".zip" extension
            file_name = os.path.abspath(item)  # get full path of files
            zip_ref = zipfile.ZipFile(file_name)  # create zipfile object
            zip_ref.extractall(corpusdir)  # extract file to dir
            zip_ref.close()  # close file
            os.remove(file_name)  # delete zipped file


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


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1]:
        install_neuro_corpus()
    else:
        install_silesia_corpus()
