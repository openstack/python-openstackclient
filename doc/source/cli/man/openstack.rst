.. _manpage:

====================
:program:`openstack`
====================

OpenStack Command Line


SYNOPSIS
========

:program:`openstack` [<global-options>] <command> [<command-arguments>]

:program:`openstack help` <command>

:program:`openstack` :option:`--help`


DESCRIPTION
===========

:program:`openstack` provides a common command-line interface to OpenStack APIs.  It is generally
equivalent to the CLIs provided by the OpenStack project client libraries, but with
a distinct and consistent command structure.


AUTHENTICATION METHODS
======================

:program:`openstack` uses a similar authentication scheme as the OpenStack project CLIs, with
the credential information supplied either as environment variables or as options on the
command line.  The primary difference is the use of 'project' in the name of the options
``OS_PROJECT_NAME``/``OS_PROJECT_ID`` over the old tenant-based names.

::

    export OS_AUTH_URL=<url-to-openstack-identity>
    export OS_PROJECT_NAME=<project-name>
    export OS_USERNAME=<user-name>
    export OS_PASSWORD=<password>  # (optional)

:program:`openstack` can use different types of authentication plugins provided by the keystoneclient library. The following default plugins are available:

* ``token``: Authentication with a token
* ``password``: Authentication with a username and a password
* ``openid`` : Authentication using the protocol OpenID Connect

Refer to the keystoneclient library documentation for more details about these plugins and their options, and for a complete list of available plugins.
Please bear in mind that some plugins might not support all of the functionalities of :program:`openstack`; for example the v3unscopedsaml plugin can deliver only unscoped tokens, some commands might not be available through this authentication method.

Additionally, it is possible to use Keystone's service token to authenticate, by setting the options :option:`--os-token` and :option:`--os-endpoint` (or the environment variables :envvar:`OS_TOKEN` and :envvar:`OS_ENDPOINT` respectively). This method takes precedence over authentication plugins.

.. NOTE::
    To use the ``v3unscopedsaml`` method, the lxml package will need to be installed.

AUTHENTICATION USING FEDERATION
-------------------------------

To use federated authentication, your configuration file needs the following:

::

    export OS_PROJECT_NAME=<project-name>
    export OS_PROJECT_DOMAIN_NAME=<project-domain-name>
    export OS_AUTH_URL=<url-to-openstack-identity>
    export OS_IDENTITY_API_VERSION=3
    export OS_AUTH_PLUGIN=openid
    export OS_AUTH_TYPE=v3oidcpassword
    export OS_USERNAME=<username-in-idp>
    export OS_PASSWORD=<password-in-idp>
    export OS_IDENTITY_PROVIDER=<the-desired-idp>
    export OS_CLIENT_ID=<the-client-id-configured-in-the-idp>
    export OS_CLIENT_SECRET=<the-client-secred-configured-in-the-idp>
    export OS_OPENID_SCOPE=<the-scopes-of-desired-attributes-to-claim-from-idp>
    export OS_PROTOCOL=<the-protocol-used-in-the-apache2-oidc-proxy>
    export OS_ACCESS_TOKEN_TYPE=<the-access-token-type-used-by-your-idp>
    export OS_DISCOVERY_ENDPOINT=<the-well-known-endpoint-of-the-idp>
    export OS_ACCESS_TOKEN_ENDPOINT=<the-idp-access-token-url>


OPTIONS
=======

:program:`openstack` takes global options that control overall behaviour and command-specific options that control the command operation.  Most global options have a corresponding environment variable that may also be used to set the value. If both are present, the command-line option takes priority. The environment variable names are derived from the option name by dropping the leading dashes ('--'), converting each embedded dash ('-') to an underscore ('_'), and converting to upper case.

:program:`openstack` recognizes the following global options:

.. option:: --os-cloud <cloud-name>

    :program:`openstack` will look for a ``clouds.yaml`` file that contains
    a cloud configuration to use for authentication.  See CLOUD CONFIGURATION
    below for more information.

.. option::  --os-auth-type <auth-type>

    The authentication plugin type to use when connecting to the Identity service.

    If this option is not set, :program:`openstack` will attempt to guess the
    authentication method to use based on the other options.

    If this option is set, its version must match
    :option:`--os-identity-api-version`

.. option:: --os-auth-url <auth-url>

    Authentication URL

.. option:: --os-endpoint <service-url>

    Service ENDPOINT, when using a service token for authentication

.. option:: --os-domain-name <auth-domain-name>

    Domain-level authorization scope (by name)

.. option:: --os-domain-id <auth-domain-id>

    Domain-level authorization scope (by ID)

.. option:: --os-project-name <auth-project-name>

    Project-level authentication scope (by name)

.. option:: --os-project-id <auth-project-id>

    Project-level authentication scope (by ID)

.. option:: --os-project-domain-name <auth-project-domain-name>

    Domain name containing project

.. option:: --os-project-domain-id <auth-project-domain-id>

    Domain ID containing project

.. option:: --os-username <auth-username>

    Authentication username

.. option:: --os-password <auth-password>

    Authentication password

.. option:: --os-token <token>

    Authenticated token or service token

.. option:: --os-user-domain-name <auth-user-domain-name>

    Domain name containing user

.. option:: --os-user-domain-id <auth-user-domain-id>

    Domain ID containing user

.. option:: --os-trust-id <trust-id>

    ID of the trust to use as a trustee user

.. option:: --os-default-domain <auth-domain>

    Default domain ID (Default: 'default')

.. option:: --os-region-name <auth-region-name>

    Authentication region name

.. option:: --os-cacert <ca-bundle-file>

    CA certificate bundle file

.. option:: --verify` | :option:`--insecure

    Verify or ignore server certificate (default: verify)

.. option:: --os-cert <certificate-file>

    Client certificate bundle file

.. option:: --os-key <key-file>

    Client certificate key file

.. option:: --os-identity-api-version <identity-api-version>

    Identity API version (Default: 2.0)

.. option:: --os-XXXX-api-version <XXXX-api-version>

    Additional API version options will be available depending on the installed
    API libraries.

.. option:: --os-interface <interface>

    Interface type. Valid options are `public`, `admin` and `internal`.

.. NOTE::
    If you switch to openstackclient from project specified clients, like:
    novaclient, neutronclient and so on, please use `--os-interface` instead of
    `--os-endpoint-type`.

.. option:: --os-profile <hmac-key>

    Performance profiling HMAC key for encrypting context data

    This key should be the value of one of the HMAC keys defined in the
    configuration files of OpenStack services to be traced.

.. option:: --os-beta-command

    Enable beta commands which are subject to change

.. option:: --log-file <LOGFILE>

    Specify a file to log output. Disabled by default.

.. option:: -v, --verbose

    Increase verbosity of output. Can be repeated.

.. option:: -q, --quiet

    Suppress output except warnings and errors

.. option:: --debug

    Show tracebacks on errors and set verbosity to debug

.. option:: --help

    Show help message and exit

.. option:: --timing

    Print API call timing information

COMMANDS
========

To get a list of the available commands::

    openstack --help

To get a description of a specific command::

    openstack help <command>

Note that the set of commands shown will vary depending on the API versions
that are in effect at that time.  For example, to force the display of the
Identity v3 commands::

    openstack --os-identity-api-version 3 --help

.. option:: complete

    Print the bash completion functions for the current command set.

.. option:: help <command>

    Print help for an individual command

Additional information on the OpenStackClient command structure and arguments
is available in the `OpenStackClient Commands`_ wiki page.

.. _`OpenStackClient Commands`: https://wiki.openstack.org/wiki/OpenStackClient/Commands

Command Objects
---------------

The list of command objects is growing longer with the addition of OpenStack
project support.  The object names may consist of multiple words to compose a
unique name.  Occasionally when multiple APIs have a common name with common
overlapping purposes there will be options to select which object to use, or
the API resources will be merged, as in the ``quota`` object that has options
referring to both Compute and Block Storage quotas.

Command Actions
---------------

The actions used by OpenStackClient are defined with specific meaning to provide a consistent behavior for each object.  Some actions have logical opposite actions, and those pairs will always match for any object that uses them.


CLOUD CONFIGURATION
===================

Working with multiple clouds can be simplified by keeping the configuration
information for those clouds in a local file.  :program:`openstack` supports
using a ``clouds.yaml`` configuration file.

Config Files
------------

:program:`openstack` will look for a file called clouds.yaml in the following
locations:

* Current Directory
* ~/.config/openstack
* /etc/openstack

The first file found wins.

The keys match the :program:`openstack` global options but without the
``--os-`` prefix:

::

    clouds:
      devstack:
        auth:
          auth_url: http://192.168.122.10:5000/
          project_name: demo
          username: demo
          password: 0penstack
        region_name: RegionOne
      ds-admin:
        auth:
          auth_url: http://192.168.122.10:5000/
          project_name: admin
          username: admin
          password: 0penstack
        region_name: RegionOne
      infra:
        cloud: rackspace
        auth:
          project_id: 275610
          username: openstack
          password: xyzpdq!lazydog
        region_name: DFW,ORD,IAD

In the above example, the ``auth_url`` for the ``rackspace`` cloud is taken
from :file:`clouds-public.yaml`:

::

    public-clouds:
      rackspace:
        auth:
          auth_url: 'https://identity.api.rackspacecloud.com/v2.0/'

Authentication Settings
-----------------------

OpenStackClient uses the Keystone authentication plugins so the required
auth settings are not always known until the authentication type is
selected.  :program:`openstack` will attempt to detect a couple of common
auth types based on the arguments passed in or found in the configuration
file, but if those are incomplete it may be impossible to know which
auth type is intended.  The :option:`--os-auth-type` option can always be
used to force a specific type.

When :option:`--os-token` and :option:`--os-endpoint` are both present the
``token_endpoint`` auth type is selected automatically.  If
:option:`--os-auth-url` and :option:`--os-username` are present ``password``
auth type is selected.

Logging Settings
----------------

:program:`openstack` can record the operation history by logging settings
in configuration file. Recording the user operation, it can identify the
change of the resource and it becomes useful information for troubleshooting.

See :ref:`configuration` about Logging Settings for more details.


NOTES
=====

The command list displayed in help output reflects the API versions selected.  For
example, to see Identity v3 commands ``OS_IDENTITY_API_VERSION`` must be set to ``3``.


EXAMPLES
========

Show the detailed information for server ``appweb01``::

    openstack \
        --os-project-name ExampleCo \
        --os-username demo --os-password secret \
        --os-auth-url http://localhost:5000:/v2.0 \
        server show appweb01

The same but using openid to authenticate in keystone::

    openstack \
        --os-project-name ExampleCo \
        --os-auth-url http://localhost:5000:/v2.0 \
        --os-auth-plugin openid \
        --os-auth-type v3oidcpassword \
        --os-username demo-idp \
        --os-password secret-idp \
        --os-identity-provider google \
        --os-client-id the-id-assigned-to-keystone-in-google \
        --os-client-secret 3315162f-2b28-4809-9369-cb54730ac837 \
        --os-openid-scope 'openid email profile'\
        --os-protocol openid \
        --os-access-token-type access_token \
        --os-discovery-endpoint https://accounts.google.com/.well-known/openid-configuration \
        server show appweb01

The same command if the auth environment variables (:envvar:`OS_AUTH_URL`, :envvar:`OS_PROJECT_NAME`,
:envvar:`OS_USERNAME`, :envvar:`OS_PASSWORD`) are set::

    openstack server show appweb01

Create a new image::

    openstack image create \
        --disk-format=qcow2 \
        --container-format=bare \
        --public \
        --copy-from http://somewhere.net/foo.img \
        foo


FILES
=====

:file:`~/.config/openstack/clouds.yaml`
    Configuration file used by the :option:`--os-cloud` global option.

:file:`~/.config/openstack/clouds-public.yaml`
    Configuration file containing public cloud provider information such as
    authentication URLs and service definitions.  The contents of this file
    should be public and sharable.  ``clouds.yaml`` may contain references
    to clouds defined here as shortcuts.

:file:`~/.openstack`
    Placeholder for future local state directory.  This directory is intended to be shared among multiple OpenStack-related applications; contents are namespaced with an identifier for the app that owns it.  Shared contents (such as :file:`~/.openstack/cache`) have no prefix and the contents must be portable.


ENVIRONMENT VARIABLES
=====================

The following environment variables can be set to alter the behaviour of :program:`openstack`.  Most of them have corresponding command-line options that take precedence if set.

.. envvar:: OS_CLOUD

    The name of a cloud configuration in ``clouds.yaml``.

.. envvar:: OS_AUTH_PLUGIN

    The authentication plugin to use when connecting to the Identity service, its version must match the Identity API version

.. envvar:: OS_AUTH_URL

    Authentication URL

.. envvar:: OS_AUTH_TYPE

    Define the authentication plugin that will be used to handle the
    authentication process. One of the following:

    - ``v2password``
    - ``v2token``
    - ``v3password``
    - ``v3token``
    - ``v3oidcclientcredentials``
    - ``v3oidcpassword``
    - ``v3oidcauthorizationcode``
    - ``v3oidcaccesstoken``
    - ``v3totp``
    - ``v3tokenlessauth``
    - ``v3applicationcredential``
    - ``v3multifactor``

.. envvar:: OS_ENDPOINT

    Service ENDPOINT (when using the service token)

.. envvar:: OS_DOMAIN_NAME

    Domain-level authorization scope (name or ID)

.. envvar:: OS_PROJECT_NAME

    Project-level authentication scope (name or ID)

.. envvar:: OS_PROJECT_DOMAIN_NAME

    Domain name or ID containing project

.. envvar:: OS_USERNAME

    Authentication username

.. envvar:: OS_TOKEN

    Authenticated or service token

.. envvar:: OS_PASSWORD

    Authentication password

.. envvar:: OS_USER_DOMAIN_NAME

    Domain name or ID containing user

.. envvar:: OS_TRUST_ID

    ID of the trust to use as a trustee user

.. envvar:: OS_DEFAULT_DOMAIN

    Default domain ID (Default: 'default')

.. envvar:: OS_REGION_NAME

    Authentication region name

.. envvar:: OS_CACERT

    CA certificate bundle file

.. envvar:: OS_CERT

    Client certificate bundle file

.. envvar:: OS_KEY

    Client certificate key file

.. envvar:: OS_IDENTITY_API_VERSION

    Identity API version (Default: 2.0)

.. envvar:: OS_XXXX_API_VERSION

    Additional API version options will be available depending on the installed
    API libraries.

.. envvar:: OS_INTERFACE

    Interface type. Valid options are `public`, `admin` and `internal`.

.. envvar:: OS_PROTOCOL

    Define the protocol that is used to execute the federated authentication
    process. It is used in the Keystone authentication URL generation process.

.. envvar:: OS_IDENTITY_PROVIDER

    Define the identity provider of your federation that will be used. It is
    used by the Keystone authentication URL generation process. The available
    Identity Providers can be listed using the
    :program:`openstack identity provider list` command

.. envvar:: OS_CLIENT_ID

    Configure the ``CLIENT_ID`` that the CLI will use to authenticate the
    application (OpenStack) in the Identity Provider. This value is defined on
    the identity provider side. Do not confuse with the user ID.

.. envvar:: OS_CLIENT_SECRET

    Configure the OS_CLIENT_SECRET that the CLI will use to authenticate the
    CLI (OpenStack secret in the identity provider).

.. envvar:: OS_OPENID_SCOPE

    Configure the attribute scopes that will be claimed by the Service Provider
    (SP), in this case OpenStack, from the identity provider. These scopes and
    which attributes each scope contains are defined in the identity provider
    side. This parameter can receive multiple values separated by space.

.. envvar:: OS_ACCESS_TOKEN_TYPE

    Define the type of access token that is used in the token introspection
    process.
    This variable can assume only one of the states ("access_token" or
    "id_token").

.. envvar:: OS_DISCOVERY_ENDPOINT

    Configure the identity provider's discovery URL. This URL will provide a
    discover document that contains metadata describing the identity provider
    endpoints. This variable is optional if the variable
    ``OS_ACCESS_TOKEN_ENDPOINT`` is defined.

.. envvar::  OS_ACCESS_TOKEN_ENDPOINT

    Overrides the value presented in the discovery document retrieved from
    ``OS_DISCOVERY_ENDPOINT`` URL request. This variable is optional if the
    ``OS_DISCOVERY_ENDPOINT`` is configured.

.. NOTE::
    If you switch to openstackclient from project specified clients, like:
    novaclient, neutronclient and so on, please use `OS_INTERFACE` instead of
    `OS_ENDPOINT_TYPE`.

BUGS
====

Bug reports are accepted at the python-openstackclient Launchpad project
"https://bugs.launchpad.net/python-openstackclient".


AUTHORS
=======

Please refer to the AUTHORS file distributed with OpenStackClient.


COPYRIGHT
=========

Copyright 2011-2014 OpenStack Foundation and the authors listed in the AUTHORS file.


LICENSE
=======

http://www.apache.org/licenses/LICENSE-2.0


SEE ALSO
========

The `OpenStackClient page <https://docs.openstack.org/python-openstackclient/latest/>`_
in the `OpenStack Docs <https://docs.openstack.org/>`_ contains further
documentation.

The individual OpenStack project CLIs, the OpenStack API references.
