"""
Alembic environment configuration for MongoDB migrations.
This file is responsible for configuring the Alembic environment
and providing access to the database connection.
"""

import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from pymongo import MongoClient

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Load environment variables
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the MongoDB URL from environment variables
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME", "teacher_query")

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client[db_name]

# Make the db and client available to the migration scripts
def get_db():
    return db

def get_client():
    return client

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # For MongoDB, we don't use SQLAlchemy URL
    context.configure(
        url=None,
        target_metadata=None,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # For MongoDB, we don't use SQLAlchemy Engine
    connectable = None

    with connectable.connect() if connectable else context.begin_transaction():
        context.configure(
            url=None,
            target_metadata=None,
            connection=connectable,
            compare_type=True,
        )

        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()