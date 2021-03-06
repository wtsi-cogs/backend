"""
Copyright (c) 2017 Genome Research Ltd.

Authors:
* Christopher Harrison <ch12@sanger.ac.uk>
* Simon Beal <sb48@sanger.ac.uk>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from functools import wraps
from typing import Any, Callable

from aiohttp.web import HTTPForbidden, Request, StreamResponse

from cogs.common.constants import PERMISSIONS
from cogs.common.types import Handler
from .roles import zero


def permit(*permissions: str) -> Callable[[Handler], Handler]:
    """
    Factory that returns a decorator that forbids access to route
    handlers if the authenticated user is missing any of the specified
    permissions (that is, all the passed permissions are required)

    NOTE While it works in a similar way, this should be used as a
    decorator, rather than web application middleware
    """
    # We must have at least one permission and our given permissions
    # must be a subset of the valid permissions
    assert permissions
    assert set(permissions) <= set(PERMISSIONS)

    def decorator(fn: Handler) -> Handler:
        @wraps(fn)
        async def decorated(request: Request) -> StreamResponse:
            """
            Check authenticated user has the necessary permissions
            """
            user = request.get("user")
            role = user.role if user else zero

            if not all(getattr(role, p) for p in permissions):
                raise HTTPForbidden(text="Permission denied")

            return await fn(request)

        return decorated

    return decorator


def permit_any(*permissions: str) -> Callable[[Handler], Handler]:
    """
    Factory that returns a decorator that forbids access to route
    handlers if the authenticated user is missing all of the specified
    permissions (that is, any of the passed permissions are sufficient)

    NOTE While it works in a similar way, this should be used as a
    decorator, rather than web application middleware
    """
    # We must have at least one permission and our given permissions
    # must be a subset of the valid permissions
    assert permissions
    assert set(permissions) <= set(PERMISSIONS)

    def decorator(fn: Handler) -> Handler:
        @wraps(fn)
        async def decorated(request: Request) -> StreamResponse:
            """
            Check authenticated user has the necessary permissions
            """
            user = request.get("user")
            role = user.role if user else zero

            if not any(getattr(role, p) for p in permissions):
                raise HTTPForbidden(text="Permission denied")

            return await fn(request)

        return decorated

    return decorator
