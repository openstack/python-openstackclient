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

To determine a list of available commands, use the :code:`-h` or
:code:`--help` options:

.. code-block:: bash

    $ openstack --help

For help with an individual command, use the :code:`help` command:

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

* The top level command name is :code:`openstack`
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

Global Options
~~~~~~~~~~~~~~

Global options are global in the sense that they apply to every command
invocation regardless of action to be performed.  They include authentication
credentials and API version selection.  Most global options have a corresponding
environment variable that may also be used to set the value.  If both are present,
the command-line option takes priority.  The environment variable names are derived
from the option name by dropping the leading dashes ('--'), converting each embedded
dash ('-') to an underscore ('_'), and converting to upper case.

* Global options shall always have a long option name, certain common options may
  also have short names.  Short names should be reserved for global options to limit
  the potential for duplication and multiple meanings between commands given the
  limited set of available short names.
* All long options names shall begin with two dashes ('--') and use a single dash
  ('-') internally between words (:code:`--like-this`).  Underscores ('_') shall not
  be used in option names.
* Authentication options conform to the common CLI authentication guidelines in
  :doc:`authentication`.

For example, :code:`--os-username` can be set from the environment via
:code:`OS_USERNAME`.

--help
++++++

The standard :code:`--help` global option displays the documentation for invoking
the program and a list of the available commands on standard output.  All other
options and commands are ignored when this is present.  The traditional short
form help option (:code:`-h`) is also available.

--version
+++++++++

The standard :code:`--version` option displays the name and version on standard
output.  All other options and commands are ignored when this is present.

Command Object(s) and Action
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Commands consist of an object described by one or more words followed by an action.  Commands that require two objects have the primary object ahead of the action and the secondary object after the action. Any positional arguments identifying the objects shall appear in the same order as the objects.  In badly formed English it is expressed as "(Take) object1 (and perform) action (using) object2 (to it)."

    <object-1> <action> [<object-2>]

Examples:

* :code:`group add user <group> <user>`
* :code:`volume type list`   # Note that :code:`volume type` is a two-word
  single object

The :code:`help` command is unique as it appears in front of a normal command
and displays the help text for that command rather than execute it.

Object names are always specified in command in their singular form.  This is
contrary to natural language use.

Command Arguments and Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each command may have its own set of options distinct from the global options.
They follow the same style as the global options and always appear between
the command and any positional arguments the command requires.

Command options shall only have long names.  The small range of available
short names makes it hard for a single short option name to have a consistent
meaning across multiple commands.

Option Forms
++++++++++++

* **boolean**: boolean options shall use a form of :code:`--<true>|--<false>`
  (preferred) or :code:`--<option>|--no-<option>`.  For example, the
  :code:`enabled` state of a project is set with :code:`--enable|--disable`.

Command Output
--------------

The default command output is pretty-printed using the Python
:code:`prettytable` module.

Machine-parsable output format may be specified with the :code:`--format`
option to :code:`list` and :code:`show` commands.  :code:`list` commands
have an option (:code:`--format csv`) for CSV output and :code:`show` commands
have an option (:code:`--format shell`) for the shell variable assignment
syntax of :code:`var="value"`.  In both cases, all data fields are quoted with `"`

Help Commands
-------------

The help system is considered separately due to its special status
among the commands.  Rather than performing tasks against a system, it
provides information about the commands available to perform those
tasks.  The format of the :code:`help` command therefore varies from the
form for other commands in that the :code:`help` command appears in front
of the first object in the command.

The options :code:`--help` and :code:`-h` display the global options and a
list of the supported commands.  Note that the commands shown depend on the API
versions that are in effect; i.e. if :code:`--os-identity-api-version=3` is
present Identity API v3 commands are shown.

Examples
========

The following examples depict common command and output formats expected to be produces by the OpenStack client.

Authentication
--------------

Using global options:

.. code-block:: bash

    $ openstack --os-tenant-name ExampleCo --os-username demo --os-password secrete --os-auth-url http://localhost:5000:/v2.0 server show appweb01
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
    $ export OS_PASSWORD=secrete
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

Using the csv output format with a list command:

.. code-block:: bash

    $ openstack server list --format csv
    "ID","Name","Status","Private_Address"
    "ead97d84-6988-47fc-9637-3564fc36bc4b","appweb01","ACTIVE","10.4.128.13"

Using the show command options of  shell output format and adding a prefix of
:code:`my_` to avoid collisions with existing environment variables:

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
