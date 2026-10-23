# models/users.py
"""
User Models Module
Defines the user class hierarchy with encapsulation and hashed passwords.
Uses inheritance: User (base) -> Lecturer, CampusAdministrator, SystemOperator
"""

import hashlib
import os


class User:
    """
    Base User class with encapsulated attributes and password hashing.
    All user types inherit from this class.
    """

    def __init__(self, user_id, username, full_name, email, role, campus_id=None):
        """Initialize a User with encapsulated private attributes."""
        self.__user_id = user_id
        self.__username = username
        self.__full_name = full_name
        self.__email = email
        self.__role = role
        self.__campus_id = campus_id

    # --- Property accessors (encapsulation) ---

    @property
    def user_id(self):
        """Get user ID."""
        return self.__user_id

    @property
    def username(self):
        """Get username."""
        return self.__username

    @property
    def full_name(self):
        """Get full name."""
        return self.__full_name

    @full_name.setter
    def full_name(self, value):
        """Set full name with validation."""
        if not value or not value.strip():
            raise ValueError("Full name cannot be empty.")
        self.__full_name = value.strip()

    @property
    def email(self):
        """Get email address."""
        return self.__email

    @email.setter
    def email(self, value):
        """Set email with basic validation."""
        if not value or "@" not in value:
            raise ValueError("Invalid email address.")
        self.__email = value.strip()

    @property
    def role(self):
        """Get user role."""
        return self.__role

    @property
    def campus_id(self):
        """Get associated campus ID."""
        return self.__campus_id

    @campus_id.setter
    def campus_id(self, value):
        """Set campus ID."""
        self.__campus_id = value

    @staticmethod
    def hash_password(password, salt=None):
        """
        Hash a password using SHA-256 with a salt.
        Returns tuple of (hash, salt).
        """
        if salt is None:
            salt = os.urandom(32).hex()
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt

    @staticmethod
    def verify_password(password, stored_hash, salt):
        """Verify a password against a stored hash and salt."""
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == stored_hash

    def get_permissions(self):
        """Return base permissions. Overridden by subclasses."""
        return []

    def __str__(self):
        """String representation of the user."""
        return f"{self.__full_name} ({self.__role})"


class Lecturer(User):
    """
    Lecturer user - can book resources and view/cancel own bookings.
    """

    def __init__(self, user_id, username, full_name, email, campus_id):
        """Initialize a Lecturer."""
        super().__init__(user_id, username, full_name, email, "lecturer", campus_id)

    def get_permissions(self):
        """Lecturers can book, view, and cancel their own bookings."""
        return ["book_resource", "view_own_bookings", "cancel_own_booking"]


class CampusAdministrator(User):
    """
    Campus Administrator - manages resources and views campus bookings.
    """

    def __init__(self, user_id, username, full_name, email, campus_id):
        """Initialize a Campus Administrator."""
        super().__init__(user_id, username, full_name, email, "administrator", campus_id)

    def get_permissions(self):
        """Administrators can manage resources and view campus bookings."""
        return [
            "add_resource", "update_resource", "remove_resource",
            "view_campus_bookings", "manage_campus"
        ]


class SystemOperator(User):
    """
    System Operator - views all campuses and generates system-wide reports.
    """

    def __init__(self, user_id, username, full_name, email):
        """Initialize a System Operator (no specific campus)."""
        super().__init__(user_id, username, full_name, email, "operator", None)

    def get_permissions(self):
        """Operators can view all data and generate reports."""
        return [
            "view_all_campuses", "view_all_bookings",
            "generate_reports", "cross_campus_comparison"
        ]