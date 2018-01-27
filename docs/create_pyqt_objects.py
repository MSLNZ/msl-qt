# -*- coding: utf-8 -*-
import re
import sys
import zlib
import codecs
import argparse

import requests
from sphinx.ext.intersphinx import debug
from sphinx.util.inventory import InventoryFileReader

# used for redirecting a PyQt URI to a Qt URI
uri_redirect = re.compile(r'(The C\+\+ documentation can be found.*)(href=")(.*)(">here)')

# make it so that the following statements are equivalent
#    :class:`QWidget`
#    :class:`QtWidgets.QWidget`
#    :class:`PyQt5.QtWidgets.QWidget`
# only do this for some of the Qt modules
alias_modules = (u'', u'QtWidgets.', u'QtCore.', u'QtGui.')

HELP = """Creates a PyQt ``objects.inv`` file that is Sphinx compatible.

Inter-Sphinx mapping works best for PyQt5 with the --use-qt-uri flag.

When using the ``pyqt#-modified-objects.inv`` file (which is created by 
running this script) for inter-Sphinx mapping, there are different ways
to link to PyQt objects (only valid for *some* of the PyQt modules).
For example, the following are equivalent ways to specify a link to the
documentation for the PyQt5.QtWidgets.QWidget class:

   :class:`QWidget`
   :class:`QtWidgets.QWidget`
   :class:`PyQt5.QtWidgets.QWidget`

The Qt modules that follow this equivalent linking syntax are currently:
%s

warning:
Running this script for PyQt4 doesn't really do anything useful.

usage:
1. run the script using, for example,

   python create_pyqt_objects.py pyqt5 --use-qt-uri

2. put the newly-created ``pyqt#-modified-objects.inv`` file in the same
   directory as Sphinx's conf.py file.

3. modify the ``intersphinx_mapping`` dictionary in the conf.py file to
   use the local ``pyqt#-modified-objects.inv`` file rather than the
   remote ``objects.inv`` file from the PyQt website. For example,

   intersphinx_mapping = {
       # 'PyQt5': ('http://pyqt.sourceforge.net/Docs/PyQt5/', None),
       'PyQt5': ('', 'pyqt5-modified-objects.inv'),
   }
""" % ' '.join([m[:-1] for m in alias_modules[1:]])


def create_modified_inv(package, original_inv, modified_inv, pyqt_uri, use_qt_uri):
    """if --use-qt-uri is used then two things will occur:

  1. creating the ``pyqt#-modified-objects.inv``
     file will take much longer (up to ~25 minutes).
  2. the value of the PyQt URI will be set equal
     to the Qt URI.

To help explain what item #2 means we will consider
the PyQt5.QtWidgets.QWidget class as an example.

Instead of using the PyQt5 URI for the
:class:`PyQt5.QtWidgets.QWidget` link, i.e.,

  http://pyqt.sourceforge.net/Docs/PyQt5/api/QtWidgets/qwidget.html##PyQt5-QtWidgets-QWidget

where that web page indicates,

  The C++ documentation can be found <here>.

the :class:`PyQt5.QtWidgets.QWidget` link will be set
equal to the Qt URI, i.e.,

  https://doc.qt.io/qt-5/qwidget.html

Basically, the --use-qt-uri flag saves you from
performing the intermediate task of clicking on
the <here> link on the PyQt web page when
navigating to the Qt documentation from your
own documentation.
    """

    # download the original objects.inv file
    with open(original_inv, 'wb') as f:
        f.write(requests.get(pyqt_uri + u'objects.inv').content)

    fin = open(original_inv, 'rb')
    fout = open(modified_inv, 'wb')

    # use the same compression for the output file as
    # sphinx.util.inventory.InventoryFile.dump
    compressor = zlib.compressobj(9)

    reader = InventoryFileReader(fin)

    # copy the header
    for i in range(4):
        fout.write((reader.readline() + u'\n').encode('utf-8'))

    for line in reader.read_compressed_lines():
        # the re.match code is copied from
        # sphinx.util.inventory.InventoryFile.load_v2
        m = re.match(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)', line.rstrip())
        if not m:
            continue
        name, type, prio, location, dispname = m.groups()

        # change the `sip` domain to `py`
        if type.startswith(u'sip'):
            type = u'py' + type[len(u'sip'):]

        # update the URI to be an absolute location
        location = pyqt_uri + location

        # check if the URI just redirects to a Qt URI
        # if so, then use the Qt URI instead of the PyQt URI
        if use_qt_uri:

            # show that stuff is still happening
            print(name)

            redirect = re.findall(uri_redirect, requests.get(location).content.decode('utf-8'))
            if redirect:
                assert len(redirect) == 1, 'Expected only 1 redirect match'
                location = redirect[0][2]  # the Qt URI

        # apply the aliases
        for module in alias_modules:
            prefix = package + u'.' + module
            if name.startswith(prefix):
                entry = u' '.join((name[len(prefix):], type, prio, location, dispname))
                fout.write(compressor.compress((entry + u'\n').encode('utf-8')))

        entry = u' '.join((name, type, prio, location, dispname))
        fout.write(compressor.compress((entry + u'\n').encode('utf-8')))

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
        choices=['pyqt4', 'pyqt5'],
        type=str.lower,
        help='the PyQt package to use to create the objects.inv file.'
    )

    parser.add_argument(
        '--use-qt-uri',
        action='store_true',
        default=False,
        help=create_modified_inv.__doc__,
    )

    return parser


def main(*args):
    if not args:
        args = sys.argv[1:]
        if not args:
            args = ['--help']

    parser = configure_parser()
    args = parser.parse_args(args)

    # either PyQt4 or PyQt5
    package = u'PyQt4' if args.pyqt == 'pyqt4' else u'PyQt5'

    # the URI of the original objects.inv file
    pyqt_uri = u'http://pyqt.sourceforge.net/Docs/' + package + u'/'

    # the filename to use to save the original objects.inv file
    original_inv = package.lower() + u'-original-objects.inv'
    original_txt = package.lower() + u'-original-objects.txt'

    # the filename to use to save the Sphinx-compatible object.inv file
    modified_inv = package.lower() + u'-modified-objects.inv'
    modified_txt = package.lower() + u'-modified-objects.txt'

    create_modified_inv(package, original_inv, modified_inv, pyqt_uri, args.use_qt_uri)

    print('\nCreated:')
    print('  ' + original_inv)
    print('  ' + original_txt)
    print('  ' + modified_inv)
    print('  ' + modified_txt)

    # redirect the print() statements in the debug() function to a file
    sys.stdout = codecs.open(original_txt, 'wb', encoding='utf-8')
    debug(['', original_inv])
    sys.stdout.close()

    # if the following succeeds without raising an exception then Sphinx is
    # able to read the pyqt#-modified-objects.inv file that was just created
    sys.stdout = codecs.open(modified_txt, 'wb', encoding='utf-8')
    debug(['', modified_inv])
    sys.stdout.close()

    sys.exit(0)


if __name__ == '__main__':
    main()
