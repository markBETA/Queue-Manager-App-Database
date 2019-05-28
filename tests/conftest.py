import os

import pytest

from ... import create_app
from .. import db as _db
from .. import db_mgr

TEST_DB = 'test.db'
TEST_DB_PATH = "{}".format(TEST_DB)
TEST_DATABASE_URI = 'sqlite:///' + TEST_DB_PATH

os.chdir(os.path.dirname(__file__))


@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + TEST_DB_PATH,
        'SQLALCHEMY_TRACK_MODIFICATIONS': True,
        'TEST_INPUTS_PATH': 'input',
        'SECRET_KEY': os.getenv('SECRET_KEY', 'my_secret_key')
    }
    enabled_modules = {
        "app-database"
    }
    app = create_app(__name__, settings_override, enabled_modules=enabled_modules)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test app_database."""
    if os.path.exists(TEST_DB_PATH):
        os.unlink(TEST_DB_PATH)

    def teardown():
        _db.drop_all()
        if os.path.exists(TEST_DB_PATH):
            os.unlink(TEST_DB_PATH)

    connection = _db.engine.connect()
    options = dict(bind=connection, binds={})
    session = _db.create_scoped_session(options=options)
    _db.session = session

    _db.create_all()

    connection.close()
    session.remove()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new app_database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    def teardown():
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope='function')
def db_manager(session):
    """Creates a new app_database DBManager instance for a test."""
    db_mgr.update_session(session)
    db_mgr.init_static_values()
    db_mgr.init_printers_state()
    db_mgr.init_jobs_can_be_printed()

    return db_mgr
