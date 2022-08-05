import re
import sys
import zlib
import codecs

import requests
from sphinx.ext.intersphinx import inspect_main
from sphinx.util.inventory import InventoryFileReader

pyside_uri = 'https://doc.qt.io/qtforpython/'
package_name = 'PySide6'

# make it so that the following statements are equivalent
#    :class:`QWidget`
#    :class:`QtWidgets.QWidget`
#    :class:`PySide6.QtWidgets.QWidget`
# only do this for some of the Qt modules
alias_modules = ('QtWidgets', 'QtCore', 'QtGui')

# the filename to use to save the original objects.inv file
original_inv = package_name + '-original.inv'
original_txt = package_name + '-original.txt'

# the filename to use to save the Sphinx-compatible object.inv file
modified_inv = package_name + '-aliases.inv'
modified_txt = package_name + '-aliases.txt'


def create_modified_inv():
    def write(*args):
        fout.write(compressor.compress((' '.join(args) + '\n').encode('utf-8')))

    # download the original objects.inv file
    with open(original_inv, mode='wb') as f:
        f.write(requests.get(pyside_uri + 'objects.inv').content)

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

        name, typ, prio, location, dispname = m.groups()
        location = pyside_uri + location.rstrip('#$')

        write(name, typ, prio, location, dispname)

        # apply the aliases
        for module in alias_modules:
            m = re.match(r'{0}\.{1}\.{0}\.{1}\.(\w+)(\.\w+)?'.format(package_name, module), name)
            if m:
                cls, method = m.groups()
                if method is None:
                    method = ''

                aliases = [
                    package_name + '.' + module + '.' + cls + method,
                    module + '.' + cls + method,
                    cls + method
                ]

                for alias in aliases:
                    write(alias, typ, prio, location, dispname)

    fout.write(compressor.flush())
    fin.close()
    fout.close()


def main():
    create_modified_inv()

    print('Created:')
    print('  ' + original_inv)
    print('  ' + original_txt)
    print('  ' + modified_inv)
    print('  ' + modified_txt)

    # redirect the print() statements in the inspect_main() function to a file
    sys.stdout = codecs.open(original_txt, 'wb', encoding='utf-8')
    inspect_main([original_inv])
    sys.stdout.close()

    # if the following succeeds without raising an exception then Sphinx is
    # able to read the pyqt#-modified-objects.inv file that was just created
    sys.stdout = codecs.open(modified_txt, 'wb', encoding='utf-8')
    inspect_main([modified_inv])
    sys.stdout.close()

    sys.exit(0)


if __name__ == '__main__':
    main()
