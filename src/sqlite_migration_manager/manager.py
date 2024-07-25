import os
import sqlite3
from typing import List, Tuple

class SQLiteMigrationManager:
    def __init__(self, db_path: str, patches_dir: str):
        self.db_path = db_path
        self.patches_dir = patches_dir
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_current_version(self) -> int:
        self.cursor.execute("PRAGMA user_version")
        return self.cursor.fetchone()[0]

    def set_version(self, version: int):
        self.cursor.execute(f"PRAGMA user_version = {version}")
        self.conn.commit()

    def get_migration_files(self) -> List[Tuple[int, str]]:
        migration_files = []
        for filename in os.listdir(self.patches_dir):
            if filename.endswith('.sql'):
                try:
                    version = int(filename.split('_')[0])
                    migration_files.append((version, filename))
                except ValueError:
                    continue
        return sorted(migration_files)

    def apply_migration(self, filename: str):
        with open(os.path.join(self.patches_dir, filename), 'r') as f:
            sql = f.read()
        self.cursor.executescript(sql)
        self.conn.commit()

    def run_migrations(self):
        current_version = self.get_current_version()
        migrations = self.get_migration_files()

        for version, filename in migrations:
            if version > current_version:
                print(f"Applying migration: {filename}")
                self.apply_migration(filename)
                self.set_version(version)
                print(f"Migration applied. New version: {version}")
