#!/usr/bin/env python
# object_api.py - Example object-store API usage

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Object Store API Examples

This script shows the basic use of the low-level Object Store API

"""

import argparse
import logging
import sys

import common
from os_client_config import config as cloud_config

from openstackclient.api import object_store_v1 as object_store
from openstackclient.identity import client as identity_client


LOG = logging.getLogger('')


def run(opts):
    """Run the examples"""

    # Look for configuration file
    # To support token-flow we have no required values
    # print "options: %s" % self.options
    cloud = cloud_config.OpenStackConfig().get_one_cloud(
        cloud=opts.cloud,
        argparse=opts,
    )
    LOG.debug("cloud cfg: %s", cloud.config)

    # Set up certificate verification and CA bundle
    # NOTE(dtroyer): This converts from the usual OpenStack way to the single
    #                requests argument and is an app-specific thing because
    #                we want to be like OpenStackClient.
    if opts.cacert:
        verify = opts.cacert
    else:
        verify = not opts.insecure

    # get a session
    # common.make_session() does all the ugly work of mapping
    # CLI options/env vars to the required plugin arguments.
    # The returned session will have a configured auth object
    # based on the selected plugin's available options.
    # So to do...oh, just go to api.auth.py and look at what it does.
    session = common.make_session(cloud, verify=verify)

    # Extract an endpoint
    auth_ref = session.auth.get_auth_ref(session)

    if opts.url:
        endpoint = opts.url
    else:
        endpoint = auth_ref.service_catalog.url_for(
            service_type='object-store',
            endpoint_type='public',
        )

    # At this point we have a working session with a configured authentication
    # plugin.  From here on it is the app making the decisions.  Need to
    # talk to two clouds?  Go back and make another session but with opts
    # set to different credentials.  Or use a config file and load it
    # directly into the plugin.  This example doesn't show that (yet).
    # Want to work ahead?  Look into the plugin load_from_*() methods
    # (start in keystoneclient/auth/base.py).

    # This example is for the Object Store API so make one
    obj_api = object_store.APIv1(
        session=session,
        service_type='object-store',
        endpoint=endpoint,
    )

    # Do useful things with it

    c_list = obj_api.container_list()
    print("Name\tCount\tBytes")
    for c in c_list:
        print("%s\t%d\t%d" % (c['name'], c['count'], c['bytes']))

    if len(c_list) > 0:
        # See what is in the first container
        o_list = obj_api.object_list(c_list[0]['name'])
        print("\nObject")
        for o in o_list:
            print("%s" % o)


if __name__ == "__main__":
    opts = common.base_parser(
        identity_client.build_option_parser(
            argparse.ArgumentParser(description='Object API Example')
        )
    ).parse_args()

    common.configure_logging(opts)
    sys.exit(common.main(opts, run))
