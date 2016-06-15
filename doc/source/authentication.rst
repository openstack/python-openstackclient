==============
Authentication
==============

OpenStackClient leverages `python-keystoneclient`_ authentication
plugins to support a number of different authentication methods.

.. _`python-keystoneclient`: http://docs.openstack.org/developer/python-keystoneclient/authentication-plugins.html

Authentication Process
----------------------

The user provides some number of authentication credential options.
If an authentication type is not provided (``--os-auth-type``), the
authentication options are examined to determine if one of the default
types can be used. If no match is found an error is reported and OSC exits.

Note that the authentication call to the Identity service has not yet
occurred. It is deferred until the last possible moment in order to
reduce the number of unnecessary queries to the server, such as when further
processing detects an invalid command.

Authentication Plugins
----------------------

The Keystone client library implements the base set of plugins. Additional
plugins may be available from the Keystone project or other sources.

There are at least three authentication types that are always available:

* **Password**: A project, username and password are used to identify the
  user.  An optional domain may also be included. This is the most common
  type and is the default any time a username is supplied.  An authentication
  URL for the Identity service is also required. [Required: ``--os-auth-url``,
  ``--os-project-name``, ``--os-username``; Optional: ``--os-password``]
* **Token**: This is slightly different from the usual token authentication
  (described below as token/endpoint) in that a token and an authentication
  URL are supplied and the plugin retrieves a new token.
  [Required: ``--os-auth-url``, ``--os-token``]
* **Token/Endpoint**: This is the original token authentication (known as 'token
  flow' in the early CLI documentation in the OpenStack wiki).  It requires
  a token and a direct endpoint that is used in the API call.  The difference
  from the new Token type is this token is used as-is, no call is made
  to the Identity service from the client.  This type is most often used to
  bootstrap a Keystone server where the token is the ``admin_token`` configured
  in ``keystone.conf``.  It will also work with other services and a regular
  scoped token such as one obtained from a ``token issue`` command.
  [Required: ``--os-url``, ``--os-token``]
* **Others**: Other authentication plugins such as SAML, Kerberos, and OAuth1.0
  are under development and also supported. To use them, they must be selected
  by supplying the ``--os-auth-type`` option.

Detailed Process
----------------

The authentication process in OpenStackClient is all contained in and handled
by the ``ClientManager`` object.

* On import ``api.auth``:

  * obtains the list of installed Keystone authentication
    plugins from the ``keystoneclient.auth.plugin`` entry point.
  * builds a list of authentication options from the plugins.

* The command line arguments are processed and a configuration is loaded from
  :file:`clouds.yaml` if ``--os-cloud`` is provided.

* A new ``ClientManager`` is created and supplied with the set of options from the
  command line, environment and/or :file:`clouds.yaml`:

  * If ``--os-auth-type`` is provided and is a valid and available plugin
      it is used.
  * If ``--os-auth-type`` is not provided an authentication plugin
    is selected based on the existing options.  This is a short-circuit
    evaluation, the first match wins.

    * If ``--os-url`` and ``--os-token`` are both present ``token_endpoint``
      is selected
    * If ``--os-username`` is supplied ``password`` is selected
    * If ``--os-token`` is supplied ``token`` is selected
    * If no selection has been made by now exit with error

  * Load the selected plugin class.

* When an operation that requires authentication is attempted ``ClientManager``
  makes the actual initial request to the Identity service.

  * if ``--os-auth-url`` is not supplied for any of the types except
    Token/Endpoint, exit with an error.

Authenticating using Identity Server API v3
-------------------------------------------

To authenticate against an Identity Server API v3, the
``OS_IDENTITY_API_VERSION`` environment variable or
``--os-identity-api-version`` option must be changed to ``3``, instead of the
default ``2.0``. Similarly ``OS_AUTH_URL`` or ``os-auth-url`` should also be
updated.

.. code-block:: bash

    $ export OS_IDENTITY_API_VERSION=3 (Defaults to 2.0)
    $ export OS_AUTH_URL=http://localhost:5000/v3

Since Identity API v3 authentication is a bit more complex, there are additional
options that may be set, either as command line options or environment
variables. The most common case will be a user supplying both user name and
password, along with the project name; previously in v2.0 this would be
sufficient, but since the Identity API v3 has a ``Domain`` component, we need
to tell the client in which domain the user and project exists.

If using a user name and password to authenticate, specify either it's owning
domain name or ID.

  * ``--os-user-domain-name`` or ``OS_USER_DOMAIN_NAME``

  * ``--os-user-domain-id`` or ``OS_USER_DOMAIN_ID``

If using a project name as authorization scope, specify either it's owning
domain name or ID.

  * ``--os-project-domain-name`` or ``OS_PROJECT_DOMAIN_NAME``

  * ``--os-project-domain-id`` or ``OS_PROJECT_DOMAIN_ID``

If using a domain as authorization scope, set either it's name or ID.

  * ``--os-domain-name`` or ``OS_DOMAIN_NAME``

  * ``--os-domain-id`` or ``OS_DOMAIN_ID``

Note that if the user and project share the same domain, then simply setting
``--os-default-domain`` or ``OS_DEFAULT_DOMAIN`` to the domain ID is sufficient.

Thus, a minimal set of environment variables would be:

.. code-block:: bash

    $ export OS_IDENTITY_API_VERSION=3
    $ export OS_AUTH_URL=http://localhost:5000/v3
    $ export OS_DEFAULT_DOMAIN=default
    $ export OS_USERNAME=admin
    $ export OS_PASSWORD=secret
    $ export OS_PROJECT_NAME=admin
