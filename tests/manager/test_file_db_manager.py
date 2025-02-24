"""
This module implements the file data related database manager testing.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from ...models import (
    User
)


def _add_file(db_manager, user):
    file = db_manager.insert_file(user, "test-file", "/var/lib/test-file", fileData={"a": 1})

    return file


def test_file_db_manager(db_manager):
    user = User.query.first()
    expected_file = _add_file(db_manager, user)

    file = db_manager.get_files(name="test-file")
    assert expected_file == file[0]

    file = db_manager.get_files(id=expected_file.id)
    assert expected_file == file

    file = db_manager.update_file(file, estimatedNeededMaterial=105.2)
    assert file.estimatedNeededMaterial == 105.2

    deleted_files_count = db_manager.delete_files(id=file.id)
    assert deleted_files_count == 1

    file = db_manager.get_files(id=expected_file.id)
    assert file is None

    another_file = _add_file(db_manager, user)
    deleted_files_count = db_manager.delete_files(name="test-file")
    assert deleted_files_count == 1

    file = db_manager.get_files(id=another_file.id)
    assert file is None

    another_file = _add_file(db_manager, user)
    db_manager.delete_file(another_file)

    file = db_manager.get_files(id=another_file.id)
    assert file is None
