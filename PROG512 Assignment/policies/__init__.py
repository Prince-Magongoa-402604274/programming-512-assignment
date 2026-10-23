# policies/__init__.py
"""Policies package - booking policy hierarchy using Open/Closed Principle."""
from policies.booking_policies import (
    BookingPolicy, StandardPolicy, ExtendedHoursPolicy,
    PriorityAccessPolicy, RestrictedHoursPolicy, PolicyFactory
)