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
This also applies to command options associated with the beta
command object.

See the examples below on how to label an entire command or
a specific option as a beta by updating the documentation
and implementation.

The initial release note must label the new command or option
as a beta. No further release notes are required until the command
or option is no longer a beta. At which time, the beta label or
the command or option itself must be removed and a new release note
must be provided.

Beta Command Example
--------------------

Documentation
~~~~~~~~~~~~~

The command documentation must label the command as a beta.

example list
++++++++++++

List examples

.. caution:: This is a beta command and subject to change.
             Use global option ``--os-beta-command`` to
             enable this command.

.. program:: example list
.. code:: bash

    os example list

Help
~~~~

The command help must label the command as a beta.

.. code-block:: python

    class ShowExample(command.ShowOne):
        """Display example details

           (Caution: This is a beta command and subject to change.
            Use global option --os-beta-command to enable
            this command)
        """

Implementation
~~~~~~~~~~~~~~

The command must raise a ``CommandError`` exception if beta commands
are not enabled via ``--os-beta-command`` global option.

.. code-block:: python

    def take_action(self, parsed_args):
        self.validate_os_beta_command_enabled()

Beta Option Example
-------------------

Documentation
~~~~~~~~~~~~~

The option documentation must label the option as a beta.

.. option:: --example <example>

     Example

     .. caution:: This is a beta command option and subject
                  to change. Use global option ``--os-beta-command``
                  to enable this command option.

Implementation
~~~~~~~~~~~~~~

The option must not be added if beta commands are not
enabled via ``--os-beta-command`` global option.

.. code-block:: python

    def get_parser(self, prog_name):
        if self.app.options.os_beta_command:
            parser.add_argument(
                '--example',
                metavar='<example>',
                help=_("Example")
            )
