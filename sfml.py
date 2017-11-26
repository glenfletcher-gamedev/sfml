from __future__ import print_function
import subprocess as ps
import shutil
import os
import argparse

CXX = ""
CC = ""
CPATH= ""

TARGET = ""
SHARED = True
BUILD_PATH = ""

SUFFIX = ""

if os.name == 'posix':
    make = "Unix Makefiles"
else:
    make = "MinGW Makefiles"
    
print("CMake using: " + make)

class Error(Exception):
    def __init__(self, errors):
        errors = errors

def copytree(src, dst, symlinks=False, ignore=None):
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if os.path.exists(dst):
        if not os.path.isdir(dst):
            raise IOError("Can't copy directory to file")
    else:
        os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.normpath(os.path.join(src, name))
        dstname = os.path.normpath(os.path.join(dst, name))
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                if os.path.exists(dstname):
                    if int(os.path.getmtime(dstname)) >= \
                       int(os.path.getmtime(srcname)):
                        continue
                print("Copying", srcname, 'to', dstname)
                shutil.copy2(srcname, dstname)                
            # XXX What about devices, sockets etc.?
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.errors)
    try:
        shutil.copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError as why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise Error(errors)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SFML Build Script')
    parser.add_argument('--build',  metavar='PATH', dest='BUILD_PATH',
                        action='store', help='Path to use for build.',
                        default='build/sfml', type=str)
    parser.add_argument('--out',  metavar='PATH', dest='OUT_PATH',
                        action='store', help='Path to use for output.',
                        default='lib', type=str)
    parser.add_argument('--cxx',  metavar='PATH', dest='CXX',
                        action='store', help='Path to use for C++ Compiler.',
                        default='g++', type=str)
    parser.add_argument('--cc',  metavar='PATH', dest='CC',
                        action='store', help='Path to use for C Compiler.',
                        default='gcc', type=str)
    parser.add_argument('--flags',  metavar='FLAGS', dest='CXX_FLAGS',
                        action='store', help='Flags to pass to Compiler',
                        default='', type=str)
    parser.add_argument('--target',  metavar='TARGET', dest='TARGET',
                        action='store', help='Luild target',
                        default='debug', type=str)
    parser.add_argument('--shared',  metavar='SHARED', dest='SHARED',
                        action='store', help='Build Shared Libary',
                        default='1', type=bool)
    args = parser.parse_args()
    SUFFIX = ""
    if not args.SHARED:
        SUFFIX += "-s"
    if args.TARGET.lower() == 'debug':
        SUFFIX += "-d"                   
    ps.call(["cmake",
             "-G{0:s}".format(make),
             "-DCMAKE_CXX_COMPILER:PATH=" + args.CXX,
             "-DCMAKE_C_COMPILER:PATH=" + args.CC,
             "-DCMAKE_BUILD_TYPE=" + args.TARGET,
             "-DBUILD_SHARED_LIBS=" + ("True" if args.SHARED else "False"),
             "-DCMAKE_CXX_FLAGS=" + args.CXX_FLAGS,
             "-Hsfml",
             "-B" + args.BUILD_PATH])
    ps.call(["cmake",
             "-G{0:s}".format(make),
             "-DCMAKE_CXX_COMPILER:PATH=" + args.CXX,
             "-DCMAKE_C_COMPILER:PATH=" + args.CC,
             "-DCMAKE_BUILD_TYPE=" + args.TARGET,
             "-DBUILD_SHARED_LIBS=" + ("True" if args.SHARED else "False"),
             "-DCMAKE_CXX_FLAGS=" + args.CXX_FLAGS,
             "-Hsfml",
             "-B" + args.BUILD_PATH])
    ps.call(["cmake",
             "--build",
             args.BUILD_PATH])
    libs = ['sfml-system', 'sfml-window', 'sfml-network',
            'sfml-graphics', 'sfml-audio', 'sfml-main']
    if not os.path.exists(args.OUT_PATH):
        os.makedirs(args.OUT_PATH)
    for lib in libs:
        lib = os.path.normpath(lib)
        src = os.path.normpath(os.path.join(args.BUILD_PATH,
                           'lib/lib{:s}{:s}.a'.format(lib, SUFFIX)))
        dest = os.path.normpath(os.path.join(args.OUT_PATH,
                                    'lib{:s}{:s}.a'.format(lib, SUFFIX)))
        if not os.path.exists(dest) or \
            int(os.path.getmtime(dest)) < int(os.path.getmtime(src)):
                print("Copying", src, 'to', dest)
                shutil.copy2(src, dest)
        if args.SHARED and lib != 'sfml-main':
            src = os.path.normpath(os.path.join(args.BUILD_PATH,
                               'lib/{:s}{:s}-2.dll'.format(lib, SUFFIX)))
            dest = os.path.normpath(os.path.join(args.OUT_PATH,
                                    '{:s}{:s}-2.dll'.format(lib, SUFFIX)))
            if not os.path.exists(dest) or \
                int(os.path.getmtime(dest)) < int(os.path.getmtime(src)):
                    print("Copying", src, 'to', dest)
                    shutil.copy2(src, dest)
    copytree('sfml/include','include')