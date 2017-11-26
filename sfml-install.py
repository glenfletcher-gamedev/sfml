from __future__ import print_function
import shutil
import os
import argparse

SUFFIX = ""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SFML Build Script')
    parser.add_argument('--lib',  metavar='PATH', dest='LIB_PATH',
                        action='store', help='Path that the binaries are stored',
                        default='lib', type=str)
    parser.add_argument('--out',  metavar='PATH', dest='OUT_PATH',
                        action='store', help='Path to use for output.',
                        default='../../lib', type=str)
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
    libs = ['sfml-system', 'sfml-window', 'sfml-network',
            'sfml-graphics', 'sfml-audio']
    if args.SHARED:
        if not os.path.exists(args.OUT_PATH):
            os.makedirs(args.OUT_PATH)
        for lib in libs:
            #lib = os.path.normpath(lib)
            src = os.path.abspath(os.path.join(args.LIB_PATH,
                               '{:s}{:s}-2.dll'.format(lib, SUFFIX)))
            dest = os.path.abspath(os.path.join(args.OUT_PATH,
                                    '{:s}{:s}-2.dll'.format(lib, SUFFIX)))
            if not os.path.exists(src):
                print("Error", src, "Missing.")
                continue
            if not os.path.exists(dest) or \
                int(os.path.getmtime(dest)) < int(os.path.getmtime(src)):
                    print("Copying", src, 'to', dest)
                    shutil.copy2(src, dest)