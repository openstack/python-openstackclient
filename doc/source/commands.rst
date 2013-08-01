========
Commands
========


Command Structure
=================

OpenStackClient has a consistent and predictable format for all of its commands.

Commands take the form::

    openstack [<global-options>] <object> <action> [<second-object>] [<command-arguments>]

* All long options names begin with two dashes ('--') and use a single dash ('-') internally between words (--like-this)


Global Options
--------------

Global options are global in the sense that the apply to every command invocation regardless of action to be performed. This includes authentication credentials and API version selection. Most global options have a corresponding environment variable that may also be used to set the value. If both are present, the command-line option takes priority. The environment variable names are derived from the option name by dropping the leading dashes ('--'), converting each embedded dash ('-') to an underscore ('_'), and converting to upper case.

For example, ``--os-username`` can be set from the environment via ``OS_USERNAME``.


Command Object(s) and Action
----------------------------

Commands consist of an object described by one or more words followed by an action.
In commands requiring two objects be acted upon, the primary object appears ahead of the action and the secondary object appears after the action.
If both objects have cooresponding positional arguments the arguments appear in the same order as the objects. In badly formed English it is expressed as "(Take) object1 (and perform) action (using) object2 (to it)."

::

    <object-1> <action> <object-2>

Examples::

    group add user <group> <user>

    volume type list   # 'volume type' is a two-word single object


Command Arguments and Options
-----------------------------

Commands have their own set of options distinct from the global options.  They follow the
same style as the global options and always appear between the command and any positional arguemnts the command may require.


Implementation
==============

The command structure is designed to support seamless addition of extension
command modules via entry points.  The extensions are assumed to be subclasses
of Cliff's command.Command object.


Command Entry Points
--------------------

Commands are added to the client using setuptools's entry points in ``setup.cfg``.
There is a single common group ``openstack.cli`` for commands that are not versioned,
and a group for each combination of OpenStack API and version that is
supported.  For example, to support Identity API v3 there is a group called
``openstack.identity.v3`` that contains the individual commands.  The command
entry points have the form::

    verb_object = fully.qualified.module.vXX.object:VerbObject

For example, the 'list user' command fir the Identity API is identified in
``setup.cfg`` with::

    openstack.identity.v3 =
        # ...
        list_user = openstackclient.identity.v3.user:ListUser
        # ...
