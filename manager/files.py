"""
This module contains the database manager class for the file operations.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from .base_class import DBManagerBase
from .exceptions import (
    InvalidParameter
)
from ..models import (
    User, File
)


class DBManagerFiles(DBManagerBase):
    """
    This class implements the database manager class for the file operations
    """
    def insert_file(self, user: User, name: str, full_path: str = None, **kwargs):
        """
        Inserts a new entry to the `File` table

        :param user: The owner of the file
        :param name: The name of the file
        :param full_path: The path where the file was stored
        :param kwargs: Additional file data parameters
        :return: The created file entry
        """
        # Check parameter values
        if name == "":
            raise InvalidParameter("The 'name' parameter can't be an empty string")
        if full_path == "":
            raise InvalidParameter("The 'full_path' parameter can't be an empty string")

        # Create the new file object
        file = File(
            idUser=user.id,
            name=name,
            fullPath=full_path,
        )

        # Add the optional values to the file object
        for key, value in kwargs.items():
            if hasattr(File, key):
                setattr(file, key, value)
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Add the new row to the database
        self.add_row(file)

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return file

    def get_files(self, **kwargs):
        """
        Makes a query to the database to retrieve the file(s) following
        the filter parameters specified by the kwargs.

        :param kwargs: The filters to apply to the query
        :return: The retrieved file(s)
        """
        # Create the query object
        query = File.query.order_by(File.id.asc())

        # Filter by the given kwargs
        for key, value in kwargs.items():
            if hasattr(File, key):
                if key in ("id", "fullPath"):
                    return self.execute_query(query.filter_by(**{key: value}), use_list=False)
                else:
                    query = query.filter_by(**{key: value})
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Return all the filtered items
        return self.execute_query(query)

    def update_file(self, file: File, **kwargs):
        """
        Update the specified file entry values according to the fields specified
        by the kwargs argument.

        :param file: The SQLAlchemy database model object to update
        :param kwargs: The fields to update
        :return: The updated `File` object
        """
        # Modify the specified file fields
        for key, value in kwargs.items():
            if hasattr(File, key):
                setattr(file, key, value)
            else:
                raise InvalidParameter("Invalid '{}' parameter".format(key))

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return file

    def delete_file(self, file: File):
        """
        Deletes a file entry from the database

        :param file: The SQLAlchemy database model object to delete
        """
        # Delete the row at the database
        self.del_row(file)

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

    def delete_files(self, **kwargs):
        """
        Deletes a set of file entries from the database according to the filters
        specified by the kwargs argument.

        :param kwargs: The filters to apply to the query
        """
        # Initialize the deleted files counter
        deleted_files_count = 0

        # Get all the files with this parameters
        files = self.get_files(**kwargs)

        # Check the type of data that we obtained from the last call
        if files is None:
            return deleted_files_count
        elif isinstance(files, File):
            # Delete the retrieved file
            self.del_row(files)
            deleted_files_count = 1
        else:
            # Delete all the retrieved files
            for file in files:
                self.del_row(file)
                deleted_files_count += 1

        # Commit the changes to the database
        if self.autocommit:
            self.commit_changes()

        return deleted_files_count
