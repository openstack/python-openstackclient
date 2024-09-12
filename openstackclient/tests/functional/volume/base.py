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

import time

from openstackclient.tests.functional import base


class BaseVolumeTests(base.TestCase):
    """Base class for Volume functional tests."""

    @classmethod
    def wait_for_status(
        cls,
        check_type,
        check_name,
        desired_status,
        wait=120,
        interval=5,
        failures=None,
    ):
        current_status = "notset"
        if failures is None:
            failures = ['error']
        total_sleep = 0
        while total_sleep < wait:
            output = cls.openstack(
                check_type + ' show ' + check_name,
                parse_output=True,
            )
            current_status = output['status']
            if current_status == desired_status:
                print(
                    f'{check_type} {check_name} now has status {current_status}'
                )
                return
            print(
                f'Checking {check_type} {check_name} Waiting for {desired_status} current status: {current_status}'
            )
            if current_status in failures:
                raise Exception(
                    f'Current status {current_status} of {check_type} {check_name} is one of failures {failures}'
                )
            time.sleep(interval)
            total_sleep += interval
        cls.assertOutput(desired_status, current_status)

    @classmethod
    def wait_for_delete(
        cls, check_type, check_name, wait=120, interval=5, name_field=None
    ):
        total_sleep = 0
        name_field = name_field or 'Name'
        while total_sleep < wait:
            result = cls.openstack(check_type + ' list', parse_output=True)
            names = [x[name_field] for x in result]
            if check_name not in names:
                print(f'{check_type} {check_name} is now deleted')
                return
            print(f'Checking {check_type} {check_name} Waiting for deleted')
            time.sleep(interval)
            total_sleep += interval
        raise Exception(
            f'Timeout: {check_type} {check_name} was not deleted in {wait} seconds'
        )
