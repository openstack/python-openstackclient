==============
Command Errors
==============

Handling errors in OpenStackClient commands is fairly straightforward.  An
exception is thrown and handled by the application-level caller.

Note: There are many cases that need to be filled out here.  The initial
version of this document considers the general command error handling as well
as the specific case of commands that make multiple REST API calls and how to
handle when one or more of those calls fails.

General Command Errors
======================

The general pattern for handling OpenStackClient command-level errors is to
raise a CommandError exception with an appropriate message.  This should include
conditions arising from arguments that are not valid/allowed (that are not otherwise
enforced by ``argparse``) as well as errors arising from external conditions.

External Errors
---------------

External errors are a result of things outside OpenStackClient not being as
expected.

Example
~~~~~~~

This example is taken from ``keypair create`` where the ``--public-key`` option
specifies a file containing the public key to upload.  If the file is not found,
the IOError exception is trapped and a more specific CommandError exception is
raised that includes the name of the file that was attempted to be opened.

.. code-block:: python

    class CreateKeypair(command.ShowOne):
        """Create new public key"""

        ## ...

        def take_action(self, parsed_args):
            compute_client = self.app.client_manager.compute

            public_key = parsed_args.public_key
            if public_key:
                try:
                    with io.open(
                        os.path.expanduser(parsed_args.public_key),
                        "rb"
                    ) as p:
                        public_key = p.read()
                except IOError as e:
                    msg = _("Key file %s not found: %s")
                    raise exceptions.CommandError(
                        msg % (parsed_args.public_key, e),
                    )

            keypair = compute_client.keypairs.create(
                parsed_args.name,
                public_key=public_key,
            )

            ## ...

REST API Errors
===============

Most commands make a single REST API call via the supporting client library
or SDK.  Errors based on HTML return codes are usually handled well by default,
but in some cases more specific or user-friendly messages need to be logged.
Trapping the exception and raising a CommandError exception with a useful
message is the correct approach.

Multiple REST API Calls
-----------------------

Some CLI commands make multiple calls to library APIs and thus REST APIs.
Most of the time these are ``create`` or ``set`` commands that expect to add or
change a resource on the server.  When one of these calls fails, the behaviour
of the remainder of the command handler is defined as such:

* Whenever possible, all API calls will be made.  This may not be possible for
  specific commands where the subsequent calls are dependent on the results of
  an earlier call.

* Any failure of an API call will be logged for the user

* A failure of any API call results in a non-zero exit code

* In the cases of failures in a ``create`` command a follow-up mode needs to
  be present that allows the user to attempt to complete the call, or cleanly
  remove the partially-created resource and re-try.

The desired behaviour is for commands to appear to the user as idempotent
whenever possible, i.e. a partial failure in a ``set`` command can be safely
retried without harm.  ``create`` commands are a harder problem and may need
to be handled by having the proper options in a set command available to allow
recovery in the case where the primary resource has been created but the
subsequent calls did not complete.

Example 1
~~~~~~~~~

This example is taken from the ``volume snapshot set`` command where ``--property``
arguments are set using the volume manager's ``set_metadata()`` method,
``--state`` arguments are set using the ``reset_state()`` method, and the
remaining arguments are set using the ``update()`` method.

.. code-block:: python

    class SetSnapshot(command.Command):
    """Set snapshot properties"""

    ## ...

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        snapshot = utils.find_resource(
            volume_client.volume_snapshots,
            parsed_args.snapshot,
        )

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        result = 0
        if parsed_args.property:
            try:
                volume_client.volume_snapshots.set_metadata(
                    snapshot.id,
                    parsed_args.property,
                )
            except SomeException:      # Need to define the exceptions to catch here
                LOG.error(_("Property set failed"))
                result += 1

        if parsed_args.state:
            try:
                volume_client.volume_snapshots.reset_state(
                    snapshot.id,
                    parsed_args.state,
                )
            except SomeException:      # Need to define the exceptions to catch here
                LOG.error(_("State set failed"))
                result += 1

        try:
            volume_client.volume_snapshots.update(
                snapshot.id,
                **kwargs
            )
        except SomeException:      # Need to define the exceptions to catch here
            LOG.error(_("Update failed"))
            result += 1

        # NOTE(dtroyer): We need to signal the error, and a non-zero return code,
        #                without aborting prematurely
        if result > 0:
            raise SomeNonFatalException

Example 2
~~~~~~~~~

This example is taken from the ``network delete`` command which takes multiple
networks to delete. All networks will be deleted in a loop, which makes
multiple ``delete_network()`` calls.

.. code-block:: python

    class DeleteNetwork(common.NetworkAndComputeCommand):
        """Delete network(s)"""

        def update_parser_common(self, parser):
            parser.add_argument(
                'network',
                metavar="<network>",
                nargs="+",
                help=_("Network(s) to delete (name or ID)")
            )
            return parser

        def take_action(self, client, parsed_args):
            ret = 0

            for network in parsed_args.network:
                try:
                    obj = client.find_network(network, ignore_missing=False)
                    client.delete_network(obj)
                except Exception:
                    LOG.error(_("Failed to delete network with name "
                                "or ID %s."), network)
                    ret += 1

            if ret > 0:
                total = len(parsed_args.network)
                msg = (_("Failed to delete %(ret)s of %(total)s networks.")
                       % {"ret": ret, "total": total})
                raise exceptions.CommandError(msg)
