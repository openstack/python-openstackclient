.. _hig:

=====================
Human Interface Guide
=====================

*Note: This page covers the OpenStackClient CLI only but looks familiar
because it was derived from the Horizon HIG.*

Overview
========

What is a HIG?
The Human Interface Guidelines document was created for OpenStack developers
in order to direct the creation of new OpenStackClient command interfaces.

Personas
========

Personas are archetypal users of the system. Keep these types of users in
mind when designing the interface.

Alice the admin
---------------

Alice is an administrator who is responsible for maintaining the OpenStack
cloud installation. She has many years of experience with Linux systems
administration.

Darren the deployer
-------------------

Darren is responsible for doing the initial OpenStack deployment on the
host machines.

Emile the end-user
------------------

Emile uses the cloud to do software development inside of the virtual
machines. She uses the command-line tools because she finds it quicker
than using the dashboard.

Principles
==========

The principles established in this section define the high-level priorities
to be used when designing and evaluating interactions for the OpenStack
command line interface. Principles are broad in scope and can be considered
the philosophical foundation for the OpenStack experience; while they may
not describe the tactical implementation of design, they should be used
when deciding between multiple courses of design.

A significant theme for designing for the OpenStack experience concerns
focusing on common uses of the system rather than adding complexity to support
functionality that is rarely used.

Consistency
-----------

Consistency between OpenStack experiences will ensure that the command line
interface feels like a single experience instead of a jumble of disparate
products. Fractured experiences only serve to undermine user expectations
about how they should interact with the system, creating an unreliable user
experience. To avoid this, each interaction and visual representation within
the system must be used uniformly and predictably. The architecture and elements
detailed in this document will provide a strong foundation for establishing a
consistent experience.

Example Review Criteria
~~~~~~~~~~~~~~~~~~~~~~~

* Do the command actions adhere to a consistent application of actions?
* Has a new type of command subject or output been introduced?
* Does the design use command elements (options and arguments) as defined?
  (See Core Elements.)
* Can any newly proposed command elements (actions or subjects) be accomplished
  with existing elements?

* Does the design adhere to the structural model of the core experience?
  (See Core Architecture.)
* Are any data objects displayed or manipulated in a way contradictory to how
  they are handled elsewhere in the core experience?

Simplicity
----------

To best support new users and create straight forward interactions, designs
should be as simple as possible. When crafting new commands, designs should
minimize the amount of noise present in output: large amounts of
nonessential data, overabundance of possible actions and so on. Designs should
focus on the intent of the command, requiring only the necessary components
and either removing superfluous elements or making
them accessible through optional arguments. An example of this principle occurs
in OpenStack's use of tables: only the most often used columns are shown by
default. Further data may be accessed through the output control options,
allowing users to specify the types of data that they find useful in their
day-to-day work.

Example Review Criteria
~~~~~~~~~~~~~~~~~~~~~~~

* Can options be used to combine otherwise similar commands?

* How many of the displayed elements are relevant to the majority of users?
* If multiple actions are required for the user to complete a task, is each
  step required or can the process be more efficient?

User-Centered Design
--------------------

Commands should be design based on how a user will interact with the system
and not how the system's backend is organized. While database structures and
APIs may define what is possible, they often do not define good user
experience; consider user goals and the way in which users will want to
interact with their data, then design for these work flows and mold the
interface to the user, not the user to the interface.

Commands should be discoverable via the interface itself.

To determine a list of available commands, use the ``-h`` or
``--help`` options:

.. code-block:: bash

    $ openstack --help

For help with an individual command, use the ``help`` command:

.. code-block:: bash

    $ openstack help server create

Example Review Criteria
~~~~~~~~~~~~~~~~~~~~~~~

* How quickly can a user figure out how to accomplish a given task?
* Has content been grouped and ordered according to usage relationships?
* Do work flows support user goals or add complexity?

Transparency
------------

Make sure users understand the current state of their infrastructure and
interactions. For example, users should be able to access information about
the state of each machine/virtual machine easily, without having to actively
seek out this information. Whenever the user initiates an action, make sure
a confirmation is displayed[1] to show that an input has been received. Upon
completion of a process, make sure the user is informed. Ensure that the user
never questions the state of their environment.

[1] This goes against the common UNIX philosophy of only reporting error
conditions and output that is specifically requested.

Example Review Criteria
~~~~~~~~~~~~~~~~~~~~~~~

* Does the user receive feedback when initiating a process?
* When a process is completed?
* Does the user have quick access to the state of their infrastructure?


Architecture
============

Command Structure
-----------------

OpenStackClient has a consistent and predictable format for all of its commands.

* The top level command name is ``openstack``
* Sub-commands take the form:

.. code-block:: bash

    openstack [<global-options>] <object-1> <action> [<object-2>] [<command-arguments>]

Subcommands shall have three distinct parts to its commands (in order that they appear):

* global options
* command object(s) and action
* command options and arguments

Output formats:

* user-friendly tables with headers, etc
* machine-parsable delimited

.. note::

   A note on terminology. An **argument** is a positional parameter to the
   command. As discussed later, these should be used sparingly in
   OpenStackClient. An **option** - also known as a **flag** - is a named
   parameter denoted with either a hyphen and a single-letter name (``-r``) or
   a double hyphen and a multiple-letter name (``--recursive``). They may or
   may not also include a user-specified value (``--file foo.txt`` or
   ``--file=foo.txt``).

   For more information on this topic and CLIs in general, refer to the
   excellent `Command Line Interface Guidelines website`__.

   .. __: https://clig.dev/#arguments-and-flags

Global Options
~~~~~~~~~~~~~~

Global options are global in the sense that they apply to every command
invocation regardless of action to be performed.  They include authentication
credentials and API version selection.  Most global options have a corresponding
environment variable that may also be used to set the value.  If both are present,
the command-line option takes priority.  The environment variable names are derived
from the option name by dropping the leading dashes (``--``), converting each embedded
dash (``-``) to an underscore (``_``), and converting to upper case.

* Global options shall always have a long option name, certain common options may
  also have short names.  Short names should be reserved for global options to limit
  the potential for duplication and multiple meanings between commands given the
  limited set of available short names.

* All long options names shall begin with two dashes (``--``) and use a single dash
  (``-``) internally between words (``--like-this``).  Underscores (``_``) shall not
  be used in option names.

* Authentication options conform to the common CLI authentication guidelines in
  :ref:`authentication`.

For example, ``--os-username`` can be set from the environment via
``OS_USERNAME``.

``--help``
++++++++++

The standard ``--help`` global option displays the documentation for invoking
the program and a list of the available commands on standard output.  All other
options and commands are ignored when this is present.  The traditional short
form help option (``-h``) is also available.

``--version``
+++++++++++++

The standard ``--version`` option displays the name and version on standard
output.  All other options and commands are ignored when this is present.

Objects and Actions
~~~~~~~~~~~~~~~~~~~

Commands consist of an object, described by one or more words, followed by an
action. ::

    <object> <action>

For example:

* ``group create``
* ``server set``
* ``volume type list``

(note that ``volume type`` is a two-word single object)

Some commands require two objects. These commands have the primary object ahead of the
action and the secondary object after the action. In badly formed English it is
expressed as "(Take) object-1 (and perform) action (using) object-2 (to it)." ::

    <object-1> <action> <object-2>

For example:

* ``group add user``
* ``aggregate add host``
* ``image remove project``

Object names are always specified in command in their singular form.  This is
contrary to natural language use.

``help``
++++++++

The ``help`` command is unique as it appears in front of a normal command
and displays the help text for that command rather than execute it.

Arguments
~~~~~~~~~

Commands that interact with a specific instance of an object should accept a
single argument. This argument should be a name or identifier for the object.
::

    <object> <action> [<name-or-id>]

For example:

* ``group create <group>``
* ``server set <server>``

(note that ``volume type`` is a two-word single object)

For commands that require two objects, the commands should accept two
arguments when interacting with specific instances of the two objects. These
arguments should appear in the same order as the objects. ::

    <object-1> <action> <object-2> [<object-1-name-or-id> <object-2-name-or-id>]

For example:

* ``group add user <group> <user>``
* ``aggregate add host <aggregate> <host>``
* ``image remove project <image> <project>``

Options
~~~~~~~

Each command may have its own set of options distinct from the global options.
They follow the same style as the global options and always appear between
the command and any arguments the command requires.

Command options should only have long names. The small range of available short
names makes it hard for a single short option name to have a consistent meaning
across multiple commands.

Option Forms
++++++++++++

* **datetime**: Datetime options shall accept a value in `ISO-8061`__ format.
  For example, you can list servers last modified before a given date using
  ``--changes-before``. ::

      server list --changes-before 2020-01-01T12:30:00+00:00

* **list**: List options shall be passed via multiple options rather than as
  a single delimited option. For example, you can set multiple properties on a
  compute flavor using multiple ``--property`` options. ::

      flavor set --property quota:read_bytes_sec=10240000 \
          --property quota:write_bytes_sec=10240000 \
          <flavor>

* **boolean**: Boolean options shall use a form of ``--<true>|--<false>``
  (preferred) or ``--<option>|--no-<option>``. These must be mutually
  exclusive and should be adjective rather than verbs. For example, the
  ``enabled`` state of a project is set with ``--enable|--disable``. ::

      project set --enable <project>

.. __: https://en.wikipedia.org/wiki/ISO_8601

Command Output
--------------

The default command output is pretty-printed using the Python
``prettytable`` module.

Machine-parsable output format may be specified with the ``--format``
option to ``list`` and ``show`` commands.  ``list`` commands
have an option (``--format csv``) for CSV output and ``show`` commands
have an option (``--format shell``) for the shell variable assignment
syntax of ``var="value"``.  In both cases, all data fields are quoted with ``"``

Help Commands
-------------

The help system is considered separately due to its special status
among the commands.  Rather than performing tasks against a system, it
provides information about the commands available to perform those
tasks.  The format of the ``help`` command therefore varies from the
form for other commands in that the ``help`` command appears in front
of the first object in the command.

The options ``--help`` and ``-h`` display the global options and a
list of the supported commands.  Note that the commands shown depend on the API
versions that are in effect; i.e. if ``--os-identity-api-version=3`` is
present Identity API v3 commands are shown.


Common Actions
==============

There are a number of common actions or patterns in use across OpenStackClient.
When adding new commands, they should aim to match one of these action formats.

``create``
----------

``create`` will create a new instance of ``<object>``. Only a name should be
accepted as an argument. All other required and optional information
should be provided as options. If a name is not required, it can be marked as
optional. If it is not possible to specify a name when creating a new instance,
no arguments should be accepted. ::

    <object> create <name>

For example:

* ``flavor create <name>`` (compute flavors require a name)
* ``volume create [<name>] ...`` (block storage volumes don't *need* names)
* ``consumer create ...`` (identity consumers don't have names)
* ``container create --public <name>`` (additional information should be
  provided as options)

``show``
--------

``show`` will fetch a single instance of ``object``. Only a name or identifier
should be accepted as a argument. Any filters or additional information should
be provided as options. Where names are not unique or an instance is not found,
an error must be shown so the user can try again using a unique or valid ID,
respectively. ::

    <object> show <name-or-id>

For example:

* ``server show <name-or-id>`` (compute servers have names or IDs and can be
  referenced by both)
* ``consumer show <id>``  (identity consumers only have IDs, not names)
* ``server show --topology <name-or-id>`` (additional information should be
  provided as options)

``list``
--------

``list`` will list multiple instances of ``object``. No arguments should be
accepted. Any filters or pagination requests should be requested via option
arguments. ::

    <object> list

For example:

* ``image list`` (no arguments should be accepted)
* ``server list --status ACTIVE`` (filters should be provided as option
  arguments)

``delete``
----------

``delete`` will delete one or more instances of ``object``. Where possible,
this command should handle deleting instances of ``object`` by either name or
ID. Where names are not unique or an instance is not found, the command should
continue deleting any other instances requested before returning an error
indicating the instances that failed to delete. ::

    <object> delete <name-or-id> [<name-or-id> ...]

For example:

* ``network delete <name-or-id>``
* ``region delete <name-or-id>``

``set``, ``unset``
------------------

``set`` and ``unset`` will add or remove one or more attributes of an instance
of ``object``, respectively. Only a name or identifier should be accepted as a
argument. All other information should be provided as option
arguments. Where names are not unique or an instance is not found, an error
must be shown so the user can try again using a unique or valid ID,
respectively. This command may result in multiple API calls but it must not
result in the creation or modification of child object. ::

    <object> set <name-or-id>

For example:

* ``network set <name-or-id>``
* ``floating ip unset --port <port> <name-or-id>`` (additional information
  should be provided as options)

``add``, ``remove``
-------------------

``add`` and ``remove`` will associate or disassociate a child object with a
parent object. Only a name or identifier for both parent and child objects
should be accepted as arguments. All other information should be provided as
options. Where names are not unique or an instance is not found, an error must
be shown so the user can try again using a unique or valid ID, respectively. ::

    <parent-object> add <child-object> <parent-name-or-id> <child-name-or-id>
    <parent-object> remove <child-object> <parent-name-or-id> <child-name-or-id>

For example:

* ``aggregate add host <aggregate-name-or-id> <host>``
* ``consistency group add volume <consistency-group-name-or-id> <volume-name-or-id>``

Other actions
-------------

There are other actions that do not fit neatly into any of the above actions.
Typically, these are used where an action would create a child object but that
child object is only exposed as part of the parent object. They are also used
where fitting the action into one of the above actions, particularly ``set``,
would be deemed to be confusing or otherwise inappropriate. These are permitted
once this has been discussed among reviewers and context provided in either the
commit message or via comments in the code.

For example:

* ``server ssh`` (this would not naturally fit into any of the other actions)
* ``server migrate`` (this results in the creation of a server migration record
  and could be implemented as ``server migration create`` but this feels
  unnatural)
* ``server migration confirm`` (this could be implemented as ``server migration
  set --confirm`` but this feels unnatural)
* ``volume backup record export`` (this could be implemented as ``volume backup
  record show --exportable`` but this feels unnatural)

.. note::

    The guidelines below are best practices but exceptions do exist in
    OpenStackClient and in various plugins. Where possible, these exceptions
    should be addressed over time.


API versioning
==============

OpenStackClient will strive to behave sensibly for services that version their
API. The API versioning schemes in use vary between services and have evolved
since the early days of OpenStack. There are two types of API versioning to
consider: the major version and the minor version. Today, most OpenStack
services have settled on a single major API version and have chosen to evolve
the API without bumping the major API version any further. There are three API
"minor" versioning schemes in common use.

.. rubric:: Per-release versions

This is used by the Image service (glance). All changes to the API during a
given release cycle are gathered into a single new API version. As such, the
API version will increase at most once per release. You can continue to request
older versions.

Example:

.. list-table:: Image (glance) API versions per release

   * - Release
     - Supported 2.x API versions

   * - Grizzly
     - 2.0 - 2.1

   * - Havana
     - 2.0 - 2.2

   * - Kilo
     - 2.0 - 2.3

   * - ...
     - ...

.. rubric:: Microversions

This is used by multiple services including the Compute service (nova), Block
Storage service (cinder), and Shared Filesystem service (manila). Each change
to the API will result in a new API version. As such, the API version can
increase multiple times per release. You can continue to request older
versions.

Example:

.. list-table:: Compute (nova) API versions per release

   * - Release
     - Supported 2.x API versions

   * - Kilo
     - 2.1 - 2.3

   * - Liberty
     - 2.1 - 2.12

   * - Mitaka
     - 2.1 - 2.25

   * - ...
     - ...

.. rubric:: Extensions

This is used by the Networking service (neutron). It's a versioning scheme that
doesn't use API versions. Instead, it exposes a list of available extensions.
An extension can add, remove or modify features and vendor-specific
functionality to the API. This can include API resources/routes as well as new
fields in API requests and responses. If you want to depend on a feature added
by an extension, you should check if the extension is present.

Major API version support
-------------------------

Major API version support has become less important over time as the various
OpenStack services have chosen to focus on the "minor" versioning mechanisms
described above. However, OpenStackClient aims to support **all** OpenStack
clouds, not just those running the most recent OpenStack release. This means it
must aim to support older major API versions that have since been removed from
the services in question. For example, the Volume service's (cinder) v2 API was
deprecated in cinder 11.0.0 (Pike) and was removed in cinder 19.0.0 (Xena),
however, OpenStackClient continues to support this API since not all OpenStack
deployments have updated or will update to Xena or later. This should remain
the case for as long as this support is technically feasible.

.. note::

    While OpenStackClient will continue to support existing command
    implementations for older APIs, there is no requirement to add **new**
    commands that implement support for deprecated or removed APIs.

OpenStackClient provides different command implementations depending on the API
version used. On startup, OpenStackClient will attempt to identify the API
version using the service catalog. Where a service provides multiple API major
versions, OpenStackClient defaults to the latest one. This can be configured by
the user using options (``--os-{service}-api-version``), environment variables
(``OS_{service}_API_VERSION``) or configuration in the ``clouds.yaml`` file.

Minor API version and extension support
---------------------------------------

As most services implement some form of versioning and use this to both add new
functionality and to modify or remove existing functionality, it is imperative
that OpenStackClient provides a mechanism to configure the API version used.
Unlike major API versions, support for API microversions or API extensions is
implemented via logic in the command itself. OpenStackClient commands should
indicate the minimum or maximum API microversion or the API extension required
for given actions and options in the help string for same. Where a user
attempts to use a feature that requires a particular microversion or extension
that the service does not support, OpenStackClient should fail with an error
message describing these requirements. Like API versions, the requested can be
configured by the user using options (``--os-{service}-api-version``),
environment variables (``OS_{service}_API_VERSION``) or configuration in
``clouds.yaml`` file.

.. important::

   Historically, OpenStackClient has defaulted to the lowest supported
   microversion for each service. This was not by design but rather a side
   effect of relying on legacy clients who implement this behavior.
   openstacksdk does not implement this behavior and instead auto-negotiates a
   version based on the versions that SDK knows about. For now, this means we
   have some commands that require explicit microversion configuration to get
   the latest and greatest behavior, while others will handle this
   transparently. For humans, this should not matter. For scripts, which are
   more fragile, it is recommended that an explicit microversion is always
   requested.


Examples
========

The following examples depict common command and output formats expected to be
produces by the OpenStackClient.

Authentication
--------------

Using global options:

.. code-block:: bash

    $ openstack --os-tenant-name ExampleCo --os-username demo --os-password secret --os-auth-url http://localhost:5000:/v2.0 server show appweb01
    +------------------------+-----------------------------------------------------+
    |        Property        |                Value                                |
    +------------------------+-----------------------------------------------------+
    | OS-DCF:diskConfig      | MANUAL                                              |
    | OS-EXT-STS:power_state | 1                                                   |
    | flavor                 | m1.small                                            |
    | id                     | dcbc2185-ba17-4f81-95a9-c3fae9b2b042                |
    | image                  | Ubuntu 12.04 (754c231e-ade2-458c-9f91-c8df107ff7ef) |
    | keyname                | demo-key                                            |
    | name                   | appweb01                                            |
    | private_address        | 10.4.128.13                                         |
    | status                 | ACTIVE                                              |
    | user                   | demo                                                |
    +------------------------+-----------------------------------------------------+

Using environment variables:

.. code-block:: bash

    $ export OS_TENANT_NAME=ExampleCo
    $ export OS_USERNAME=demo
    $ export OS_PASSWORD=secret
    $ export OS_AUTH_URL=http://localhost:5000:/v2.0
    $ openstack server show appweb01
    +------------------------+-----------------------------------------------------+
    |        Property        |                Value                                |
    +------------------------+-----------------------------------------------------+
    | OS-DCF:diskConfig      | MANUAL                                              |
    | OS-EXT-STS:power_state | 1                                                   |
    | flavor                 | m1.small                                            |
    | id                     | dcbc2185-ba17-4f81-95a9-c3fae9b2b042                |
    | image                  | Ubuntu 12.04 (754c231e-ade2-458c-9f91-c8df107ff7ef) |
    | keyname                | demo-key                                            |
    | name                   | appweb01                                            |
    | private_address        | 10.4.128.13                                         |
    | status                 | ACTIVE                                              |
    | user                   | demo                                                |
    +------------------------+-----------------------------------------------------+

Machine Output Format
---------------------

Using the CSV output format with a list command:

.. code-block:: bash

    $ openstack server list --format csv
    "ID","Name","Status","Private_Address"
    "ead97d84-6988-47fc-9637-3564fc36bc4b","appweb01","ACTIVE","10.4.128.13"

Using the show command options of  shell output format and adding a prefix of
``my_`` to avoid collisions with existing environment variables:

.. code-block:: bash

    $ openstack server show --format shell --prefix my_ appweb01
    my_OS-DCF:diskConfig="MANUAL"
    my_OS-EXT-STS:power_state="1"
    my_flavor="m1.small"
    my_id="dcbc2185-ba17-4f81-95a9-c3fae9b2b042"
    my_image="Ubuntu 12.04 (754c231e-ade2-458c-9f91-c8df107ff7ef)"
    my_keyname="demo-key"
    my_name="appweb01"
    my_private_address="10.4.128.13"
    my_status="ACTIVE"
    my_user="demo"
