# Copyright 2023 Red Hat.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest.mock import call

from openstack import exceptions as sdk_exceptions
from osc_lib import exceptions

from openstackclient.image.v2 import cache
from openstackclient.tests.unit.image.v2 import fakes


class TestCacheList(fakes.TestImagev2):
    _cache = fakes.create_cache()
    columns = [
        "ID",
        "State",
        "Last Accessed (UTC)",
        "Last Modified (UTC)",
        "Size",
        "Hits",
    ]

    cache_list = cache._format_image_cache(dict(fakes.create_cache()))
    datalist = (
        (
            image['image_id'],
            image['state'],
            image['last_accessed'],
            image['last_modified'],
            image['size'],
            image['hits'],
        )
        for image in cache_list
    )

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.image_client.get_image_cache.return_value = self._cache
        self.cmd = cache.ListCachedImage(self.app, None)

    def test_image_cache_list(self):
        arglist = []
        parsed_args = self.check_parser(self.cmd, arglist, [])
        columns, data = self.cmd.take_action(parsed_args)

        self.image_client.get_image_cache.assert_called()
        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.datalist), tuple(data))


class TestQueueCache(fakes.TestImagev2):
    def setUp(self):
        super().setUp()

        self.image_client.queue_image.return_value = None
        self.cmd = cache.QueueCachedImage(self.app, None)

    def test_cache_queue(self):
        images = fakes.create_images(count=1)
        arglist = [
            images[0].id,
        ]

        verifylist = [
            ('images', [images[0].id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.image_client.find_image.side_effect = images

        self.cmd.take_action(parsed_args)

        self.image_client.queue_image.assert_called_once_with(images[0].id)

    def test_cache_queue_multiple_images(self):
        images = fakes.create_images(count=3)
        arglist = [i.id for i in images]

        verifylist = [
            ('images', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.image_client.find_image.side_effect = images

        self.cmd.take_action(parsed_args)
        calls = [call(i.id) for i in images]
        self.image_client.queue_image.assert_has_calls(calls)


class TestCacheDelete(fakes.TestImagev2):
    def setUp(self):
        super().setUp()

        self.image_client.cache_delete_image.return_value = None
        self.cmd = cache.DeleteCachedImage(self.app, None)

    def test_cache_delete(self):
        images = fakes.create_images(count=1)
        arglist = [
            images[0].id,
        ]

        verifylist = [
            ('images', [images[0].id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.image_client.find_image.side_effect = images

        self.cmd.take_action(parsed_args)

        self.image_client.find_image.assert_called_once_with(
            images[0].id, ignore_missing=False
        )
        self.image_client.cache_delete_image.assert_called_once_with(
            images[0].id
        )

    def test_cache_delete_multiple_images(self):
        images = fakes.create_images(count=3)
        arglist = [i.id for i in images]

        verifylist = [
            ('images', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.image_client.find_image.side_effect = images

        self.cmd.take_action(parsed_args)
        calls = [call(i.id) for i in images]
        self.image_client.cache_delete_image.assert_has_calls(calls)

    def test_cache_delete_multiple_images_exception(self):
        images = fakes.create_images(count=2)
        arglist = [
            images[0].id,
            images[1].id,
            'x-y-x',
        ]
        verifylist = [
            ('images', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ret_find = [images[0], images[1], sdk_exceptions.ResourceNotFound()]

        self.image_client.find_image.side_effect = ret_find

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        calls = [call(i.id) for i in images]
        self.image_client.cache_delete_image.assert_has_calls(calls)


class TestCacheClear(fakes.TestImagev2):
    def setUp(self):
        super().setUp()

        self.image_client.clear_cache.return_value = None
        self.cmd = cache.ClearCachedImage(self.app, None)

    def test_cache_clear_no_option(self):
        arglist = []

        verifylist = [('target', 'both')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.assertIsNone(
            self.image_client.clear_cache.assert_called_with('both')
        )

    def test_cache_clear_queue_option(self):
        arglist = ['--queue']

        verifylist = [('target', 'queue')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.image_client.clear_cache.assert_called_once_with('queue')

    def test_cache_clear_cache_option(self):
        arglist = ['--cache']

        verifylist = [('target', 'cache')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.image_client.clear_cache.assert_called_once_with('cache')
