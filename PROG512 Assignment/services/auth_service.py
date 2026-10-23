# services/auth_service.py
"""
Authentication Service Module
Handles user login, registration, and session management.
"""

import re
from database.queries import QueryManager
from models.users import User, Lecturer, CampusAdministrator, SystemOperator


class AuthService:
    """Provides authentication and user management services."""

    def __init__(self):
        """Initialize with a query manager."""
        self._qm = QueryManager()

    def close(self):
        """Close the query manager connection."""
        self._qm.close()

    def login(self, username, password):
        """
        Authenticate a user with username and password.
        Returns a User subclass instance on success, or (None, error_message) on failure.
        """
        if not username or not username.strip():
            return None, "Username is required."
        if not password:
            return None, "Password is required."

        username = username.strip()
        user_row = self._qm.get_user_by_username(username)

        if not user_row:
            return None, "Invalid username or password."

        # Verify password
        if not User.verify_password(password, user_row["password_hash"], user_row["salt"]):
            return None, "Invalid username or password."

        # Create the appropriate user object based on role
        user = self._create_user_object(user_row)
        return user, "Login successful."

    def register(self, username, password, confirm_password, full_name, email, role, campus_id):
        """
        Register a new user with validation.
        Returns (success: bool, message: str).
        """
        # Input validation
        errors = self._validate_registration(
            username, password, confirm_password, full_name, email, role, campus_id
        )
        if errors:
            return False, errors

        # Hash the password
        password_hash, salt = User.hash_password(password)

        # Handle campus_id for operators
        if role == "operator":
            campus_id = None

        # Create user in database
        user_id = self._qm.create_user(
            username.strip(), password_hash, salt,
            full_name.strip(), email.strip(), role, campus_id
        )

        if user_id is None:
            return False, "Username already exists. Please choose another."

        return True, "Registration successful! You can now log in."

    def _validate_registration(self, username, password, confirm_password,
                                full_name, email, role, campus_id):
        """Validate all registration fields. Returns error message or None."""
        if not username or not username.strip():
            return "Username is required."

        if len(username.strip()) < 3:
            return "Username must be at least 3 characters long."

        if not re.match(r'^[a-zA-Z0-9_]+$', username.strip()):
            return "Username can only contain letters, numbers, and underscores."

        if not password:
            return "Password is required."

        if len(password) < 6:
            return "Password must be at least 6 characters long."

        if password != confirm_password:
            return "Passwords do not match."

        if not full_name or not full_name.strip():
            return "Full name is required."

        if not email or not email.strip():
            return "Email is required."

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.strip()):
            return "Invalid email format."

        valid_roles = ["lecturer", "administrator", "operator"]
        if role not in valid_roles:
            return "Invalid role selected."

        if role != "operator" and not campus_id:
            return "Please select a campus."

        return None

    def _create_user_object(self, user_row):
        """Create the appropriate User subclass based on role."""
        role = user_row["role"]
        if role == "lecturer":
            return Lecturer(
                user_row["user_id"], user_row["username"],
                user_row["full_name"], user_row["email"],
                user_row["campus_id"]
            )
        elif role == "administrator":
            return CampusAdministrator(
                user_row["user_id"], user_row["username"],
                user_row["full_name"], user_row["email"],
                user_row["campus_id"]
            )
        elif role == "operator":
            return SystemOperator(
                user_row["user_id"], user_row["username"],
                user_row["full_name"], user_row["email"]
            )
        return None