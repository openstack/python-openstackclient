============
Command Logs
============

Logger usage in OpenStackClient is not exactly the same as those in other
OpenStack projects. The following basic rules should be followed.

1. OpenStackClient uses python standard logging library instead of oslo.log
   so that it will depend on oslo as little as possible.

2. All logs except debug log need to be translated. The log message strings
   that need to be translated should follow the rule of i18n guidelines:
   http://docs.openstack.org/developer/oslo.i18n/guidelines.html

3. There are mainly two kinds of logs in OpenStackClient: command specific
   log and general log. Use different logger to record them. The examples
   below will show the detail.

Command specific log
====================

Command specific logs are those messages that used to record info, warning
and error generated from a specific command. OpenStackClient uses the logger
of the module the command belongs to to record the command specific logs.

Example
~~~~~~~

This example shows how to log command specific logs in OpenStackClient.

.. code-block:: python

    import logging

    from openstackclient.i18n import _


    LOG = logging.getLogger(__name__)     # Get the logger of this module

    ## ...

        LOG.error(_("Error message"))
        LOG.warning(_("Warning message"))
        LOG.info(_("Info message"))
        LOG.debug("Debug message")        # Debug messages do not need to be translated

    ## ...

General log
===========

General logs are those messages that not specific to any single command. Use
the logger of ``openstackclient.shell`` to record them. In each command class,
we can simply get this logger by ``self.app.log``.

Example
~~~~~~~

This example shows how to log general logs in OpenStackClient.

.. code-block:: python

    from openstackclient.i18n import _


    ## ...

        self.app.log.error(_("Error message"))
        self.app.log.warning(_("Warning message"))
        self.app.log.info(_("Info message"))
        self.app.log.debug("Debug message")        # Debug messages do not need to be translated

    ## ...
