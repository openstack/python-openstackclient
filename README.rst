================
OpenStack Client
================

python-openstackclient is a unified command-line client for the OpenStack APIs.  It is
a thin wrapper to the stock python-*client modules that implement the
actual REST API client actions.

This is an implementation of the design goals shown in 
http://wiki.openstack.org/UnifiedCLI.  The primary goal is to provide
a unified shell command structure and a common language to describe
operations in OpenStack.

python-openstackclient is designed to add support for API extensions via a
plugin mechanism


Configuration
=============

The cli is configured via environment variables and command-line
options as listed in http://wiki.openstack.org/UnifiedCLI/Authentication.

The 'password flow' variation is most commonly used::

   export OS_AUTH_URL=<url-to-openstack-identity>
   export OS_TENANT_NAME=<tenant-name>
   export OS_USERNAME=<user-name>
   export OS_PASSWORD=<password>    # yes, it isn't secure, we'll address it in the future

The corresponding command-line options look very similar::

   --os-auth-url <url>
   --os-tenant-name <tenant-name>
   --os-username <user-name>
   --os-password <password>

The token flow variation for authentication uses an already-aquired token
and a URL pointing directly to the service API that presumably was acquired
from the Service Catalog::

    export OS_TOKEN=<token>
    export OS_URL=<url-to-openstack-service>

The corresponding command-line options look very similar::

    --os-token <token>
    --os-url <url-to-openstack-service>

Additional command-line options and their associated environment variables
are listed here::

   --debug             # turns on some debugging of the API conversation
                         (via httplib2)
   --verbose | -v      # Increase verbosity of output. Can be repeated.
   --quiet | -q        # suppress output except warnings and errors
   --help | -h         # show a help message and exit