================
OpenStack Client
================

This is an unified command-line client for the OpenStack APIs.  It is
a thin wrapper to the stock python-*client modules that implement the
actual API clients.

This is an implementation of the design goals shown in 
http://wiki.openstack.org/UnifiedCLI.  The primary goal is to provide
a unified shell command structure and a common language to describe
operations in OpenStack.

Configuration
=============

The cli is entirely configured with environment variables and command-line
options.  It looks for the standard variables listed in
http://wiki.openstack.org/UnifiedCLI/Authentication for
the 'password flow' variation.

::

   export OS_AUTH_URL=url-to-openstack-identity
   export OS_TENANT_NAME=tenant
   export OS_USERNAME=user
   export OS_PASSWORD=password    # yes, it isn't secure, we'll address it in the future

The corresponding command-line options look very similar::

   --os-auth-url <url>
   --os-tenant-name <tenant-name>
   --os-username <user-name>
   --os-password <password>

Additional command-line options and their associated environment variables
are listed here::

   --debug             # turns on some debugging of the API conversation
                         (via httplib2)

