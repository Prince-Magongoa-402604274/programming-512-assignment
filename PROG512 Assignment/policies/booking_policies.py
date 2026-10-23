# policies/booking_policies.py
"""
Booking Policies Module
Implements the Strategy/Template pattern for campus-specific booking rules.
New campuses can be added by creating a new subclass without modifying existing code.
"""

from datetime import datetime


class BookingPolicy:
    """
    Base booking policy class.
    Defines the interface and common validation logic.
    Subclasses override specific rules.
    """

    POLICY_NAME = "Base Policy"
    POLICY_DESCRIPTION = "Default booking policy"

    def get_max_duration_minutes(self):
        """Return maximum allowed booking duration in minutes."""
        return 120  # Default: 2 hours

    def get_allowed_start_hour(self):
        """Return the earliest allowed booking hour (24h format)."""
        return 7

    def get_allowed_end_hour(self):
        """Return the latest allowed booking end hour (24h format)."""
        return 22

    def has_priority_access(self):
        """Whether this policy supports priority/extended access."""
        return False

    def get_max_bookings_per_day(self):
        """Maximum number of bookings a user can make per day."""
        return 5

    def validate_booking(self, start_time_str, end_time_str, booking_date_str):
        """
        Validate a booking against this policy's rules.
        Returns (is_valid, error_message).
        """
        errors = []

        try:
            start_time = datetime.strptime(start_time_str, "%H:%M")
            end_time = datetime.strptime(end_time_str, "%H:%M")
            booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d")
        except ValueError:
            return False, "Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time."

        # Check that end time is after start time
        if end_time <= start_time:
            errors.append("End time must be after start time.")

        # Check booking is not in the past
        now = datetime.now()
        booking_datetime = datetime.combine(booking_date.date(), start_time.time())
        if booking_datetime < now:
            errors.append("Cannot book in the past.")

        # Check duration
        duration_minutes = (end_time - start_time).seconds // 60
        max_dur = self.get_max_duration_minutes()
        if duration_minutes > max_dur:
            errors.append(f"Booking exceeds maximum duration of {max_dur} minutes.")

        # Check allowed hours
        start_hour = start_time.hour
        end_hour = end_time.hour
        end_minute = end_time.minute

        if start_hour < self.get_allowed_start_hour():
            errors.append(f"Bookings cannot start before {self.get_allowed_start_hour():02d}:00.")

        # Allow end_hour == allowed_end_hour only if minutes == 0
        if end_hour > self.get_allowed_end_hour() or (end_hour == self.get_allowed_end_hour() and end_minute > 0 and self.get_allowed_end_hour() != 24):
            errors.append(f"Bookings cannot end after {self.get_allowed_end_hour():02d}:00.")

        if errors:
            return False, " ".join(errors)

        return True, "Booking is valid."

    def get_policy_info(self):
        """Return a description of this policy's rules."""
        return (
            f"Policy: {self.POLICY_NAME}\n"
            f"{self.POLICY_DESCRIPTION}\n"
            f"Max Duration: {self.get_max_duration_minutes()} minutes\n"
            f"Allowed Hours: {self.get_allowed_start_hour():02d}:00 - "
            f"{self.get_allowed_end_hour():02d}:00\n"
            f"Max Bookings/Day: {self.get_max_bookings_per_day()}"
        )


class StandardPolicy(BookingPolicy):
    """
    Standard campus policy with moderate restrictions.
    Max 2 hours, 07:00-18:00, up to 5 bookings per day.
    """

    POLICY_NAME = "Standard Policy"
    POLICY_DESCRIPTION = "Regular booking rules with moderate restrictions."

    def get_max_duration_minutes(self):
        return 120

    def get_allowed_start_hour(self):
        return 7

    def get_allowed_end_hour(self):
        return 18

    def get_max_bookings_per_day(self):
        return 5


class ExtendedHoursPolicy(BookingPolicy):
    """
    Extended hours policy for research-focused campuses.
    Max 4 hours, 06:00-23:00, up to 3 bookings per day.
    """

    POLICY_NAME = "Extended Hours Policy"
    POLICY_DESCRIPTION = "Extended operating hours for research activities."

    def get_max_duration_minutes(self):
        return 240

    def get_allowed_start_hour(self):
        return 6

    def get_allowed_end_hour(self):
        return 23

    def get_max_bookings_per_day(self):
        return 3


class PriorityAccessPolicy(BookingPolicy):
    """
    Priority access policy for engineering campus.
    Max 3 hours, 08:00-20:00, priority users can book longer.
    """

    POLICY_NAME = "Priority Access Policy"
    POLICY_DESCRIPTION = "Priority booking with extended duration for senior lecturers."

    def get_max_duration_minutes(self):
        return 180

    def get_allowed_start_hour(self):
        return 8

    def get_allowed_end_hour(self):
        return 20

    def has_priority_access(self):
        return True

    def get_max_bookings_per_day(self):
        return 4


class RestrictedHoursPolicy(BookingPolicy):
    """
    Restricted hours policy for medical campus.
    Max 1.5 hours, 09:00-16:00, limited bookings to ensure availability.
    """

    POLICY_NAME = "Restricted Hours Policy"
    POLICY_DESCRIPTION = "Limited hours and duration for high-demand medical facilities."

    def get_max_duration_minutes(self):
        return 90

    def get_allowed_start_hour(self):
        return 9

    def get_allowed_end_hour(self):
        return 16

    def get_max_bookings_per_day(self):
        return 2


class PolicyFactory:
    """
    Factory class to create the appropriate policy based on campus type.
    New policies can be registered without modifying existing code (OCP).
    """

    # Registry of policy types mapped to their classes
    _policies = {
        "standard": StandardPolicy,
        "extended_hours": ExtendedHoursPolicy,
        "priority_access": PriorityAccessPolicy,
        "restricted_hours": RestrictedHoursPolicy,
    }

    @classmethod
    def get_policy(cls, policy_type):
        """
        Get a policy instance by type string.
        Returns StandardPolicy as default if type is unknown.
        """
        policy_class = cls._policies.get(policy_type, StandardPolicy)
        return policy_class()

    @classmethod
    def register_policy(cls, policy_type, policy_class):
        """Register a new policy type (Open/Closed Principle)."""
        cls._policies[policy_type] = policy_class

    @classmethod
    def get_all_policy_types(cls):
        """Return all registered policy type names."""
        return list(cls._policies.keys())