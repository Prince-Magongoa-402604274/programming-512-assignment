# services/booking_service.py
"""
Booking Service Module
Handles booking creation, overlap detection, cancellation, and policy enforcement.
"""

from database.queries import QueryManager
from policies.booking_policies import PolicyFactory


class BookingService:
    """Provides booking-related business logic and validation."""

    def __init__(self):
        """Initialize with query manager."""
        self._qm = QueryManager()

    def close(self):
        """Close the query manager."""
        self._qm.close()

    def create_booking(self, resource_id, user_id, campus_id, booking_date,
                       start_time, end_time, purpose):
        """
        Create a new booking with full validation.
        Returns (success: bool, message: str).
        """
        # Validate inputs
        if not resource_id:
            return False, "Please select a resource."
        if not booking_date:
            return False, "Please enter a booking date."
        if not start_time:
            return False, "Please enter a start time."
        if not end_time:
            return False, "Please enter an end time."

        # Get campus policy and validate
        policy_type = self._qm.get_campus_policy(campus_id)
        policy = PolicyFactory.get_policy(policy_type)

        is_valid, message = policy.validate_booking(start_time, end_time, booking_date)
        if not is_valid:
            return False, message

        # Check for overlapping bookings
        if self._qm.check_overlap(resource_id, booking_date, start_time, end_time):
            return False, "This time slot conflicts with an existing booking. Please choose a different time."

        # Verify resource exists and is available
        resource = self._qm.get_resource_by_id(resource_id)
        if not resource:
            return False, "Selected resource not found."
        if not resource["is_available"]:
            return False, "Selected resource is no longer available."

        # Create the booking
        try:
            booking_id = self._qm.create_booking(
                resource_id, user_id, campus_id,
                booking_date, start_time, end_time, purpose
            )
            return True, f"Booking confirmed! Booking ID: {booking_id}"
        except Exception as e:
            return False, f"Failed to create booking: {str(e)}"

    def cancel_booking(self, booking_id, user_id=None):
        """
        Cancel a booking.
        Returns (success: bool, message: str).
        """
        if not booking_id:
            return False, "No booking selected."

        success = self._qm.cancel_booking(booking_id, user_id)
        if success:
            return True, "Booking cancelled successfully."
        else:
            return False, "Unable to cancel booking. It may already be cancelled or you don't have permission."

    def get_user_bookings(self, user_id):
        """Get all bookings for a specific user."""
        return self._qm.get_bookings_by_user(user_id)

    def get_campus_bookings(self, campus_id):
        """Get all bookings for a specific campus."""
        return self._qm.get_bookings_by_campus(campus_id)

    def get_all_bookings(self):
        """Get all bookings across campuses."""
        return self._qm.get_all_bookings()

    def get_resources_for_campus(self, campus_id):
        """Get available resources for a campus."""
        return self._qm.get_resources_by_campus(campus_id)

    def get_campus_policy(self, campus_id):
        """Get the booking policy for a campus."""
        policy_type = self._qm.get_campus_policy(campus_id)
        return PolicyFactory.get_policy(policy_type)