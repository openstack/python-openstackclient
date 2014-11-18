====
user
====

Identity v2, v3

user create
-----------

Create new user

.. program:: user create
.. code:: bash

    os user create
        [--domain <domain>]
        [--project <project>]
        [--password <password>]
        [--password-prompt]
        [--email <email-address>]
        [--description <description>]
        [--enable | --disable]
        [--or-show]
        <user-name>

.. option:: --domain <domain>

    Default domain (name or ID)

    .. versionadded:: 3

.. option:: --project <project>

    Default project (name or ID)

.. option:: --password <password>

    Set user password

.. option:: --password-prompt

    Prompt interactively for password

.. option:: --email <email-address>

    Set user email address

.. option:: --description <description>

    User description

    .. versionadded:: 3

.. option:: --enable

    Enable user (default)

.. option:: --disable

    Disable user

.. option:: --or-show

    Return existing user

    If the username already exist return the existing user data and do not fail.

.. describe:: <name>

    New user name

user delete
-----------

Delete user

.. program:: user delete
.. code:: bash

    os user delete
        <user>

.. describe:: <user>

    User to delete (name or ID)

user list
---------

List users

.. program:: user list
.. code:: bash

    os user list
        [--domain <domain>]
        [--project <project>]
        [--group <group>]
        [--long]

.. option:: --domain <domain>

    Filter users by `<domain>` (name or ID)

    .. versionadded:: 3

.. option:: --project <project>

    Filter users by `<project>` (name or ID)

    *Removed in version 3.*

.. option:: --group <group>

    Filter users by `<group>` membership (name or ID)

    .. versionadded:: 3

.. option:: --long

    List additional fields in output

user set
--------

Set user properties

.. program:: user set
.. code:: bash

    os user set
        [--name <name>]
        [--domain <domain>]
        [--project <project>]
        [--password <password>]
        [--email <email-address>]
        [--description <description>]
        [--enable|--disable]
        <user>

.. option:: --name <name>

    Set user name

.. option:: --domain <domain>

    Set default domain (name or ID)

    .. versionadded:: 3

.. option:: --project <project>

    Set default project (name or ID)

.. option:: --password <password>

    Set user password

.. option:: --password-prompt

    Prompt interactively for password

.. option:: --email <email-address>

    Set user email address

.. option:: --description <description>

    Set user description

    .. versionadded:: 3

.. option:: --enable

    Enable user (default)

.. option:: --disable

    Disable user

.. describe:: <user>

    User to modify (name or ID)

user show
---------

.. program:: user show
.. code:: bash

    os user show
        [--domain <domain>]
        <user>

.. option:: --domain <domain>

    Domain owning :ref:`\<user\> <user_show-user>` (name or ID)

    .. versionadded:: 3

.. _user_show-user:
.. describe:: <user>

    User to show (name or ID)
