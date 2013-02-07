========
Commands
========

Command Structure
=================

OpenStack Client uses a command form ``verb object``.

Note that 'object' here refers to the target of a command's action.  In coding
discussions 'object' has its usual Python meaning.  Go figure.

Commands take the form::

    openstack [<global-options>] <verb> <object> [<command-local-arguments>]

Command Arguments
-----------------

  * All long option names use two dashes ('--') as the prefix and a single dash
    ('-') as the interpolation character.  Some common options also have the
    traditional single letter name prefixed by a single dash ('-').
  * Global options generally have a corresponding environment variable that
    may also be used to set the value. If both are present, the command-line
    option takes priority. The environment variable names can be derived from
    the option name by dropping the leading '--', converting all embedded dashes
    ('-') to underscores ('_'), and converting the name to upper case.
  * Positional arguments trail command options. In commands that require two or
    more objects be acted upon, such as 'attach A to B', both objects appear
    as positional arguments. If they also appear in the command object they are
    in the same order.


Implementation
==============

The command structure is designed to support seamless addition of extension
command modules via entry points.  The extensions are assumed to be subclasses
of Cliff's command.Command object.

Command Entry Points
--------------------

Commands are added to the client using distribute's entry points in ``setup.py``.
There is a single common group ``openstack.cli`` for commands that are not versioned,
and a group for each combination of OpenStack API and version that is
supported.  For example, to support Identity API v3 there is a group called
``openstack.identity.v3`` that contains the individual commands.  The command
entry points have the form::

    "verb_object=fully.qualified.module.vXX.object:VerbObject"

For example, the 'list user' command fir the Identity API is identified in
``setup.py`` with::

    'openstack.identity.v3': [
        # ...
        'list_user=openstackclient.identity.v3.user:ListUser',
        # ...
    ],
