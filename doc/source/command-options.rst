===============
Command Options
===============

OpenStackClient commands all have a set of zero or more options unique to
the command, however there are of course ways in which these options are
common and consistent across all of the commands that include them.

These are the set of guidelines for OSC developers that help keep the
interface and commands consistent.

In some cases (like the boolean variables below) we use the same pattern
for defining and using options in all situations.  The alternative of only
using it when necessary leads to errors when copy-n-paste is used for a
new command without understanding why or why not that instance is correct.

General Command Options
=======================

Boolean Options
---------------

Boolean options for any command that sets a resource state, such as 'enabled'
or 'public', shall always have both positive and negative options defined.
The names of those options shall either be a naturally occurring pair of
words (in English) or a positive option and a negative option with `no-`
prepended (such as in the traditional GNU option usage) like `--share` and
`--no-share`.

In order to handle those APIs that behave differently when a field is set to
`None` and when the field is not present in a passed argument list or dict,
each of the boolean options shall set its own variable to `True` as part of
a mutiually exclusive group, rather than the more common configuration of
setting a single destination variable `True` or `False` directly.  This allows
us to detect the situation when neither option is present (both variables will
be `False`) and act accordingly for those APIs where this matters.

This also requires that each of the boolean values be tested in the
`take_action()` method to correctly set (or not) the underlying API field
values.

.. option:: --enable

    Enable <resource> (default)

.. option:: --disable

    Disable <resource>

Implementation
~~~~~~~~~~~~~~

The parser declaration should look like this:

.. code-block:: python

        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help=_('Enable <resource> (default)'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help=_('Disable <resource>'),
        )

An example handler in `take_action()`:

.. code-block:: python

        # This leaves 'enabled' undefined if neither option is present
        if parsed_args.enable:
            kwargs['enabled'] = True
        if parsed_args.disable:
            kwargs['enabled'] = False

Options with Choices
--------------------

Some options have a specific set of values (or choices) that are valid.
These choices may be validated by the CLI. If the underlying API is stable
and the list of choices are unlikely to change then the CLI may validate
the choices. Otherwise, the CLI must defer validation of the choices to
the API. If the option has a default choice then it must be documented.

Having the CLI validate choices will be faster and may provide a better
error message for the user if an invalid choice is specified
(for example: ``argument --test: invalid choice: 'choice4' (choose from 'choice1', 'choice2', 'choice3')``).
The trade-off is that CLI changes are required in order to take advantage
of new choices.

Implementation
~~~~~~~~~~~~~~

An example parser declaration:

.. code-block:: python

        choice_option.add_argument(
            '--test',
            metavar='<test>,
            choices=['choice1', 'choice2', 'choice3'],
            help=_('Test type (choice1, choice2 or choice3)'),
        )

List Command Options
====================

Additional Fields
-----------------

Most list commands only return a subset of the available fields by default.
Additional fields are available with the `--long` option.  All list
commands should allow `--long` even if they return all fields by default.

.. option:: --long

    List additional fields in output

Implementation
~~~~~~~~~~~~~~

The parser declaration should look like this:

.. code-block:: python

        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )

Pagination
----------

There are many ways to do pagination, some OpenStack APIs support it, some
don't. OpenStackClient attempts to define a single common way to specify
pagination on the command line.

.. option:: --marker <marker>

    Anchor for paging

.. option:: --limit <limit>

    Limit number of <resource> returned (*integer*)

Implementation
~~~~~~~~~~~~~~

The parser declaration should look like this:

.. code-block:: python

        parser.add_argument(
            "--marker",
            metavar="<marker>",
            help="Anchor for paging",
        )

        parser.add_argument(
            "--limit",
            metavar="<limit>",
            type=int,
            help="Limit the number of <resource> returned",
        )
