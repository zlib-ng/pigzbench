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
    corpus.install_neuro_corpus()
    compile_pigz()
