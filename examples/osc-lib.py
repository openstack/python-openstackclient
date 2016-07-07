#!/usr/bin/env python
# osc-lib.py - Example using OSC as a library

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
OpenStackClient Library Examples

This script shows the basic use of the OpenStackClient ClientManager
as a library.

"""

import argparse
import logging
import sys

import common
from os_client_config import config as cloud_config

from openstackclient.common import clientmanager


LOG = logging.getLogger('')


def run(opts):
    """Run the examples"""

    # Do configuration file handling
    cc = cloud_config.OpenStackConfig()
    LOG.debug("defaults: %s", cc.defaults)

    cloud = cc.get_one_cloud(
        cloud=opts.cloud,
        argparse=opts,
    )
    LOG.debug("cloud cfg: %s", cloud.config)

    # Loop through extensions to get API versions
    # Currently API versions are statically selected.  Once discovery
    # is working this can go away...
    api_version = {}
    for mod in clientmanager.PLUGIN_MODULES:
        version_opt = getattr(opts, mod.API_VERSION_OPTION, None)
        if version_opt:
            api = mod.API_NAME
            api_version[api] = version_opt

    # Set up certificate verification and CA bundle
    # NOTE(dtroyer): This converts from the usual OpenStack way to the single
    #                requests argument and is an app-specific thing because
    #                we want to be like OpenStackClient.
    if opts.cacert:
        verify = opts.cacert
    else:
        verify = not opts.insecure

    # Get a ClientManager
    # Collect the auth and config options together and give them to
    # ClientManager and it will wrangle all of the goons into place.
    client_manager = clientmanager.ClientManager(
        cli_options=cloud,
        verify=verify,
        api_version=api_version,
    )

    # At this point we have a working client manager with a configured
    # session and authentication plugin.  From here on it is the app
    # making the decisions.  Need to talk to two clouds?  Make another
    # client manager with different opts.  Or use a config file and load it
    # directly into the plugin.  This example doesn't show that (yet).

    # Do useful things with it

    # Look in the object store
    c_list = client_manager.object_store.container_list()
    print("Name\tCount\tBytes")
    for c in c_list:
        print("%s\t%d\t%d" % (c['name'], c['count'], c['bytes']))

    if len(c_list) > 0:
        # See what is in the first container
        o_list = client_manager.object_store.object_list(c_list[0]['name'])
        print("\nObject")
        for o in o_list:
            print("%s" % o)

    # Look at the compute flavors
    flavor_list = client_manager.compute.flavors.list()
    print("\nFlavors:")
    for f in flavor_list:
        print("%s" % f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ClientManager Example')
    opts = common.base_parser(
        clientmanager.build_plugin_option_parser(parser),
    ).parse_args()

    common.configure_logging(opts)
    sys.exit(common.main(opts, run))
