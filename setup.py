import os
import sys
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = [
        'cliff',
        'distribute',
        'httplib2', 
        'prettytable',
        "python-keystoneclient >= 2012.1",
        "python-novaclient >= 2012.1",
]

if sys.version_info < (2, 6):
    requirements.append('simplejson')
if sys.version_info < (2, 7):
    requirements.append("argparse")

setup(
    name = "python-openstackclient",
    version = "2012.0",
    description = "OpenStack command-line client",
    long_description = read('README.rst'),
    license="Apache License, Version 2.0",
    author = "Dean Troyer",
    author_email = "dtroyer@gmail.com",
    packages=find_packages(exclude=['tests', 'tests.*']),
    url = "https://github.com/dtroyer/python-openstackclient",
    install_requires=requirements,
    classifiers=[
       'Development Status :: 2 - Pre-Alpha',
       'Environment :: Console',
       'Intended Audience :: Developers',
       'Intended Audience :: Information Technology',
       'License :: OSI Approved :: Apache Software License',
       'Operating System :: OS Independent',
       'Programming Language :: Python',
   ],

    tests_require = ["nose", "mock", "mox"],
    test_suite = "nose.collector",

    entry_points = {
        'console_scripts': ['stack = openstackclient.shell:main'],
        'openstack.cli': [
            'list_server = openstackclient.compute.v2.server:List_Server',
            'show_server = openstackclient.compute.v2.server:Show_Server',
            'list_service = openstackclient.identity.v2_0.service:List_Service',
        ]
    }
)

