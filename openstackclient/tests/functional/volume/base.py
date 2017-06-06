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

import json
import time

from openstackclient.tests.functional import base


class BaseVolumeTests(base.TestCase):
    """Base class for Volume functional tests. """

    @classmethod
    def wait_for_status(cls, check_type, check_name, desired_status,
                        wait=120, interval=5, failures=None):
        current_status = "notset"
        if failures is None:
            failures = ['error']
        total_sleep = 0
        while total_sleep < wait:
            output = json.loads(cls.openstack(
                check_type + ' show -f json ' + check_name))
            current_status = output['status']
            if (current_status == desired_status):
                print('{} {} now has status {}'
                      .format(check_type, check_name, current_status))
                return
            print('Checking {} {} Waiting for {} current status: {}'
                  .format(check_type, check_name,
                          desired_status, current_status))
            if current_status in failures:
                raise Exception(
                    'Current status {} of {} {} is one of failures {}'
                    .format(current_status, check_type, check_name, failures))
            time.sleep(interval)
            total_sleep += interval
        cls.assertOutput(desired_status, current_status)

    @classmethod
    def wait_for_delete(cls, check_type, check_name, wait=120, interval=5,
                        name_field=None):
        total_sleep = 0
        name_field = name_field or 'Name'
        while total_sleep < wait:
            result = json.loads(cls.openstack(check_type + ' list -f json'))
            names = [x[name_field] for x in result]
            if check_name not in names:
                print('{} {} is now deleted'.format(check_type, check_name))
                return
            print('Checking {} {} Waiting for deleted'
                  .format(check_type, check_name))
            time.sleep(interval)
            total_sleep += interval
        raise Exception('Timeout: {} {} was not deleted in {} seconds'
                        .format(check_type, check_name, wait))
