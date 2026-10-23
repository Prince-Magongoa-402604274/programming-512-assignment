# services/report_service.py
"""
Report Service Module
Generates reports and statistics for system operators.
"""

from database.queries import QueryManager


class ReportService:
    """Provides reporting and analytics functionality."""

    def __init__(self):
        """Initialize with query manager."""
        self._qm = QueryManager()

    def close(self):
        """Close the query manager."""
        self._qm.close()

    def get_summary_report(self):
        """
        Generate a comprehensive summary report.
        Returns a dictionary with all key metrics.
        """
        report = {
            "total_bookings": self._qm.get_total_bookings_count(),
            "most_used_resources": self._qm.get_most_used_resources(limit=10),
            "average_duration": self._qm.get_average_booking_duration(),
            "campus_comparison": self._qm.get_campus_comparison(),
            "campuses": self._qm.get_all_campuses(),
        }
        return report

    def get_campus_report(self, campus_id):
        """Generate a report for a specific campus."""
        campus = self._qm.get_campus_by_id(campus_id)
        return {
            "campus": campus,
            "total_bookings": self._qm.get_total_bookings_count(campus_id),
            "most_used_resources": self._qm.get_most_used_resources(campus_id, limit=5),
            "average_duration": self._qm.get_average_booking_duration(campus_id),
        }

    def get_cross_campus_comparison(self):
        """Get cross-campus comparison data."""
        return self._qm.get_campus_comparison()

    def format_summary_report(self):
        """Generate a formatted text summary report."""
        report = self.get_summary_report()
        lines = []
        lines.append("=" * 60)
        lines.append("   SMART CAMPUS RESOURCE BOOKING - SYSTEM REPORT")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Total Confirmed Bookings: {report['total_bookings']}")
        lines.append(f"Average Booking Duration: {report['average_duration']} minutes")
        lines.append("")

        # Most Used Resources
        lines.append("-" * 40)
        lines.append("TOP MOST USED RESOURCES:")
        lines.append("-" * 40)
        for i, res in enumerate(report["most_used_resources"], 1):
            lines.append(
                f"  {i}. {res['resource_name']} ({res['resource_uid']}) "
                f"- {res['campus_name']} - {res['booking_count']} bookings"
            )
        if not report["most_used_resources"]:
            lines.append("  No bookings recorded yet.")
        lines.append("")

        # Cross-Campus Comparison
        lines.append("-" * 40)
        lines.append("CROSS-CAMPUS COMPARISON:")
        lines.append("-" * 40)
        for campus in report["campus_comparison"]:
            avg_dur = round(campus["avg_duration"], 1) if campus["avg_duration"] else 0
            lines.append(
                f"  {campus['campus_name']}:\n"
                f"    Bookings: {campus['total_bookings']} | "
                f"Unique Resources: {campus['unique_resources_used']} | "
                f"Unique Users: {campus['unique_users']} | "
                f"Avg Duration: {avg_dur} min"
            )
        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)