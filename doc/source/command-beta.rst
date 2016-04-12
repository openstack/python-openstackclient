============
Command Beta
============

OpenStackClient releases do not always coincide with OpenStack
releases. This creates challenges when developing new OpenStackClient
commands for the current OpenStack release under development
since there may not be an official release of the REST API
enhancements necessary for the command. In addition, backwards
compatibility may not be guaranteed until an official OpenStack release.
To address these challenges, an OpenStackClient command may
be labeled as a beta command according to the guidelines
below. Such commands may introduce backwards incompatible
changes and may use REST API enhancements not yet released.

See the examples below on how to label a command as a beta
by updating the command documentation, help and implementation.

The initial release note must label the new command as a beta.
No further release notes are required until the command
is no longer a beta. At which time, the command beta label
or the command itself must be removed and a new release note
must be provided.

Documentation
-------------

The command documentation must label the command as a beta.

example list
~~~~~~~~~~~~

List examples

.. caution:: This is a beta command and subject to change.
             Use global option ``--enable-beta-commands`` to
             enable this command.

.. program:: example list
.. code:: bash

    os example list

Help
----

The command help must label the command as a beta.

.. code-block:: python

    class ShowExample(command.ShowOne):
        """Display example details

           (Caution: This is a beta command and subject to change.
            Use global option --enable-beta-commands to enable
            this command)
        """

Implementation
--------------

The command must raise a ``CommandError`` exception if beta commands
are not enabled via ``--enable-beta-commands`` global option.

.. code-block:: python

    def take_action(self, parsed_args):
        if not self.app.options.enable_beta_commands:
            msg = _('Caution: This is a beta command and subject to '
                    'change. Use global option --enable-beta-commands '
                    'to enable this command.')
            raise exceptions.CommandError(msg)
