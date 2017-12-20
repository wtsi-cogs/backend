"""
Copyright (c) 2017 Genome Research Ltd.

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

import os.path
from glob import glob
from typing import List

from cogs.common import logging
from cogs.db.models import Project


class FileHandler(logging.LogWriter):
    """ Project file handling interface """
    _upload_dir:str
    _max_filesize:int

    def __init__(self, upload_directory:str, max_filesize:int) -> None:
        """
        Constructor

        :param upload_directory:
        :param max_filesize:
        :return:
        """
        self._upload_dir = os.path.normpath(os.path.expanduser(upload_directory))
        self._max_filesize = max_filesize

    def get_files_by_project(self, project:Project) -> List[str]:
        """
        Return a list of absolute paths of files associated with a
        project

        FIXME This is just a quick-and-dirty implementation

        :param project:
        :return:
        """
        user_path = os.path.join(self._upload_dir, str(project.student_id))
        pattern = os.path.join(user_path, f"{project.group.series}_{project.group.part}*")
        return glob(pattern)

    def upload_file(self, user, project, extension):
        # Get the path to upload files
        user_path = os.path.join(self._upload_dir, str(user.id))
        if not os.path.isdir(user_path):
            os.makedirs(user_path)

        group = project.group

        # Special case part 2 because they want poster and document
        max_files_for_project = 1 if group.part != 2 else 2

        # Get the filename with path we'll be saving to
        filename = f"{user_path}/{group.series}_{group.part}"
        existing_files = glob(filename+"*")
        if len(existing_files) >= max_files_for_project:
            for path in existing_files:
                os.remove(path)
            existing_files = []

        return open(f"{filename}_{len(existing_files)+1}.{extension}", mode="wb"), \
               len(existing_files) + 1 == max_files_for_project
