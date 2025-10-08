# All Rights Reserved 2020
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

import copy

from oslo_utils import uuidutils


class FakeTapService:
    @staticmethod
    def create_tap_service(attrs=None):
        """Create a fake tap service."""
        attrs = attrs or {}
        tap_service_attrs = {
            'id': uuidutils.generate_uuid(),
            'tenant_id': uuidutils.generate_uuid(),
            'name': 'test_tap_service' + uuidutils.generate_uuid(),
            'status': 'ACTIVE',
        }
        tap_service_attrs.update(attrs)
        return copy.deepcopy(tap_service_attrs)

    @staticmethod
    def create_tap_services(attrs=None, count=1):
        """Create multiple fake tap services."""

        tap_services = []
        for i in range(0, count):
            if attrs is None:
                attrs = {'id': f'fake_id{i}'}
            elif getattr(attrs, 'id', None) is None:
                attrs['id'] = f'fake_id{i}'
            tap_services.append(FakeTapService.create_tap_service(attrs=attrs))

        return tap_services


class FakeTapFlow:
    @staticmethod
    def create_tap_flow(attrs=None):
        """Create a fake tap service."""
        attrs = attrs or {}
        tap_flow_attrs = {
            'id': uuidutils.generate_uuid(),
            'tenant_id': uuidutils.generate_uuid(),
            'name': 'test_tap_flow' + uuidutils.generate_uuid(),
            'status': 'ACTIVE',
            'direction': 'BOTH',
        }
        tap_flow_attrs.update(attrs)
        return copy.deepcopy(tap_flow_attrs)

    @staticmethod
    def create_tap_flows(attrs=None, count=1):
        """Create multiple fake tap flows."""

        tap_flows = []
        for i in range(0, count):
            if attrs is None:
                attrs = {
                    'id': f'fake_id{i}',
                    'source_port': uuidutils.generate_uuid(),
                    'tap_service_id': uuidutils.generate_uuid(),
                }
            elif getattr(attrs, 'id', None) is None:
                attrs['id'] = f'fake_id{i}'
            tap_flows.append(FakeTapFlow.create_tap_flow(attrs=attrs))

        return tap_flows


class FakeTapMirror:
    @staticmethod
    def create_tap_mirror(attrs=None):
        """Create a fake tap mirror."""
        attrs = attrs or {}
        tap_mirror_attrs = {
            'id': uuidutils.generate_uuid(),
            'tenant_id': uuidutils.generate_uuid(),
            'name': 'test_tap_mirror' + uuidutils.generate_uuid(),
            'port_id': uuidutils.generate_uuid(),
            'directions': 'IN=99',
            'remote_ip': '192.10.10.2',
            'mirror_type': 'gre',
        }
        tap_mirror_attrs.update(attrs)
        return copy.deepcopy(tap_mirror_attrs)

    @staticmethod
    def create_tap_mirrors(attrs=None, count=1):
        """Create multiple fake tap mirrors."""

        tap_mirrors = []
        for i in range(0, count):
            if attrs is None:
                attrs = {
                    'id': f'fake_id{i}',
                    'port_id': uuidutils.generate_uuid(),
                    'name': f'test_tap_mirror_{i}',
                    'directions': f'IN={99 + i}',
                    'remote_ip': f'192.10.10.{i + 3}',
                }
            elif getattr(attrs, 'id', None) is None:
                attrs['id'] = f'fake_id{i}'
            tap_mirrors.append(FakeTapMirror.create_tap_mirror(attrs=attrs))

        return tap_mirrors
