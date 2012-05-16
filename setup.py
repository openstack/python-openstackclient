# Copyright 2012 OpenStack LLC.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

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
        'console_scripts': ['openstack=openstackclient.shell:main'],
        'openstack.cli': [
            'add_role=' +
                'openstackclient.identity.v2_0.role:AddRole',
            'create_role=' +
                'openstackclient.identity.v2_0.role:CreateRole',
            'delete_role=' +
                'openstackclient.identity.v2_0.role:DeleteRole',
            'list_role=openstackclient.identity.v2_0.role:ListRole',
            'remove_role=' +
                'openstackclient.identity.v2_0.role:RemoveRole',
            'show_role=openstackclient.identity.v2_0.role:ShowRole',
            'list_server=openstackclient.compute.v2.server:ListServer',
            'show_server=openstackclient.compute.v2.server:ShowServer',
            'create_endpoint=' +
                'openstackclient.identity.v2_0.endpoint:CreateEndpoint',
            'delete_endpoint=' +
                'openstackclient.identity.v2_0.endpoint:DeleteEndpoint',
            'list_endpoint=' +
                'openstackclient.identity.v2_0.endpoint:ListEndpoint',
            'show_endpoint=' +
                'openstackclient.identity.v2_0.endpoint:ShowEndpoint',
            'create_service=' +
                'openstackclient.identity.v2_0.service:CreateService',
            'delete_service=' +
                'openstackclient.identity.v2_0.service:DeleteService',
            'list_service=openstackclient.identity.v2_0.service:ListService',
            'show_service=openstackclient.identity.v2_0.service:ShowService',
            'create_tenant=' +
                'openstackclient.identity.v2_0.tenant:CreateTenant',
            'delete_tenant=' +
                'openstackclient.identity.v2_0.tenant:DeleteTenant',
            'list_tenant=openstackclient.identity.v2_0.tenant:ListTenant',
            'set_tenant=openstackclient.identity.v2_0.tenant:SetTenant',
            'show_tenant=openstackclient.identity.v2_0.tenant:ShowTenant',
            'create_user=' +
                'openstackclient.identity.v2_0.user:CreateUser',
            'delete_user=' +
                'openstackclient.identity.v2_0.user:DeleteUser',
            'list_user=openstackclient.identity.v2_0.user:ListUser',
            'set_user=openstackclient.identity.v2_0.user:SetUser',
            'show_user=openstackclient.identity.v2_0.user:ShowUser',
            'list_user-role=openstackclient.identity.v2_0.role:ListUserRole',
        ]
    }
)
