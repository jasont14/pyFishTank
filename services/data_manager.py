"""Data manager for SQLite database operations."""

import sqlite3
from pathlib import Path
from typing import Optional


class DataManager:
    """Handles SQLite database operations for pyFishTank."""

    def __init__(self, db_path: str = "data/fishtank.db"):
        """Initialize the data manager.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = Path(db_path)
        self._ensure_data_dir()
        self._connection: Optional[sqlite3.Connection] = None
        self._init_database()

    def _ensure_data_dir(self) -> None:
        """Create data directory if it doesn't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def _init_database(self) -> None:
        """Initialize database tables."""
        cursor = self.connection.cursor()

        # Tanks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tanks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                size_gallons REAL NOT NULL,
                tank_type TEXT NOT NULL,
                location TEXT DEFAULT '',
                equipment TEXT DEFAULT ''
            )
        """)

        # Water parameters table (for current tank parameters)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS water_parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tank_id TEXT,
                date_tested TEXT NOT NULL,
                temperature REAL,
                ph REAL,
                ammonia REAL,
                nitrite REAL,
                nitrate REAL,
                salinity REAL,
                FOREIGN KEY (tank_id) REFERENCES tanks(id)
            )
        """)

        # Fish table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fish (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                tank_id TEXT NOT NULL,
                date_added TEXT NOT NULL,
                birth_date TEXT,
                health_status TEXT DEFAULT 'healthy',
                size TEXT,
                color TEXT,
                feeding_preferences TEXT,
                notes TEXT,
                FOREIGN KEY (tank_id) REFERENCES tanks(id)
            )
        """)

        # Maintenance logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_logs (
                id TEXT PRIMARY KEY,
                tank_id TEXT NOT NULL,
                date TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                description TEXT NOT NULL,
                water_params_id INTEGER,
                FOREIGN KEY (tank_id) REFERENCES tanks(id),
                FOREIGN KEY (water_params_id) REFERENCES water_parameters(id)
            )
        """)

        self.connection.commit()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return the cursor."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor

    def commit(self) -> None:
        """Commit the current transaction."""
        self.connection.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
