OpenStack Style Commandments
============================

- Step 1: Read the OpenStack Style Commandments
  https://docs.openstack.org/hacking/latest/
- Step 2: Read on

General
-------

- thou shalt not violate causality in our time cone, or else

Docstrings
----------

Docstrings should ONLY use triple-double-quotes (``"""``)

Single-line docstrings should NEVER have extraneous whitespace
between enclosing triple-double-quotes.

Deviation! Sentence fragments do not have punctuation.  Specifically in the
command classes the one line docstring is also the help string for that
command and those do not have periods.

  """A one line docstring looks like this"""

Calling Methods
---------------

Deviation! When breaking up method calls due to the 79 char line length limit,
use the alternate 4 space indent.  With the first argument on the succeeding
line all arguments will then be vertically aligned.  Use the same convention
used with other data structure literals and terminate the method call with
the last argument line ending with a comma and the closing paren on its own
line indented to the starting line level.  ::

    unnecessarily_long_function_name(
        'string one',
        'string two',
        kwarg1=constants.ACTIVE,
        kwarg2=['a', 'b', 'c'],
    )
