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

The :doc:`Human Interface Guide <humaninterfaceguide>`
describes the guildelines for option names and usage.  In short:
  * All option names shall be GNU-style long names (two leading dashes).
  * Some global options may have short names, generally limited to those defined
    in support libraries such as ``cliff``.

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
a mutually exclusive group, rather than the more common configuration of
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
            metavar='<test>',
            choices=['choice1', 'choice2', 'choice3'],
            help=_('Test type (choice1, choice2 or choice3)'),
        )

Options with Multiple Values
----------------------------

Some options can be repeated to build a collection of values for a property.
Adding a value to the collection must be provided via the ``set`` action.
Removing a value from the collection must be provided via an ``unset`` action.
As a convenience, removing all values from the collection may be provided via a
``--no`` option on the ``set`` and ``unset`` actions. If both ``--no`` option
and option are specified, the values specified on the command would overwrite
the collection property instead of appending on the ``set`` action. The
``--no`` option must be part of a mutually exclusive group with the related
property option on the ``unset`` action, overwrite case don't exist in
``unset`` action.

An example behavior for ``set`` action:

Append:

.. code-block:: bash

    object set --example-property xxx

Overwrite:

.. code-block:: bash

    object set --no-example-property --example-property xxx

The example below assumes a property that contains a list of unique values.
However, this example can also be applied to other collections using the
appropriate parser action and action implementation (e.g. a dict of key/value
pairs). Implementations will vary depending on how the REST API handles
adding/removing values to/from the collection and whether or not duplicate
values are allowed.

Implementation
~~~~~~~~~~~~~~

An example parser declaration for `set` action:

.. code-block:: python

        parser.add_argument(
            '--example-property',
            metavar='<example-property>',
            dest='example_property',
            action='append',
            help=_('Example property for this <resource> '
                   '(repeat option to set multiple properties)'),
        )
        parser.add_argument(
            '--no-example-property',
            dest='no_example_property',
            action='store_true',
            help=_('Remove all example properties for this <resource>'),
        )

An example handler in `take_action()` for `set` action:

.. code-block:: python

        if parsed_args.example_property and parsed_args.no_example_property:
            kwargs['example_property'] = parsed_args.example_property
        elif parsed_args.example_property:
            kwargs['example_property'] = \
                resource_example_property + parsed_args.example_property
        elif parsed_args.no_example_property:
            kwargs['example_property'] = []

An example parser declaration for `unset` action:

.. code-block:: python

        example_property_group = parser.add_mutually_exclusive_group()
        example_property_group.add_argument(
            '--example-property',
            metavar='<example-property>',
            dest='example_property',
            action='append',
            help=_('Example property for this <resource> '
                   '(repeat option to remove multiple properties)'),
        )
        example_property_group.add_argument(
            '--no-example-property',
            dest='no_example_property',
            action='store_true',
            help=_('Remove all example properties for this <resource>'),
        )

An example handler in `take_action()` for `unset` action:

.. code-block:: python

        if parsed_args.example_property:
            kwargs['example_property'] = \
                list(set(resource_example_property) - \
                     set(parsed_args.example_property))
        if parsed_args.no_example_property:
            kwargs['example_property'] = []

Required Options
----------------

Some options have no default value and the API does not allow them to be
`None`, then these options are always required when users use the command
to which these options belong.

Required options must be validated by the CLI to avoid omissions. The CLI
validation may provide an error message for the user if a required option
is not specified.
(for example: ``error: argument --test is required``)

.. option:: --test

    Test option (required)

Implementation
~~~~~~~~~~~~~~

The parser declaration should look like this:

.. code-block:: python

        parser.add_argument(
            '--test',
            metavar='<test>',
            required=True,
            help=_('Test option (required)'),
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
