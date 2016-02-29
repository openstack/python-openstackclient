======================
Command Class Wrappers
======================

When we want to deprecate a command, policy says we need to alert the user.
We do this with a message logged at WARNING level before any command output
is emitted.

OpenStackClient command classes are derived from the ``cliff`` classes.
Cliff uses ``setuptools`` entry points for dispatching the parsed command
to the respective handler classes.  This lends itself to modifying the
command execution at run-time.

The obvious approach to adding the deprecation message would be to just add
the message to the command class ``take_action()`` method directly.  But then
the various deprecations are scattered throughout the code base.  If we
instead wrap the deprecated command class with a new class we can put all of
the wrappers into a separate, dedicated module.  This also lets us leave the
original class unmodified and puts all of the deprecation bits in one place.

This is an example of a minimal wrapper around a command class that logs a
deprecation message as a warning to the user then calls the original class.

* Subclass the deprecated command.

* Set class attribute ``deprecated`` to ``True`` to signal cliff to not
  emit help text for this command.

* Log the deprecation message at WARNING level and refer to the replacement
  for the deprecated command in the log warning message.

* Change the entry point class in ``setup.cfg`` to point to the new class.

Example Deprecation Class
-------------------------

.. code-block:: python

    class ListFooOld(ListFoo):
        """List resources"""

        # This notifies cliff to not display the help for this command
        deprecated = True

        log = logging.getLogger('deprecated')

        def take_action(self, parsed_args):
            self.log.warning(
                "%s is deprecated, use 'foobar list'",
                getattr(self, 'cmd_name', 'this command'),
            )
            return super(ListFooOld, self).take_action(parsed_args)
