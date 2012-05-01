import os

import setuptools

from openstackclient.openstack.common.setup import generate_authors
from openstackclient.openstack.common.setup import parse_requirements
from openstackclient.openstack.common.setup import parse_dependency_links
from openstackclient.openstack.common.setup import write_git_changelog


requires = parse_requirements()
dependency_links = parse_dependency_links()
write_git_changelog()
generate_authors()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setuptools.setup(
    name="python-openstackclient",
    version="0.1",
    description="OpenStack command-line client",
    long_description=read('README.rst'),
    url='https://github.com/openstack/python-openstackclient',
    license="Apache License, Version 2.0",
    author='OpenStack Client Contributors',
    author_email='openstackclient@example.com',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
       'Development Status :: 2 - Pre-Alpha',
       'Environment :: Console',
       'Intended Audience :: Developers',
       'Intended Audience :: Information Technology',
       'License :: OSI Approved :: Apache Software License',
       'Operating System :: OS Independent',
       'Programming Language :: Python',
    ],
    install_requires=requires,
    dependency_links=dependency_links,
    test_suite="nose.collector",
    entry_points={
        'console_scripts': ['stack=openstackclient.shell:main'],
        'openstack.cli': [
            'list_server=openstackclient.compute.v2.server:List_Server',
            'show_server=openstackclient.compute.v2.server:Show_Server',
            'list_service=openstackclient.identity.v2_0.service:List_Service',
        ]
    }
)
