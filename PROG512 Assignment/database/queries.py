# database/queries.py
"""
Query Manager Module
Provides parameterized query methods for all database operations.
"""

import sqlite3
import os
from database.db_manager import DatabaseManager


class QueryManager:
    """Handles all database queries with parameterized statements."""

    def __init__(self):
        """Initialize with a fresh database connection."""
        self._db = DatabaseManager()
        self._conn = self._db.get_connection()
        self._cursor = self._db.get_cursor()

    def close(self):
        """Close the database connection."""
        self._db.close()

    # ---- User Queries ----

    def get_user_by_username(self, username):
        """Retrieve a user record by username."""
        self._cursor.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1", (username,)
        )
        return self._cursor.fetchone()

    def get_user_by_id(self, user_id):
        """Retrieve a user record by ID."""
        self._cursor.execute(
            "SELECT * FROM users WHERE user_id = ? AND is_active = 1", (user_id,)
        )
        return self._cursor.fetchone()

    def create_user(self, username, password_hash, salt, full_name, email, role, campus_id):
        """Insert a new user into the database."""
        try:
            self._cursor.execute(
                """INSERT INTO users (username, password_hash, salt, full_name, email, role, campus_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (username, password_hash, salt, full_name, email, role, campus_id)
            )
            self._conn.commit()
            return self._cursor.lastrowid
        except sqlite3.IntegrityError as e:
            return None

    def get_all_users(self):
        """Retrieve all active users."""
        self._cursor.execute("SELECT * FROM users WHERE is_active = 1")
        return self._cursor.fetchall()

    # ---- Campus Queries ----

    def get_all_campuses(self):
        """Retrieve all active campuses."""
        self._cursor.execute("SELECT * FROM campuses WHERE is_active = 1")
        return self._cursor.fetchall()

    def get_campus_by_id(self, campus_id):
        """Retrieve a campus by its ID."""
        self._cursor.execute(
            "SELECT * FROM campuses WHERE campus_id = ? AND is_active = 1", (campus_id,)
        )
        return self._cursor.fetchone()

    def get_campus_policy(self, campus_id):
        """Get the policy type for a campus."""
        self._cursor.execute(
            "SELECT policy_type FROM campuses WHERE campus_id = ?", (campus_id,)
        )
        result = self._cursor.fetchone()
        return result["policy_type"] if result else None

    # ---- Resource Queries ----

    def get_resources_by_campus(self, campus_id):
        """Retrieve all available resources for a campus."""
        self._cursor.execute(
            "SELECT * FROM resources WHERE campus_id = ? AND is_available = 1",
            (campus_id,)
        )
        return self._cursor.fetchall()

    def get_all_resources(self):
        """Retrieve all resources across all campuses."""
        self._cursor.execute(
            """SELECT r.*, c.campus_name FROM resources r
               JOIN campuses c ON r.campus_id = c.campus_id
               WHERE r.is_available = 1"""
        )
        return self._cursor.fetchall()

    def get_resource_by_id(self, resource_id):
        """Retrieve a resource by its ID."""
        self._cursor.execute(
            "SELECT * FROM resources WHERE resource_id = ?", (resource_id,)
        )
        return self._cursor.fetchone()

    def get_resource_by_uid(self, resource_uid):
        """Retrieve a resource by its unique identifier."""
        self._cursor.execute(
            "SELECT * FROM resources WHERE resource_uid = ?", (resource_uid,)
        )
        return self._cursor.fetchone()

    def add_resource(self, resource_uid, resource_name, resource_type, campus_id, capacity, description):
        """Add a new resource to the database."""
        try:
            self._cursor.execute(
                """INSERT INTO resources (resource_uid, resource_name, resource_type,
                   campus_id, capacity, description) VALUES (?, ?, ?, ?, ?, ?)""",
                (resource_uid, resource_name, resource_type, campus_id, capacity, description)
            )
            self._conn.commit()
            return self._cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def update_resource(self, resource_id, resource_name, resource_type, capacity, description):
        """Update an existing resource."""
        self._cursor.execute(
            """UPDATE resources SET resource_name = ?, resource_type = ?,
               capacity = ?, description = ? WHERE resource_id = ?""",
            (resource_name, resource_type, capacity, description, resource_id)
        )
        self._conn.commit()
        return self._cursor.rowcount > 0

    def remove_resource(self, resource_id):
        """Soft-delete a resource by marking it unavailable."""
        self._cursor.execute(
            "UPDATE resources SET is_available = 0 WHERE resource_id = ?",
            (resource_id,)
        )
        self._conn.commit()
        return self._cursor.rowcount > 0

    # ---- Booking Queries ----

    def create_booking(self, resource_id, user_id, campus_id, booking_date,
                       start_time, end_time, purpose):
        """Insert a new booking record."""
        self._cursor.execute(
            """INSERT INTO bookings (resource_id, user_id, campus_id, booking_date,
               start_time, end_time, purpose, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'confirmed')""",
            (resource_id, user_id, campus_id, booking_date, start_time, end_time, purpose)
        )
        self._conn.commit()
        return self._cursor.lastrowid

    def get_bookings_by_user(self, user_id):
        """Retrieve all bookings for a specific user."""
        self._cursor.execute(
            """SELECT b.*, r.resource_name, r.resource_uid, c.campus_name
               FROM bookings b
               JOIN resources r ON b.resource_id = r.resource_id
               JOIN campuses c ON b.campus_id = c.campus_id
               WHERE b.user_id = ? AND b.status = 'confirmed'
               ORDER BY b.booking_date, b.start_time""",
            (user_id,)
        )
        return self._cursor.fetchall()

    def get_bookings_by_campus(self, campus_id):
        """Retrieve all confirmed bookings for a campus."""
        self._cursor.execute(
            """SELECT b.*, r.resource_name, r.resource_uid, u.full_name, u.username
               FROM bookings b
               JOIN resources r ON b.resource_id = r.resource_id
               JOIN users u ON b.user_id = u.user_id
               WHERE b.campus_id = ? AND b.status = 'confirmed'
               ORDER BY b.booking_date, b.start_time""",
            (campus_id,)
        )
        return self._cursor.fetchall()

    def get_all_bookings(self):
        """Retrieve all confirmed bookings across all campuses."""
        self._cursor.execute(
            """SELECT b.*, r.resource_name, r.resource_uid, u.full_name,
                      c.campus_name
               FROM bookings b
               JOIN resources r ON b.resource_id = r.resource_id
               JOIN users u ON b.user_id = u.user_id
               JOIN campuses c ON b.campus_id = c.campus_id
               WHERE b.status = 'confirmed'
               ORDER BY b.booking_date, b.start_time"""
        )
        return self._cursor.fetchall()

    def cancel_booking(self, booking_id, user_id=None):
        """Cancel a booking. If user_id is provided, ensure ownership."""
        if user_id:
            self._cursor.execute(
                """UPDATE bookings SET status = 'cancelled'
                   WHERE booking_id = ? AND user_id = ? AND status = 'confirmed'""",
                (booking_id, user_id)
            )
        else:
            self._cursor.execute(
                """UPDATE bookings SET status = 'cancelled'
                   WHERE booking_id = ? AND status = 'confirmed'""",
                (booking_id,)
            )
        self._conn.commit()
        return self._cursor.rowcount > 0

    def check_overlap(self, resource_id, booking_date, start_time, end_time, exclude_booking_id=None):
        """Check if a booking overlaps with existing confirmed bookings."""
        if exclude_booking_id:
            self._cursor.execute(
                """SELECT COUNT(*) FROM bookings
                   WHERE resource_id = ? AND booking_date = ? AND status = 'confirmed'
                   AND booking_id != ?
                   AND NOT (end_time <= ? OR start_time >= ?)""",
                (resource_id, booking_date, exclude_booking_id, start_time, end_time)
            )
        else:
            self._cursor.execute(
                """SELECT COUNT(*) FROM bookings
                   WHERE resource_id = ? AND booking_date = ? AND status = 'confirmed'
                   AND NOT (end_time <= ? OR start_time >= ?)""",
                (resource_id, booking_date, start_time, end_time)
            )
        return self._cursor.fetchone()[0] > 0

    # ---- Report Queries ----

    def get_total_bookings_count(self, campus_id=None):
        """Get total number of confirmed bookings, optionally filtered by campus."""
        if campus_id:
            self._cursor.execute(
                "SELECT COUNT(*) FROM bookings WHERE campus_id = ? AND status = 'confirmed'",
                (campus_id,)
            )
        else:
            self._cursor.execute(
                "SELECT COUNT(*) FROM bookings WHERE status = 'confirmed'"
            )
        return self._cursor.fetchone()[0]

    def get_most_used_resources(self, campus_id=None, limit=5):
        """Get the most frequently booked resources."""
        if campus_id:
            self._cursor.execute(
                """SELECT r.resource_name, r.resource_uid, c.campus_name,
                          COUNT(b.booking_id) as booking_count
                   FROM bookings b
                   JOIN resources r ON b.resource_id = r.resource_id
                   JOIN campuses c ON b.campus_id = c.campus_id
                   WHERE b.status = 'confirmed' AND b.campus_id = ?
                   GROUP BY b.resource_id
                   ORDER BY booking_count DESC
                   LIMIT ?""",
                (campus_id, limit)
            )
        else:
            self._cursor.execute(
                """SELECT r.resource_name, r.resource_uid, c.campus_name,
                          COUNT(b.booking_id) as booking_count
                   FROM bookings b
                   JOIN resources r ON b.resource_id = r.resource_id
                   JOIN campuses c ON b.campus_id = c.campus_id
                   WHERE b.status = 'confirmed'
                   GROUP BY b.resource_id
                   ORDER BY booking_count DESC
                   LIMIT ?""",
                (limit,)
            )
        return self._cursor.fetchall()

    def get_average_booking_duration(self, campus_id=None):
        """Calculate the average booking duration in minutes."""
        if campus_id:
            self._cursor.execute(
                """SELECT AVG(
                       (CAST(substr(end_time, 1, 2) AS INTEGER) * 60 +
                        CAST(substr(end_time, 4, 2) AS INTEGER)) -
                       (CAST(substr(start_time, 1, 2) AS INTEGER) * 60 +
                        CAST(substr(start_time, 4, 2) AS INTEGER))
                   ) as avg_duration
                   FROM bookings
                   WHERE status = 'confirmed' AND campus_id = ?""",
                (campus_id,)
            )
        else:
            self._cursor.execute(
                """SELECT AVG(
                       (CAST(substr(end_time, 1, 2) AS INTEGER) * 60 +
                        CAST(substr(end_time, 4, 2) AS INTEGER)) -
                       (CAST(substr(start_time, 1, 2) AS INTEGER) * 60 +
                        CAST(substr(start_time, 4, 2) AS INTEGER))
                   ) as avg_duration
                   FROM bookings
                   WHERE status = 'confirmed'"""
            )
        result = self._cursor.fetchone()[0]
        return round(result, 1) if result else 0

    def get_campus_comparison(self):
        """Get booking statistics for each campus for cross-campus comparison."""
        self._cursor.execute(
            """SELECT c.campus_name, c.campus_id,
                      COUNT(b.booking_id) as total_bookings,
                      COUNT(DISTINCT b.resource_id) as unique_resources_used,
                      COUNT(DISTINCT b.user_id) as unique_users,
                      AVG(
                          (CAST(substr(b.end_time, 1, 2) AS INTEGER) * 60 +
                           CAST(substr(b.end_time, 4, 2) AS INTEGER)) -
                          (CAST(substr(b.start_time, 1, 2) AS INTEGER) * 60 +
                           CAST(substr(b.start_time, 4, 2) AS INTEGER))
                      ) as avg_duration
               FROM campuses c
               LEFT JOIN bookings b ON c.campus_id = b.campus_id AND b.status = 'confirmed'
               WHERE c.is_active = 1
               GROUP BY c.campus_id
               ORDER BY total_bookings DESC"""
        )
        return self._cursor.fetchall()

    def get_bookings_per_campus_count(self):
        """Get the count of bookings per campus."""
        self._cursor.execute(
            """SELECT c.campus_name, COUNT(b.booking_id) as count
               FROM campuses c
               LEFT JOIN bookings b ON c.campus_id = b.campus_id AND b.status = 'confirmed'
               GROUP BY c.campus_id"""
        )
        return self._cursor.fetchall()