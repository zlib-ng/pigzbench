#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import stat
import shutil
import subprocess
import platform
import _install_corpus as corpus


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


def compile_pigz():
    """compile system variant of pigz"""

    method = 'System'
    basedir = os.getcwd()
    exedir = os.path.join(basedir, 'exe')
    if os.path.isdir(exedir):
        rmtree(exedir)
    try:
        os.mkdir(exedir)
    except OSError:
        print('Unable to create folder "' + exedir +'"')
    pigzdir = './pigz'
    if os.path.isdir(pigzdir):
        rmtree(pigzdir)

    # cmd='git clone https://github.com/neurolabusc/pigz'

    cmd = 'git clone https://github.com/madler/pigz'
    subprocess.call(cmd, shell=True)
    pigzdir = os.path.join(basedir, 'pigz')
    pigzexe = os.path.join(pigzdir, 'pigz')
    ext = ''
    if platform.system() == 'Windows':
        ext = '.exe'
    pigzexe = pigzexe + ext
    os.chdir(pigzdir)
    cmd = 'make'
    subprocess.call(cmd, shell=True)
    outnm = os.path.join(exedir, 'pigz' + method + ext)
    print(pigzexe + '->' + outnm)
    shutil.move(pigzexe, outnm)


if __name__ == '__main__':
    corpus.install_neuro_corpus()
    compile_pigz()
