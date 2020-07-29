# pigz-bench for Python

## Introduction

These simple Python scripts benchmark different zlib compression libraries for the [pigz](https://zlib.net/pigz/) parallel compressor. Parallel compression can use multiple cores available with modern computers to rapidly compress data. This technique can be combined with the [CloudFlare zlib](https://github.com/cloudflare/zlib) or [zlib-ng](https://github.com/zlib-ng/zlib-ng/) which accelerates compression using other features of modern hardware.

By default, these scripts examine compression and decompression of the [Silesia compression corpus](http://sun.aei.polsl.pl/~sdeor/index.php?page=silesia). Some compression methods work particularly well for some datasets (for example, the  Italian alphabet only has 21 letters, whereas some other languages have a larger set). The scripts will also install an optional corpus of brain imaging data in the [NIfTI](https://nifti.nimh.nih.gov/) format.  It is common for tools like [AFNI](https://afni.nimh.nih.gov/) and [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki) to save NIfTI images using gzip compression (.nii.gz files).  Modern MRI methods such as multi-band yield huge datasets, so considerable [time](https://github.com/rordenlab/niimath) spent compressing these images. You can also choose to compress the files in any folder you wish, allowing you to create a custom corpus. You can also download and test the [Canterbury corpus](https://corpus.canterbury.ac.nz/purpose.html) or the [Calgary corpus](http://www.data-compression.info/Corpora/CalgaryCorpus/).

The graph below shows the performance of pigz variants compressing the Silesia corpus with increasing numbers of threads (CPU cores) devoted to the compression. The test system was a 12-core (24 thread) AMD Ryzen 3900X:

![alt tag](https://github.com/neurolabusc/pigz-bench-python/blob/master/silesia_speed_threads.png)

The next graph shows each tool using its preferred number of threads to compress the Silesia corpus. All versions of pigz outperform the system's single threaded gzip. One can see that the [modern zstd](https://facebook.github.io/zstd/) format dominates the older and simpler gzip. gzip has been widely adopted in many fields (for example in brain imaging it is used for [NIfTI](https://nifti.nimh.nih.gov), [NRRD](http://teem.sourceforge.net/nrrd/format.html) and [AFNI](https://afni.nimh.nih.gov/pub/dist/doc/program_help/README.compression.html)). The simplicity of the gzip format means it is easy for developers to include support in their tools. Therefore, gzip plays an important niche in the community. However, this graph demonstrates that modern compression formats (like zstd) that were designed for modern hardware and leveraging new techniques have inherent benefits.

![alt tag](https://github.com/neurolabusc/pigz-bench-python/blob/master/silesia_speed_size.png)

The script `c_decompress.py` allows us to compare speed of decompression. Decompression is faster than compression. However, gzip decompression can not leverage multiple threads, and is generally slower than [modern compression formats](https://facebook.github.io/zstd/). However, the modern zstd is not [tuned for the datatypes common in science](https://github.com/facebook/zstd/issues/1492). The tests below illustrate that gz decompression remains competitive in this niche. In this test, all gz tools are decompressing the same data (addressing a concern by [Sebastian Pop](https://github.com/zlib-ng/zlib-ng/issues/326) that different gzip compressors create different file sizes, and smaller files might be more complicated and therefore slower to extract). In contrast, bzip2 and ztd are decompressing data that was compressed to a smaller size. It is typical for more compact compression to use more complicated algorithms, so  comparing between formats is challenging. Regardless, among gz tools, zlib-ng shows superior decompression performance:

| Speed (mb/s)  | pigz-CF  | pigz-ng  | pigz-Sys |   gzip   |  pbzip2  |   zstd   |
| ------------- | -------- | -------- | -------- | -------- | -------- | -------- |
| Decompression |     307  |     361  |     306  |     189  |     448  |     528  |

## Running the benchmark

Run the benchmark with a command like the following (you may need to use `python` instead of `python3`):

```
python3 a_compile.py
python3 b_speed_threads.py
python3 c_decompress.py
python3 d_speed_size.py
python3 f_speed_size_decompress.py
```
## Dependencies

This script required Python 3.3 or later (for functions like shutil.which, os.cpu_count).

The compile script will require your system has a C compiler, CMake, and git installed. Installation depends on operating system, but for a Debian-based Linux system the install might be `sudo apt install build-essential cmake git`.


You may have to install some Python packages. You can install these with your favorite package manager, if you use `pip3` the commands will look like this:

```
pip3 install seaborn
pip3 install psutil
```

This should be sufficient for most modern systems (since installing seaborn should install `pandas`, `scipy`, `numpy`). However, you may need to install additional dependencies (e.g. `pip3 install Cython; pip3 install numpy`).

The `a_compile.py` will build variants of pigz. However, it will also test the `gzip`, `zstd` and `pbzip2` compressors if they are installed. Installation varies for different operating systems. For example, on Debian-based Linux distributions you could run `sudo apt install pbzip2` to install `pbzip2`.

## Running data on a server

These scripts will attempt to generate a line plot to show the performance of different versions of pigz. These plots require access to a graphical display. Some servers only provide test-based command line access, so in these cases the scripts will report `Plot the results on a machine with a graphical display`. In this case, you can copy the result files generated and view them on a computer with a graphical display. This Python script shows how to view plots for results generated on a different computer:

```
import b_speed_threads
b_speed_threads.plot('speed_threadsAmpere.pkl')
import d_speed_size
d_speed_size.plot('speed_size.pkl')
```

## The scripts

1. `a_compile.py` will download and build copies of pigz using different zlib variants (system, CloudFlare, ng). It also downloads sample images to test compression, specifically the [sample MRI scans](https://github.com/neurolabusc/zlib-bench) which are copied to the folder `corpus`. You **must** run this script once first, before the other scripts. All the other scripts can be run independently of each other.
2. `b_speed_threads.py` compares the speed of the different versions of pigz as the number of threads is increased. Each variant is timed compressing the files in the folder `corpus`. You can replace the files in the `corpus` folder with ones more representative of the files you hope to compress.
3. `c_decompress.py` evaluates the decompression speed. In general, the gzip format is slow to compress but fast to decompress (particularly compared to formats developed at the same time). However, gzip decompression is slow relative to the modern [zstd](https://facebook.github.io/zstd/). Further, while gzip compression can benefit from parallel processing, decompression does not. An important feature of this script is that each variant of zlib contributes compressed files to the testing corpus, and then each tool is tested on this full corpus. This ensures we are [comparing similar tasks](https://github.com/zlib-ng/zlib-ng/issues/326), as some zlib compression methods might generate smaller files at the cost of creating files that are slower to decompress. The script also validates the compression and decompression of each datatype, ensuring the process is truly lossless.
4. `d_speed_size.sh` compares different variants of pigz to gzip, zstd and bzip2 for compressing the corpus. Each tool is tested at different compression levels, but always using the preferred number of threads.
5. `e_test_mgzip.py` evaluates [mgzip](https://pypi.org/project/mgzip/) which creates gz format files that are both compressed and decompressed in parallel. The files created by this method can be decompressed by any gz compatible tool, but the faster parallel decompression requires using mgzip.
6. `f_speed_size_decompress.py` combines `c_decompress.py` and `d_speed_size.sh` into a single script. The strength of this script is that it is easy to extend. You can edit it to include additional compressors. For example, commented out lines test `lz4` and `xz` compres./sion. It can be run with two optional arguments. The first sets the folder with files to compress (defaults to `./corpus`). The second allows you to determine how many runs are computed (default 3). This script reports the **fastest** time across all the runs.

## Testing custom versions of pigz

The script `a_compile.py` will compile 3 popular variants of pigz and copy these to the `exe` folder. The subsequent scripts will test all executables in this folder. Therefore, you can copy your own variation into this folder and compare your best effort against the competition. [Issue 1](https://github.com/neurolabusc/pigz-bench-python/issues/1) describes how to easily compile a custom variation without changing the base version.

## Alternatives

 - Python users may want to examine [mgzip](https://pypi.org/project/mgzip/). Like pigz, mgzip can compress files to gz format in parallel. However, it can also decompress files created with mgzip in parallel. The gz files created by mgzip are completely valid gzip files, so they can be decompressed by any gzip compatible tool. However, these files require a tiny bit more disk space which allows parallel blocked decompression (as long as you use mgzip to do the decompression). For optimal performance, one should set a `blocksize` that correspnds to the number of threads for compression. This repository includes the `test_mgzip.py` script to evaluate this tool.
 - Python users can use [indexed-gzip](https://pypi.org/project/indexed-gzip/) to generate an index file for any gzip file. This index file accelerates random access to a gzip file.
 - These Python scripts are portedfrom [shell scripts](https://github.com/neurolabusc/pigz-bench). Some users may prefer the shell scripts which have fewer dependencies.
