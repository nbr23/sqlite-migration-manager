# SQLite Migration Manager

A simple file based SQlite migration manager python library

## Installation

You can install SQLite Migration Manager using pip:

```bash
pip install sqlite-migration-manager
```

## Usage
Here's a basic example of how to use SQLite Migration Manager:

```python
from sqlite_migration_manager import SQLiteMigrationManager

db_path = 'path/to/your/database.db'
patches_dir = 'path/to/your/migration/files'

with SQLiteMigrationManager(db_path, patches_dir) as manager:
    manager.run_migrations()
```

## Migration Files
Create SQL migration files in your patches directory with names following the pattern:

```bash
001_initial_schema.sql
002_add_users_table.sql
003_add_email_to_users.sql
...
```

The numeric prefix determines the order of execution.
