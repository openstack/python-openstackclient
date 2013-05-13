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
        'openstack.identity.v3_0': [
            'endpoint_create='
                'openstackclient.identity.v2_0.endpoint:CreateEndpoint',
            'endpoint_delete='
                'openstackclient.identity.v2_0.endpoint:DeleteEndpoint',
            'endpoint_list='
                'openstackclient.identity.v2_0.endpoint:ListEndpoint',
            'endpoint_show='
                'openstackclient.identity.v2_0.endpoint:ShowEndpoint',

            'role_add='
                'openstackclient.identity.v2_0.role:AddRole',
            'role_create='
                'openstackclient.identity.v2_0.role:CreateRole',
            'role_delete='
                'openstackclient.identity.v2_0.role:DeleteRole',
            'role_list=openstackclient.identity.v2_0.role:ListRole',
            'role_remove='
                'openstackclient.identity.v2_0.role:RemoveRole',
            'role_show=openstackclient.identity.v2_0.role:ShowRole',

            'service_create='
                'openstackclient.identity.v2_0.service:CreateService',
            'service_delete='
                'openstackclient.identity.v2_0.service:DeleteService',
            'service_list=openstackclient.identity.v2_0.service:ListService',
            'service_show=openstackclient.identity.v2_0.service:ShowService',

            'tenant_create='
                'openstackclient.identity.v2_0.tenant:CreateTenant',
            'tenant_delete='
                'openstackclient.identity.v2_0.tenant:DeleteTenant',
            'tenant_list=openstackclient.identity.v2_0.tenant:ListTenant',
            'tenant_set=openstackclient.identity.v2_0.tenant:SetTenant',
            'tenant_show=openstackclient.identity.v2_0.tenant:ShowTenant',

            'user_role_list=openstackclient.identity.v2_0.role:ListUserRole',

            'user_create='
                'openstackclient.identity.v2_0.user:CreateUser',
            'user_delete='
                'openstackclient.identity.v2_0.user:DeleteUser',
            'user_list=openstackclient.identity.v2_0.user:ListUser',
            'user_set=openstackclient.identity.v2_0.user:SetUser',
            'user_show=openstackclient.identity.v2_0.user:ShowUser',
        ],
        'openstack.identity.v3': [
            'credential_create='
                'openstackclient.identity.v3.credential:CreateCredential',
            'credential_delete='
                'openstackclient.identity.v3.credential:DeleteCredential',
            'credential_list='
                'openstackclient.identity.v3.credential:ListCredential',
            'credential_set='
                'openstackclient.identity.v3.credential:SetCredential',
            'credential_show='
                'openstackclient.identity.v3.credential:ShowCredential',

            'domain_create=openstackclient.identity.v3.domain:CreateDomain',
            'domain_delete=openstackclient.identity.v3.domain:DeleteDomain',
            'domain_list=openstackclient.identity.v3.domain:ListDomain',
            'domain_set=openstackclient.identity.v3.domain:SetDomain',
            'domain_show=openstackclient.identity.v3.domain:ShowDomain',

            'endpoint_create='
                'openstackclient.identity.v3.endpoint:CreateEndpoint',
            'endpoint_delete='
                'openstackclient.identity.v3.endpoint:DeleteEndpoint',
            'endpoint_set=openstackclient.identity.v3.endpoint:SetEndpoint',
            'endpoint_show=openstackclient.identity.v3.endpoint:ShowEndpoint',
            'endpoint_list=openstackclient.identity.v3.endpoint:ListEndpoint',

            'group_create=openstackclient.identity.v3.group:CreateGroup',
            'group_delete=openstackclient.identity.v3.group:DeleteGroup',
            'group_list=openstackclient.identity.v3.group:ListGroup',
            'group_set=openstackclient.identity.v3.group:SetGroup',
            'group_show=openstackclient.identity.v3.group:ShowGroup',

            'policy_create=openstackclient.identity.v3.policy:CreatePolicy',
            'policy_delete=openstackclient.identity.v3.policy:DeletePolicy',
            'policy_list=openstackclient.identity.v3.policy:ListPolicy',
            'policy_set=openstackclient.identity.v3.policy:SetPolicy',
            'policy_show=openstackclient.identity.v3.policy:ShowPolicy',

            'project_create='
                'openstackclient.identity.v3.project:CreateProject',
            'project_delete='
                'openstackclient.identity.v3.project:DeleteProject',
            'project_list=openstackclient.identity.v3.project:ListProject',
            'project_set=openstackclient.identity.v3.project:SetProject',
            'project_show=openstackclient.identity.v3.project:ShowProject',

            'role_add=openstackclient.identity.v3.role:AddRole',
            'role_create='
                'openstackclient.identity.v3.role:CreateRole',
            'role_delete='
                'openstackclient.identity.v3.role:DeleteRole',
            'role_list=openstackclient.identity.v3.role:ListRole',
            'role_show=openstackclient.identity.v3.role:ShowRole',
            'role_set=openstackclient.identity.v3.role:SetRole',

            'service_create='
                'openstackclient.identity.v3.service:CreateService',
            'service_delete='
                'openstackclient.identity.v3.service:DeleteService',
            'service_list=openstackclient.identity.v3.service:ListService',
            'service_show=openstackclient.identity.v3.service:ShowService',
            'service_set=openstackclient.identity.v3.service:SetService',

            'user_create='
                'openstackclient.identity.v3.user:CreateUser',
            'user_delete='
                'openstackclient.identity.v3.user:DeleteUser',
            'user_list=openstackclient.identity.v3.user:ListUser',
            'user_set=openstackclient.identity.v3.user:SetUser',
            'user_show=openstackclient.identity.v3.user:ShowUser',
        ],
        'openstack.image.v1': [
            'image_create=openstackclient.image.v1.image:CreateImage',
        ],
        'openstack.image.v2': [
            'image_delete=openstackclient.image.v2.image:DeleteImage',
            'image_list=openstackclient.image.v2.image:ListImage',
            'image_save=openstackclient.image.v2.image:SaveImage',
            'image_show=openstackclient.image.v2.image:ShowImage',
        ],
        'openstack.compute.v2': [
            'agent_create=openstackclient.compute.v2.agent:CreateAgent',
            'agent_delete=openstackclient.compute.v2.agent:DeleteAgent',
            'agent_list=openstackclient.compute.v2.agent:ListAgent',
            'agent_set=openstackclient.compute.v2.agent:SetAgent',

            'compute_service_list='
                'openstackclient.compute.v2.service:ListService',
            'compute_service_set='
                'openstackclient.compute.v2.service:SetService',

            'console_log_show='
                'openstackclient.compute.v2.console:ShowConsoleLog',
            'console_url_show='
                'openstackclient.compute.v2.console:ShowConsoleURL',

            'ip_fixed_add=openstackclient.compute.v2.fixedip:AddFixedIP',
            'ip_fixed_remove=openstackclient.compute.v2.fixedip:RemoveFixedIP',

            'flavor_create=openstackclient.compute.v2.flavor:CreateFlavor',
            'flavor_delete=openstackclient.compute.v2.flavor:DeleteFlavor',
            'flavor_list=openstackclient.compute.v2.flavor:ListFlavor',
            'flavor_show=openstackclient.compute.v2.flavor:ShowFlavor',

            'ip_floating_add='
                'openstackclient.compute.v2.floatingip:AddFloatingIP',
            'ip_floating_create='
                'openstackclient.compute.v2.floatingip:CreateFloatingIP',
            'ip_floating_delete='
                'openstackclient.compute.v2.floatingip:DeleteFloatingIP',
            'ip_floating_list='
                'openstackclient.compute.v2.floatingip:ListFloatingIP',
            'ip_floating_remove='
                'openstackclient.compute.v2.floatingip:RemoveFloatingIP',

            'ip_floating_pool_list='
                'openstackclient.compute.v2.floatingippool:ListFloatingIPPool',

            'host_list=openstackclient.compute.v2.host:ListHost',
            'host_show=openstackclient.compute.v2.host:ShowHost',

            'hypervisor_list='
                'openstackclient.compute.v2.hypervisor:ListHypervisor',
            'hypervisor_show='
                'openstackclient.compute.v2.hypervisor:ShowHypervisor',

            'keypair_create='
                'openstackclient.compute.v2.keypair:CreateKeypair',
            'keypair_delete='
                'openstackclient.compute.v2.keypair:DeleteKeypair',
            'keypair_list='
                'openstackclient.compute.v2.keypair:ListKeypair',
            'keypair_show='
                'openstackclient.compute.v2.keypair:ShowKeypair',

            'server_create=openstackclient.compute.v2.server:CreateServer',
            'server_delete=openstackclient.compute.v2.server:DeleteServer',
            'server_list=openstackclient.compute.v2.server:ListServer',
            'server_pause=openstackclient.compute.v2.server:PauseServer',
            'server_reboot=openstackclient.compute.v2.server:RebootServer',
            'server_rebuild=openstackclient.compute.v2.server:RebuildServer',
            'server_resume=openstackclient.compute.v2.server:ResumeServer',
            'server_show=openstackclient.compute.v2.server:ShowServer',
            'server_suspend=openstackclient.compute.v2.server:SuspendServer',
            'server_unpause=openstackclient.compute.v2.server:UnpauseServer',
        ],
        'openstack.volume.v1': [
            'quota_list=openstackclient.volume.v1.quota:ListQuota',
            'quota_set=openstackclient.volume.v1.quota:SetQuota',
            'quota_show=openstackclient.volume.v1.quota:ShowQuota',

            'snapshot_create='
                'openstackclient.volume.v1.snapshot:CreateSnapshot',
            'snapshot_delete='
                'openstackclient.volume.v1.snapshot:DeleteSnapshot',
            'snapshot_list=openstackclient.volume.v1.snapshot:ListSnapshot',
            'snapshot_set=openstackclient.volume.v1.snapshot:SetSnapshot',
            'snapshot_show=openstackclient.volume.v1.snapshot:ShowSnapshot',

            'volume_create=openstackclient.volume.v1.volume:CreateVolume',
            'volume_delete=openstackclient.volume.v1.volume:DeleteVolume',
            'volume_list=openstackclient.volume.v1.volume:ListVolume',
            'volume_set=openstackclient.volume.v1.volume:SetVolume',
            'volume_show=openstackclient.volume.v1.volume:ShowVolume',
            'volume_unset=openstackclient.volume.v1.volume:UnsetVolume',

            'volume_type_create='
                'openstackclient.volume.v1.type:CreateVolumeType',
            'volume_type_delete='
                'openstackclient.volume.v1.type:DeleteVolumeType',
            'volume_type_list=openstackclient.volume.v1.type:ListVolumeType',
            'volume_type_set=openstackclient.volume.v1.type:SetVolumeType',
            'volume_type_unset=openstackclient.volume.v1.type:UnsetVolumeType',
        ]
    }
)
