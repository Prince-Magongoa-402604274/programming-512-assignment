# database/db_manager.py
"""
Database Manager Module
Handles SQLite database creation, connection, and table initialization.
"""

import sqlite3
import os
import hashlib


class DatabaseManager:
    """Manages SQLite database connections and schema creation."""

    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "smart_campus.db")

    def __init__(self):
        """Initialize database connection."""
        self._connection = sqlite3.connect(self.DB_PATH)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._cursor = self._connection.cursor()

    def get_connection(self):
        """Return the active database connection."""
        return self._connection

    def get_cursor(self):
        """Return the active cursor."""
        return self._cursor

    def initialize_database(self):
        """Create all required tables if they don't exist."""

        # Users table with role-based access
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('lecturer', 'administrator', 'operator')),
                campus_id INTEGER,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
            )
        """)

        # Campuses table
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS campuses (
                campus_id INTEGER PRIMARY KEY AUTOINCREMENT,
                campus_name TEXT UNIQUE NOT NULL,
                location TEXT NOT NULL,
                policy_type TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Resources table with unique ID
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_uid TEXT UNIQUE NOT NULL,
                resource_name TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                campus_id INTEGER NOT NULL,
                capacity INTEGER DEFAULT 0,
                description TEXT,
                is_available INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
            )
        """)

        # Bookings table
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                campus_id INTEGER NOT NULL,
                booking_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                purpose TEXT,
                status TEXT DEFAULT 'confirmed' CHECK(status IN ('confirmed', 'cancelled', 'completed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (campus_id) REFERENCES campuses(campus_id)
            )
        """)

        self._connection.commit()

    def seed_default_data(self):
        """Insert default campuses and an operator account if not present."""

        # Check if campuses already exist
        self._cursor.execute("SELECT COUNT(*) FROM campuses")
        count = self._cursor.fetchone()[0]

        if count == 0:
            # Insert default campuses with different policy types
            campuses = [
                ("Main Campus", "Downtown City Center", "standard"),
                ("Science Campus", "North Research Park", "extended_hours"),
                ("Engineering Campus", "Industrial District", "priority_access"),
                ("Medical Campus", "Hospital Complex", "restricted_hours"),
            ]
            self._cursor.executemany(
                "INSERT INTO campuses (campus_name, location, policy_type) VALUES (?, ?, ?)",
                campuses
            )

        # Check if operator account exists
        self._cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'operator'")
        op_count = self._cursor.fetchone()[0]

        if op_count == 0:
            # Create default system operator account
            salt = os.urandom(32).hex()
            password_hash = hashlib.sha256(("admin123" + salt).encode()).hexdigest()
            self._cursor.execute(
                """INSERT INTO users (username, password_hash, salt, full_name, email, role, campus_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("operator", password_hash, salt, "System Operator",
                 "operator@smartcampus.edu", "operator", None)
            )

        self._connection.commit()

    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()