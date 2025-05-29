.. _authentication:

==============
Authentication
==============

OpenStackClient leverages `python-keystoneclient`_ authentication
plugins to support a number of different authentication methods.

.. _`python-keystoneclient`: https://docs.openstack.org/python-keystoneclient/latest/using-sessions.html#sharing-authentication-plugins

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
  in that a token and an authentication
  URL are supplied and the plugin retrieves a new token.
  [Required: ``--os-auth-url``, ``--os-token``]
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

Federated users support
-----------------------

The OpenStackClient also allows the use of Federated users to log in.
It enables one to use the identity providers credentials such as Google or
Facebook to log in the OpenStackClient instead of using the Keystone
credentials.

This is useful in a Federated environment where one credential give access
to many applications/services that the Federation supports. To check how to
configure the OpenStackClient to allow Federated users to log in, please check
the :ref:`Authentication using federation. <manpage>`

Examples
--------

.. todo: It would be nice to add more examples here, particularly for
   complicated things like oauth2

``v3password``
~~~~~~~~~~~~~~

Using ``clouds.yaml``:

.. code-block:: yaml

    clouds:
      demo:
        auth:
          auth_url: http://openstack.dev/identity
          project_name: demo
          project_domain_name: default
          user_domain_name: default
          username: demo
          password: password
        auth_type: v3password

or, using command line options:

.. code-block:: bash

    $ openstack \
      --os-auth-url "http://openstack.dev/identity" \
      --os-project-name demo \
      --os-project-domain-name default \
      --os-user-domain-name default \
      --os-auth-type=v3password \
      --os-username demo \
      --os-password password \
      server list

or, using environment variables:

.. code-block:: bash

    $ export OS_AUTH_URL="http://openstack.dev/identity"
    $ export OS_PROJECT_NAME=demo
    $ export OS_PROJECT_DOMAIN_NAME=default
    $ export OS_AUTH_TYPE=v3password
    $ export OS_USERNAME=demo
    $ export OS_PASSWORD=password
    $ openstack server list

.. note::

    If a password is not provided, you will be prompted for one.

``v3applicationcredential``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using ``clouds.yaml``:

.. code-block:: yaml

    clouds:
      demo:
        auth:
          auth_url: http://openstack.dev/identity
          application_credential_id: ${APP_CRED_ID}
          application_credential_secret: ${APP_CRED_SECRET}
        auth_type: v3applicationcredential

or, using command line options:

.. code-block:: bash

    $ openstack \
      --os-auth-url "http://openstack.dev/identity" \
      --os-auth-type=v3applicationcredential \
      --os-application-credential-id=${APP_CRED_ID} \
      --os-application-credential-secret=${APP_CRED_SECRET}
      server list

or, using environment variables:

.. code-block:: bash

    $ export OS_AUTH_URL="http://openstack.dev/identity"
    $ export OS_AUTH_TYPE=v3applicationcredential
    $ export OS_APPLICATION_CREDENTIAL_ID=${APP_CRED_ID}
    $ export OS_APPLICATION_CREDENTIAL_SECRET=${APP_CRED_SECRET}
    $ openstack server list

.. note::

    You can generate application credentials using the :program:`openstack
    application credential create` command:

    .. code-block:: bash

       $ readarray -t lines <<< $(openstack application credential create test -f value -c id -c secret)
       $ APP_CRED_ID=${lines[0]}
       $ APP_CRED_SECRET=${lines[1]}

``v3token``
~~~~~~~~~~~

Using ``clouds.yaml``:

.. code-block:: yaml

    clouds:
      demo:
        auth:
          auth_url: http://openstack.dev/identity
          project_name: demo
          project_domain_name: default
          token: ${TOKEN}
        auth_type: v3token

or, using command line options:

.. code-block:: bash

    $ openstack \
      --os-auth-url "http://openstack.dev/identity" \
      --os-project-name demo \
      --os-project-domain-name default \
      --os-auth-type=v3token \
      --os-token ${TOKEN} \
      server list

or, using environment variables:

.. code-block:: bash

    $ export OS_AUTH_URL="http://openstack.dev/identity"
    $ export OS_PROJECT_NAME=demo
    $ export OS_PROJECT_DOMAIN_NAME=default
    $ export OS_AUTH_TYPE=v3token
    $ export OS_TOKEN=${TOKEN}
    $ openstack server list

.. note::

    You can generate tokens using the :program:`openstack token issue` command:

    .. code-block:: bash

       $ TOKEN=$(openstack token issue -f value -c id)

.. note::

    The above examples assume you require a project-scoped token. You can omit
    the project-related configuration if your user has a default project ID set.
    Conversely, if requesting domain-scoped or system-scoped, you should update
    these examples accordingly. If the user does not have a default project
    configured and no scoping information is provided, the resulting token will
    be unscoped.

``v3totp``
~~~~~~~~~~

.. note::

    The TOTP mechanism is poorly suited to command line-driven API
    interactions. Where the TOTP mechanism is configured for a cloud, it is
    expected that it is to be used for initial authentication and to create a
    token or application credential, which can then be used for future
    interactions.

.. note::

    The TOTP mechanism is often combined with other mechanisms to enable
    Multi-Factor Authentication, or MFA. The authentication type
    ``v3multifactor`` is used in this case, while the ``v3totp`` authentication
    type is specified alongside the other mechanisms in ``auth_methods``.

Using ``clouds.yaml``:

.. code-block:: yaml

    clouds:
      demo:
        auth:
          auth_url: http://openstack.dev/identity
          project_name: demo
          project_domain_name: default
          user_domain_name: default
          username: demo
          passcode: ${PASSCODE}
        auth_type: v3totp

or, using command line options:

.. code-block:: bash

    $ openstack \
      --os-auth-url "http://openstack.dev/identity" \
      --os-project-name demo \
      --os-project-domain-name default \
      --os-user-domain-name default \
      --os-auth-type=v3totp \
      --os-username demo \
      --os-passcode ${PASSCODE} \
      server list

or, using environment variables:

.. code-block:: bash

    $ export OS_AUTH_URL="http://openstack.dev/identity"
    $ export OS_PROJECT_NAME=demo
    $ export OS_PROJECT_DOMAIN_NAME=default
    $ export OS_AUTH_TYPE=v3totp
    $ export OS_USERNAME=demo
    $ export OS_PASSCODE=${PASSCODE}
    $ openstack server list

.. note::

    The passcode will be generated by an authenticator application such FreeOTP
    or Google Authenticator. Refer to your cloud provider's documentation for
    information on how to configure an authenticator application, or to the
    `Keystone documentation`__ if you are configuring this for your own cloud.

    .. __: https://docs.openstack.org/keystone/latest/admin/auth-totp.html

.. note::

    If a passcode is not provided, you will be prompted for one.
