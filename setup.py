#   Copyright 2012-2013 OpenStack, LLC.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import os

import setuptools

from openstackclient.openstack.common import setup


project = "python-openstackclient"
requires = setup.parse_requirements()
dependency_links = setup.parse_dependency_links()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setuptools.setup(
    name=project,
    version=setup.get_version(project),
    description="OpenStack command-line client",
    long_description=read('README.rst'),
    url='https://github.com/openstack/python-openstackclient',
    license="Apache License, Version 2.0",
    author='OpenStack Client Contributors',
    author_email='openstack@lists.launchpad.net',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: OpenStack',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=requires,
    dependency_links=dependency_links,
    cmdclass=setup.get_cmdclass(),
    entry_points={
        'console_scripts': ['openstack=openstackclient.shell:main'],
        'openstack.cli': [
        ],
        'openstack.identity.v2_0': [
            'create_endpoint=' +
            'openstackclient.identity.v2_0.endpoint:CreateEndpoint',
            'delete_endpoint=' +
            'openstackclient.identity.v2_0.endpoint:DeleteEndpoint',
            'list_endpoint=' +
            'openstackclient.identity.v2_0.endpoint:ListEndpoint',
            'show_endpoint=' +
            'openstackclient.identity.v2_0.endpoint:ShowEndpoint',
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
            'list_user-role=openstackclient.identity.v2_0.role:ListUserRole',
            'create_user=' +
            'openstackclient.identity.v2_0.user:CreateUser',
            'delete_user=' +
            'openstackclient.identity.v2_0.user:DeleteUser',
            'list_user=openstackclient.identity.v2_0.user:ListUser',
            'set_user=openstackclient.identity.v2_0.user:SetUser',
            'show_user=openstackclient.identity.v2_0.user:ShowUser',
        ],
        'openstack.identity.v3': [
            'create_group=openstackclient.identity.v3.group:CreateGroup',
            'delete_group=openstackclient.identity.v3.group:DeleteGroup',
            'set_group=openstackclient.identity.v3.group:SetGroup',
            'show_group=openstackclient.identity.v3.group:ShowGroup',
            'list_group=openstackclient.identity.v3.group:ListGroup',
            'create_project=' +
            'openstackclient.identity.v3.project:CreateProject',
            'delete_project=' +
            'openstackclient.identity.v3.project:DeleteProject',
            'set_project=openstackclient.identity.v3.project:SetProject',
            'show_project=openstackclient.identity.v3.project:ShowProject',
            'list_project=openstackclient.identity.v3.project:ListProject',
            'create_user=' +
            'openstackclient.identity.v3.user:CreateUser',
            'delete_user=' +
            'openstackclient.identity.v3.user:DeleteUser',
            'list_user=openstackclient.identity.v3.user:ListUser',
            'set_user=openstackclient.identity.v3.user:SetUser',
            'show_user=openstackclient.identity.v3.user:ShowUser',
        ],
        'openstack.image.v2': [
            'list_image=openstackclient.image.v2.image:ListImage',
            'show_image=openstackclient.image.v2.image:ShowImage',
            'save_image=openstackclient.image.v2.image:SaveImage',
        ],
        'openstack.compute.v2': [
            'create_agent=openstackclient.compute.v2.agent:CreateAgent',
            'create_flavor=openstackclient.compute.v2.flavor:CreateFlavor',
            'create_server=openstackclient.compute.v2.server:CreateServer',
            'delete_agent=openstackclient.compute.v2.agent:DeleteAgent',
            'delete_flavor=openstackclient.compute.v2.flavor:DeleteFlavor',
            'delete_server=openstackclient.compute.v2.server:DeleteServer',
            'list_agent=openstackclient.compute.v2.agent:ListAgent',
            'list_flavor=openstackclient.compute.v2.flavor:ListFlavor',
            'list_server=openstackclient.compute.v2.server:ListServer',
            'list_compute-service=' +
            'openstackclient.compute.v2.service:ListService',
            'pause_server=openstackclient.compute.v2.server:PauseServer',
            'reboot_server=openstackclient.compute.v2.server:RebootServer',
            'rebuild_server=openstackclient.compute.v2.server:RebuildServer',
            'resume_server=openstackclient.compute.v2.server:ResumeServer',
            'set_agent=openstackclient.compute.v2.agent:SetAgent',
            'show_flavor=openstackclient.compute.v2.flavor:ShowFlavor',
            'set_compute-service=' +
            'openstackclient.compute.v2.service:SetService',
            'show_server=openstackclient.compute.v2.server:ShowServer',
            'suspend_server=openstackclient.compute.v2.server:SuspendServer',
            'unpause_server=openstackclient.compute.v2.server:UnpauseServer',
        ],
        'openstack.volume.v1': [
            'create_type=openstackclient.volume.v1.type:CreateType',
            'delete_type=openstackclient.volume.v1.type:DeleteType',
            'list_type=openstackclient.volume.v1.type:ListType',
            'set_type=openstackclient.volume.v1.type:SetType',
            'unset_type=openstackclient.volume.v1.type:UnsetType',
            'show_quota=openstackclient.volume.v1.quota:ShowQuota',
            'list_quota=openstackclient.volume.v1.quota:ListQuota',
            'set_quota=openstackclient.volume.v1.quota:SetQuota',
            'create_volume=openstackclient.volume.v1.volume:CreateVolume',
            'delete_volume=openstackclient.volume.v1.volume:DeleteVolume',
            'list_volume=openstackclient.volume.v1.volume:ListVolume',
            'set_volume=openstackclient.volume.v1.volume:SetVolume',
            'show_volume=openstackclient.volume.v1.volume:ShowVolume',
            'create_snapshot=' +
            'openstackclient.volume.v1.snapshot:CreateSnapshot',
            'delete_snapshot=' +
            'openstackclient.volume.v1.snapshot:DeleteSnapshot',
            'list_snapshot=openstackclient.volume.v1.snapshot:ListSnapshot',
            'set_snapshot=openstackclient.volume.v1.snapshot:SetSnapshot',
            'show_snapshot=openstackclient.volume.v1.snapshot:ShowSnapshot',
        ]
    }
)
