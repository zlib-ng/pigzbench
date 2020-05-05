#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import argparse
import stat
import shutil
import subprocess
import platform
import zipfile
from distutils.dir_util import copy_tree

parser = argparse.ArgumentParser(description='Pigz script')
parser.add_argument('--rebuild', help='Rebuild', action='store_const', const=True, default=None)
args, unknown = parser.parse_known_args()


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
        print('Creation of the directory {} failed' .format(corpusdir))
    cmd = 'git clone https://github.com/MiloszKrajewski/SilesiaCorpus silesia'
    print("Installing "+corpusdir)
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
        print('Creation of the directory {} failed' .format(exedir))
    cmd = 'git clone https://github.com/neurolabusc/zlib-bench.git'
    subprocess.call(cmd, shell=True)
    indir = os.path.join(basedir, 'zlib-bench', 'corpus')
    tmpfile = os.path.join(indir, 'README')
    if os.path.isfile(tmpfile):
        os.remove(tmpfile)
    copy_tree(indir, corpusdir)
    indir = os.path.join(basedir, 'zlib-bench')
    rmtree(indir)


def compile_pigz(rebuild=True):
    """compile variants of pigz"""

    methods = [
        {'name': 'madler',
         'repository': 'https://github.com/madler/zlib',
         'branch': None},
        {'name': 'cloudflare',
         'repository': 'https://github.com/cloudflare/zlib',  # Only supports 64-bit builds
         'branch': None},
        {'name': 'ng',
         'repository': 'https://github.com/zlib-ng/zlib-ng',
         'branch': 'develop'}
    ]
    basedir = os.getcwd()
    exedir = os.path.join(basedir, 'exe')

    if os.path.isdir(exedir):
        rmtree(exedir)
    if not os.path.isdir(exedir):
        os.mkdir(exedir)

    ext = ''
    if platform.system() == 'Windows':
        ext = '.exe'

    for method in methods:
        os.chdir(basedir)

        pthreads4wdir = os.path.join(basedir, 'pthreads4w')
        if rebuild or not os.path.exists('pthreads4w') and platform.system() == 'Windows':
            cmd = 'git clone https://github.com/jwinarske/pthreads4w'
            subprocess.call(cmd, shell=True)

        zlibname = 'zlib-{0}'.format(method['name'])
        if rebuild or not os.path.exists(zlibname):
            if os.path.isdir(zlibname):
                rmtree(zlibname)
            print("Checking out zlib source code for {0}".format(method['name']))
            cmd = 'git clone {0} {1}'.format(method['repository'], zlibname)
            subprocess.call(cmd, shell=True)

        pigzname = 'pigz-{0}'.format(method['name'])
        if rebuild or not os.path.exists(pigzname):
            if os.path.isdir(pigzname):
                rmtree(pigzname)
            print("Checking out pigz source code for {0}".format(method['name']))
            cmd = 'git clone https://github.com/madler/pigz {0}'.format(pigzname)
            subprocess.call(cmd, shell=True)

        os.chdir(zlibname)
        if method['branch']:
            cmd = 'git checkout {0}'.format(method['branch'])
            subprocess.call(cmd, shell=True)

        pigzdir = os.path.join(basedir, pigzname)
        copy_tree(os.path.join(basedir, 'pigz'), pigzdir)
        builddir = os.path.join(pigzdir, 'build')
        if rebuild or not os.path.exists(builddir):
            if os.path.isdir(builddir):
                rmtree(builddir)
            os.mkdir(builddir)

        os.chdir(builddir)

        cmd = 'cmake  .. -DZLIB_ROOT:PATH=../{0} -DZLIB_COMPAT=ON -DBUILD_SHARED_LIBS=OFF'.format(zlibname)
        if platform.system() == 'Windows':
            cmd += ' -DPTHREADS4W_ROOT:PATH=../pthreads4w'
        subprocess.call(cmd, shell=True)

        cmd = 'cmake --build . --config Release'
        subprocess.call(cmd, shell=True)

        pigzexe = os.path.join(builddir, 'bin', 'pigz' + ext)
        if not os.path.exists(pigzexe):
            pigzexe = os.path.join(builddir, 'pigz' + ext)
        if not os.path.exists(pigzexe):
            pigzexe = os.path.join(builddir, 'Release', 'pigz' + ext)

        outnm = os.path.join(exedir, pigzname + ext)
        shutil.move(pigzexe, outnm)
        print(pigzexe + '->' + outnm)


if __name__ == '__main__':
    """compile variants of pigz and sample compression corpus"""

    if args.rebuild:
        install_neuro_corpus()
        install_silesia_corpus()

    compile_pigz(args.rebuild)
