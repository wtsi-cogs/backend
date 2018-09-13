"""
Copyright (c) 2017, 2018 Genome Research Ltd.

Authors:
* Christopher Harrison <ch12@sanger.ac.uk>

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

from aiohttp.web import Response

from cogs.auth.exceptions import AuthenticationError, NotLoggedInError, SessionTimeoutError


class InvalidPagesmithUserCookie(AuthenticationError):
    """ Raised if the Pagesmith user cookie can't be decoded """


class NoPagesmithUserCookie(NotLoggedInError):
    """ Raised on the absence of a Pagesmith user cookie """


class PagesmithSessionTimeoutError(SessionTimeoutError):
    """ Raise when the Pagesmith user cookie has expired """
    def clear_session(self, response:Response) -> Response:
        response.del_cookie("Pagesmith_User")
        return response
