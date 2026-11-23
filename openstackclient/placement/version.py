# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import annotations

from collections.abc import Callable, Iterable
import functools
import operator
import re
from typing import (
    cast,
    Concatenate,
    ParamSpec,
    Protocol,
    TYPE_CHECKING,
    TypedDict,
    TypeVar,
    Unpack,
)

if TYPE_CHECKING:
    from openstackclient.placement import api
    from openstackclient import shell


_Predicate = Callable[[str], bool | str]


class _PredicateOptions(TypedDict, total=False):
    op: Callable[[Iterable[bool]], bool]


class _CompareOptions(_PredicateOptions, total=False):
    exc: bool


class _Command(Protocol):
    @property
    def app(self) -> shell.OpenStackShell: ...


_CommandT = TypeVar('_CommandT', bound=_Command)
_P = ParamSpec('_P')
_R = TypeVar('_R')


NEGOTIATE_VERSIONS = [
    '1',  # Added for auto choice for appropriate version
]
SUPPORTED_MICROVERSIONS = [
    '1.0',
    '1.1',
    '1.2',
    '1.3',
    '1.4',
    '1.5',
    '1.6',
    '1.7',
    '1.8',
    '1.9',
    '1.10',
    '1.11',
    '1.12',
    '1.13',  # unused
    '1.14',
    '1.15',  # unused
    '1.16',
    '1.17',
    '1.18',
    '1.19',
    '1.20',  # unused
    '1.21',
    '1.22',
    '1.23',  # unused
    '1.24',
    '1.25',
    '1.26',  # unused
    '1.27',  # unused
    '1.28',  # Added for provider allocation (un)set (Ussuri)
    '1.29',
    '1.37',  # unused
    '1.38',  # Added for consumer types (Xena)
    '1.39',  # Added any-traits support (Yoga)
]
SUPPORTED_VERSIONS = SUPPORTED_MICROVERSIONS + NEGOTIATE_VERSIONS
# The max microversion lower than which are all supported by this client.
# This is used to automatically pick up the microversion to use. Change this
# when you add a microversion to the `_SUPPORTED_VERSIONS` without a gap.
# TestVersion.test_max_version_consistency checks its consistency.
MAX_VERSION_NO_GAP = '1.29'


@functools.total_ordering
class _Version:
    _version_re = re.compile(r'^(\d) \. (\d+)$', re.VERBOSE | re.ASCII)

    def __init__(self, version: str) -> None:
        match = self._version_re.match(version)
        if not match:
            raise ValueError(f'invalid version number {version}')
        major, minor = match.group(1, 2)
        self.version = (int(major), int(minor))

    def __str__(self) -> str:
        return '.'.join(str(v) for v in self.version)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _Version):
            return NotImplemented
        return self.version == other.version

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, _Version):
            return NotImplemented
        return self.version < other.version


def _op(
    func: Callable[[_Version, _Version], bool], b: str, msg: str
) -> _Predicate:
    return lambda a: func(_Version(a), _Version(b)) or msg


def lt(b: str) -> _Predicate:
    msg = f'requires version less than {b}'
    return _op(operator.lt, b, msg)


def le(b: str) -> _Predicate:
    msg = f'requires at most version {b}'
    return _op(operator.le, b, msg)


def eq(b: str) -> _Predicate:
    msg = f'requires version {b}'
    return _op(operator.eq, b, msg)


def ne(b: str) -> _Predicate:
    msg = f'can not use version {b}'
    return _op(operator.ne, b, msg)


def ge(b: str) -> _Predicate:
    msg = f'requires at least version {b}'
    return _op(operator.ge, b, msg)


def gt(b: str) -> _Predicate:
    msg = f'requires version greater than {b}'
    return _op(operator.gt, b, msg)


def _compare(
    ver: str, *predicates: _Predicate, **kwargs: Unpack[_CompareOptions]
) -> bool | str:
    func = kwargs.get('op', all)
    if func(p(ver) is True for p in predicates):
        return True
    # construct an error message if the requirement not satisfied
    err_msg = f'Operation or argument is not supported with version {ver}; '
    err_detail = [p(ver) for p in predicates if p(ver) is not True]
    logic = ', and ' if func is all else ', or '
    return err_msg + logic.join(cast(list[str], err_detail))


def compare(
    ver: str, *predicates: _Predicate, **kwargs: Unpack[_CompareOptions]
) -> bool:
    """Validate version satisfies provided predicates.

    kwargs['exc'] - boolean whether exception should be raised
    kwargs['op'] - (all, any) how predicates should be checked

    Examples:
        compare('1.1', version.gt('1.2'), exc=False) - False
        compare('1.1', version.eq('1.0'), version.eq('1.1'), op=any) - True

    """
    exc = kwargs.get('exc', True)
    result = _compare(ver, *predicates, **kwargs)
    if result is not True:
        if exc:
            raise ValueError(result)
        return False
    return True


def check(
    *predicates: _Predicate, **check_kwargs: Unpack[_CompareOptions]
) -> Callable[
    [Callable[Concatenate[_CommandT, _P], _R]],
    Callable[Concatenate[_CommandT, _P], _R],
]:
    """Decorator for command object method.

    See `compare`

    """

    def wrapped(
        func: Callable[Concatenate[_CommandT, _P], _R],
    ) -> Callable[Concatenate[_CommandT, _P], _R]:
        def inner(self: _CommandT, *args: _P.args, **kwargs: _P.kwargs) -> _R:
            compare(get_version(self), *predicates, **check_kwargs)
            return func(self, *args, **kwargs)

        return cast(Callable[Concatenate[_CommandT, _P], _R], inner)

    return wrapped


def get_version(obj: _Command) -> str:
    """Extract version from a command object."""
    try:
        if obj.app.client_manager.session is None:
            return MAX_VERSION_NO_GAP
        version = cast(
            'api.SessionClient', obj.app.client_manager.placement
        ).api_version
    except AttributeError:
        # resource does not have api_version attr when docs are generated
        # so let's use the minimal one
        version = SUPPORTED_VERSIONS[0]
    return version


class CheckerMixin:
    app: shell.OpenStackShell

    def check_version(
        self, *predicates: _Predicate, **kwargs: Unpack[_CompareOptions]
    ) -> bool:
        return compare(get_version(self), *predicates, **kwargs)

    def compare_version(
        self, *predicates: _Predicate, **kwargs: Unpack[_PredicateOptions]
    ) -> bool:
        return compare(get_version(self), *predicates, exc=False, **kwargs)
