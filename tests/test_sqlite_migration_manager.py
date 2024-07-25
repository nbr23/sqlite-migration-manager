import unittest
import os
import sqlite3
import tempfile
from sqlite_migration_manager import SQLiteMigrationManager

class TestSQLiteMigrationManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for our test database and migration files
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.patches_dir = os.path.join(self.temp_dir, 'patches')
        os.mkdir(self.patches_dir)

        # Create some test migration files
        self.create_migration_file('001_initial.sql', 'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);')
        self.create_migration_file('002_add_email.sql', 'ALTER TABLE users ADD COLUMN email TEXT;')
        self.create_migration_file('003_add_age.sql', 'ALTER TABLE users ADD COLUMN age INTEGER;')

    def tearDown(self):
        # Clean up temporary files and directories
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def create_migration_file(self, filename, content):
        with open(os.path.join(self.patches_dir, filename), 'w') as f:
            f.write(content)

    def test_init(self):
        with SQLiteMigrationManager(self.db_path, self.patches_dir) as manager:
            self.assertIsNotNone(manager.conn)
            self.assertIsNotNone(manager.cursor)

    def test_get_current_version(self):
        with SQLiteMigrationManager(self.db_path, self.patches_dir) as manager:
            version = manager.get_current_version()
            self.assertEqual(version, 0)  # Initial version should be 0

    def test_set_version(self):
        with SQLiteMigrationManager(self.db_path, self.patches_dir) as manager:
            manager.set_version(5)
            version = manager.get_current_version()
            self.assertEqual(version, 5)

    def test_get_migration_files(self):
        with SQLiteMigrationManager(self.db_path, self.patches_dir) as manager:
            files = manager.get_migration_files()
            self.assertEqual(len(files), 3)
            self.assertEqual(files[0], (1, '001_initial.sql'))
            self.assertEqual(files[1], (2, '002_add_email.sql'))
            self.assertEqual(files[2], (3, '003_add_age.sql'))

    def test_apply_migration(self):
        with SQLiteMigrationManager(self.db_path, self.patches_dir) as manager:
            manager.apply_migration('001_initial.sql')
            # Check if the table was created
            manager.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            result = manager.cursor.fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result[0], 'users')

    def test_run_migrations(self):
        with SQLiteMigrationManager(self.db_path, self.patches_dir) as manager:
            manager.run_migrations()
            # Check final version
            version = manager.get_current_version()
            self.assertEqual(version, 3)
            # Check if all migrations were applied
            manager.cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in manager.cursor.fetchall()]
            self.assertIn('id', columns)
            self.assertIn('name', columns)
            self.assertIn('email', columns)
            self.assertIn('age', columns)

    def test_run_migrations_idempotent(self):
        with SQLiteMigrationManager(self.db_path, self.patches_dir) as manager:
            manager.run_migrations()
            version1 = manager.get_current_version()
            # Run migrations again
            manager.run_migrations()
            version2 = manager.get_current_version()
            self.assertEqual(version1, version2)

    def test_connection_closed_after_context(self):
        with SQLiteMigrationManager(self.db_path, self.patches_dir) as manager:
            pass
        # Connection should be closed after exiting the context
        with self.assertRaises(sqlite3.ProgrammingError):
            manager.cursor.execute("SELECT 1")

if __name__ == '__main__':
    unittest.main()
