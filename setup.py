import os
import re
import sys
from setuptools import setup, find_packages

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'docs'))
import docs_commands


def read(filename):
    with open(filename) as fp:
        text = fp.read()
    return text


def fetch_init(key):
    # open the __init__.py file to determine the value instead of importing the package to get the value
    init_text = read('msl/qt/__init__.py')
    return re.compile(r'{}\s*=\s*(.*)'.format(key)).search(init_text).group(1)[1:-1]


testing = {'test', 'tests', 'pytest'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if testing else []

needs_sphinx = {'doc', 'docs', 'apidoc', 'apidocs', 'build_sphinx'}.intersection(sys.argv)
sphinx = ['sphinx', 'sphinx_rtd_theme'] if needs_sphinx else []

setup(
    name='msl-qt',
    version=fetch_init('__version__'),
    author=fetch_init('__author__'),
    author_email='joseph.borbely@measurement.govt.nz',
    url='https://github.com/MSLNZ/msl-qt',
    description='Write a short description about msl-qt here',
    long_description=read('README.rst'),
    license='MIT',
    platforms='any',
    classifiers=[],  # list the classifiers, see: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    setup_requires=sphinx + pytest_runner,
    tests_require=['pytest-cov', 'pytest'],
    install_requires=read('requirements.txt').splitlines(),
    cmdclass={
        'docs': docs_commands.BuildDocs,
        'apidocs': docs_commands.ApiDocs,
    },
    packages=find_packages(include=('msl*',)),
    include_package_data=True,
)
