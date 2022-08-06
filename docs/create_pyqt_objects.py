# -*- coding: utf-8 -*-
import re
import sys
import zlib
import codecs
import argparse

import requests
from sphinx.ext.intersphinx import inspect_main
from sphinx.util.inventory import InventoryFileReader

# make it so that the following statements are equivalent
#    :class:`QWidget`
#    :class:`QtWidgets.QWidget`
#    :class:`PyQt5.QtWidgets.QWidget`
#
# only do this for the following Qt modules
alias_modules = ('', 'QtWidgets.', 'QtCore.', 'QtGui.')

HELP = """Creates a PyQt ``objects.inv`` file that is Sphinx compatible.

When using the ``PyQt#-modified-objects.inv`` file (which is created by 
running this script) for inter-Sphinx mapping, there are different ways
to link to PyQt objects (only valid for *some* of the PyQt modules).
For example, the following are equivalent ways to specify a link to the
documentation for the PyQt6.QtWidgets.QWidget class:

   :class:`QWidget`
   :class:`QtWidgets.QWidget`
   :class:`PyQt6.QtWidgets.QWidget`

The Qt modules that follow this equivalent linking syntax are currently:
%s

usage:
1. run the script using, for example,

   python create_pyqt_objects.py PyQt6

2. put the newly-created ``PyQt#-modified-objects.inv`` file in the same
   directory as Sphinx's conf.py file.

3. modify the ``intersphinx_mapping`` dictionary in the conf.py file to
   use the local ``PyQt#-modified-objects.inv`` file rather than the
   remote ``objects.inv`` file from the PyQt website. For example,

   intersphinx_mapping = {
       # 'PyQt6': ('https://www.riverbankcomputing.com/static/Docs/PyQt6/', None),
       'PyQt6': ('', PyQt6-modified-objects.inv'),
   }
""" % ' '.join([m[:-1] for m in alias_modules[1:]])


def create_modified_inv(package, original_inv, modified_inv, pyqt_uri):
    # download the original objects.inv file
    with open(original_inv, mode='wb') as f:
        f.write(requests.get(pyqt_uri + 'objects.inv').content)

    fin = open(original_inv, mode='rb')
    fout = open(modified_inv, mode='wb')

    # use the same compression for the output file as
    # sphinx.util.inventory.InventoryFile.dump
    compressor = zlib.compressobj(9)

    reader = InventoryFileReader(fin)

    # copy the header
    for i in range(4):
        fout.write((reader.readline() + '\n').encode('utf-8'))

    for line in reader.read_compressed_lines():
        # the re.match code is copied from
        # sphinx.util.inventory.InventoryFile.load_v2
        m = re.match(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)', line.rstrip())
        if not m:
            continue
        name, type, prio, location, dispname = m.groups()

        # change the 'sip' domain to 'py' and
        # rename the 'enum' and 'signal' roles
        if type.startswith('sip'):
            type = 'py' + type[len('sip'):]
        if type == 'py:enum':
            type = 'py:attribute'
        if type == 'py:signal':
            type = 'py:method'

        # update the URI to be an absolute location
        location = pyqt_uri + location.replace('##', '#')

        # apply the aliases
        for module in alias_modules:
            prefix = package + '.' + module
            if name.startswith(prefix):
                entry = ' '.join((name[len(prefix):], type, prio, location, dispname))
                fout.write(compressor.compress((entry + '\n').encode('utf-8')))

        entry = ' '.join((name, type, prio, location, dispname))
        fout.write(compressor.compress((entry + '\n').encode('utf-8')))

    fout.write(compressor.flush())
    fin.close()
    fout.close()


def configure_parser():
    parser = argparse.ArgumentParser(
        description=HELP,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        'pyqt',
        choices=['PyQt4', 'PyQt5', 'PyQt6'],
        help='the PyQt package to use to create the objects.inv file.'
    )

    return parser


def main(*args):
    if not args:
        args = sys.argv[1:]
        if not args:
            args = ['--help']

    parser = configure_parser()
    args = parser.parse_args(args)

    # the URI of the original objects.inv file
    pyqt_uri = 'https://www.riverbankcomputing.com/static/Docs/' + args.pyqt + '/'

    # the filename to use to save the original objects.inv file
    original_inv = args.pyqt + '-original-objects.inv'
    original_txt = args.pyqt + '-original-objects.txt'

    # the filename to use to save the Sphinx-compatible object.inv file
    modified_inv = args.pyqt + '-modified-objects.inv'
    modified_txt = args.pyqt + '-modified-objects.txt'

    create_modified_inv(args.pyqt, original_inv, modified_inv, pyqt_uri)

    print('Created:')
    print('  ' + original_inv)
    print('  ' + original_txt)
    print('  ' + modified_inv)
    print('  ' + modified_txt)

    # redirect the print() statements in the inspect_main() function to a file
    sys.stdout = codecs.open(original_txt, mode='wb', encoding='utf-8')
    inspect_main([original_inv])
    sys.stdout.close()

    # if the following succeeds without raising an exception then Sphinx is
    # able to read the pyqt#-modified-objects.inv file that was just created
    sys.stdout = codecs.open(modified_txt, mode='wb', encoding='utf-8')
    inspect_main([modified_inv])
    sys.stdout.close()


if __name__ == '__main__':
    sys.exit(main())
