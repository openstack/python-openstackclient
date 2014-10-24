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

* A new ``ClientManager`` is created and supplied with the set of options from the
  command line and/or environment:

  * If ``--os-auth-type`` is provided and is a valid and available plugin
      it is used.
  * If ``--os-auth-type`` is not provided an authentication plugin
    is selected based on the existing options.  This is a short-circuit
    evaluation, the first match wins.

    * If ``--os-endpoint`` and ``--os-token`` are both present ``token_endpoint``
      is selected
    * If ``--os-username`` is supplied ``password`` is selected
    * If ``--os-token`` is supplied ``token`` is selected
    * If no selection has been made by now exit with error

  * Load the selected plugin class.

* When an operation that requires authentication is attempted ``ClientManager``
  makes the actual inital request to the Identity service.

  * if ``--os-auth-url`` is not supplied for any of the types except
    Token/Endpoint, exit with an error.
