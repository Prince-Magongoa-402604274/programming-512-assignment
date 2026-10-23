# gui/operator_dashboard.py
"""
Operator Dashboard Module
System operators can view all campuses and generate comprehensive reports.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from services.report_service import ReportService
from services.booking_service import BookingService
from database.queries import QueryManager


class OperatorDashboard:
    """System Operator dashboard with reporting and cross-campus views."""

    def __init__(self, root, user):
        """Initialize operator dashboard."""
        self.root = root
        self.user = user
        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        """Build the operator dashboard."""
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text=f"System Operator - {self.user.full_name}",
                  font=("Helvetica", 14, "bold")).pack(side=tk.LEFT)

        ttk.Button(header_frame, text="Logout", command=self._logout).pack(side=tk.RIGHT, padx=3)

        # Notebook with tabs
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Tab 1: All Campuses
        self.campus_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.campus_tab, text="All Campuses")
        self._build_campus_tab()

        # Tab 2: All Bookings
        self.bookings_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.bookings_tab, text="All Bookings")
        self._build_all_bookings_tab()

        # Tab 3: Reports
        self.reports_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.reports_tab, text="Reports & Analytics")
        self._build_reports_tab()

        # Tab 4: Cross-Campus Comparison
        self.comparison_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.comparison_tab, text="Cross-Campus Comparison")
        self._build_comparison_tab()

    def _build_campus_tab(self):
        """Show all campuses with their details."""
        columns = ("id", "name", "location", "policy", "status")
        self.campus_tree = ttk.Treeview(self.campus_tab, columns=columns,
                                         show="headings", height=12)

        self.campus_tree.heading("id", text="ID")
        self.campus_tree.heading("name", text="Campus Name")
        self.campus_tree.heading("location", text="Location")
        self.campus_tree.heading("policy", text="Policy Type")
        self.campus_tree.heading("status", text="Status")

        self.campus_tree.column("id", width=40)
        self.campus_tree.column("name", width=180)
        self.campus_tree.column("location", width=200)
        self.campus_tree.column("policy", width=150)
        self.campus_tree.column("status", width=80)

        self.campus_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(self.campus_tab, text="Refresh", command=self._refresh_campuses,
                   width=12).pack(pady=5)

        self._refresh_campuses()

    def _refresh_campuses(self):
        """Refresh campus list."""
        for item in self.campus_tree.get_children():
            self.campus_tree.delete(item)

        qm = QueryManager()
        campuses = qm.get_all_campuses()
        qm.close()

        for c in campuses:
            self.campus_tree.insert("", tk.END, values=(
                c["campus_id"], c["campus_name"], c["location"],
                c["policy_type"].replace("_", " ").title(),
                "Active" if c["is_active"] else "Inactive"
            ))

    def _build_all_bookings_tab(self):
        """Show all bookings across all campuses."""
        columns = ("id", "resource", "user", "campus", "date", "start", "end", "purpose")
        self.all_bookings_tree = ttk.Treeview(self.bookings_tab, columns=columns,
                                               show="headings", height=14)

        self.all_bookings_tree.heading("id", text="ID")
        self.all_bookings_tree.heading("resource", text="Resource")
        self.all_bookings_tree.heading("user", text="User")
        self.all_bookings_tree.heading("campus", text="Campus")
        self.all_bookings_tree.heading("date", text="Date")
        self.all_bookings_tree.heading("start", text="Start")
        self.all_bookings_tree.heading("end", text="End")
        self.all_bookings_tree.heading("purpose", text="Purpose")

        self.all_bookings_tree.column("id", width=35)
        self.all_bookings_tree.column("resource", width=120)
        self.all_bookings_tree.column("user", width=100)
        self.all_bookings_tree.column("campus", width=110)
        self.all_bookings_tree.column("date", width=85)
        self.all_bookings_tree.column("start", width=50)
        self.all_bookings_tree.column("end", width=50)
        self.all_bookings_tree.column("purpose", width=130)

        scrollbar = ttk.Scrollbar(self.bookings_tab, orient=tk.VERTICAL,
                                   command=self.all_bookings_tree.yview)
        self.all_bookings_tree.configure(yscrollcommand=scrollbar.set)
        self.all_bookings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        btn_frame = ttk.Frame(self.bookings_tab)
        btn_frame.pack(side=tk.RIGHT, padx=10, anchor=tk.N)
        ttk.Button(btn_frame, text="Refresh", command=self._refresh_all_bookings,
                   width=12).pack(pady=5)

        self._refresh_all_bookings()

    def _refresh_all_bookings(self):
        """Refresh all bookings list."""
        for item in self.all_bookings_tree.get_children():
            self.all_bookings_tree.delete(item)

        bs = BookingService()
        bookings = bs.get_all_bookings()
        bs.close()

        for b in bookings:
            self.all_bookings_tree.insert("", tk.END, values=(
                b["booking_id"], b["resource_name"], b["full_name"],
                b["campus_name"], b["booking_date"],
                b["start_time"], b["end_time"], b["purpose"] or ""
            ))

    def _build_reports_tab(self):
        """Build the reports generation tab."""
        # Button bar
        btn_frame = ttk.Frame(self.reports_tab)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_frame, text="Generate Full Report",
                   command=self._generate_full_report, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Total Bookings",
                   command=self._show_total_bookings, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Most Used Resources",
                   command=self._show_most_used, width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Average Duration",
                   command=self._show_avg_duration, width=15).pack(side=tk.LEFT, padx=5)

        # Report display area
        self.report_text = scrolledtext.ScrolledText(self.reports_tab,
                                                      font=("Courier", 10),
                                                      wrap=tk.WORD, height=20)
        self.report_text.pack(fill=tk.BOTH, expand=True)

    def _generate_full_report(self):
        """Generate and display the full system report."""
        rs = ReportService()
        report_text = rs.format_summary_report()
        rs.close()

        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, report_text)
        self.report_text.config(state=tk.DISABLED)

    def _show_total_bookings(self):
        """Show total bookings metric."""
        rs = ReportService()
        report = rs.get_summary_report()
        rs.close()

        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, f"Total Confirmed Bookings: {report['total_bookings']}\n\n")

        for campus in report["campus_comparison"]:
            self.report_text.insert(tk.END,
                                    f"  {campus['campus_name']}: {campus['total_bookings']} bookings\n")

        self.report_text.config(state=tk.DISABLED)

    def _show_most_used(self):
        """Show most used resources."""
        rs = ReportService()
        report = rs.get_summary_report()
        rs.close()

        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, "Most Used Resources:\n")
        self.report_text.insert(tk.END, "-" * 40 + "\n")

        for i, res in enumerate(report["most_used_resources"], 1):
            self.report_text.insert(tk.END,
                                    f"  {i}. {res['resource_name']} ({res['resource_uid']}) "
                                    f"- {res['campus_name']} - {res['booking_count']} bookings\n")

        if not report["most_used_resources"]:
            self.report_text.insert(tk.END, "  No bookings recorded yet.\n")

        self.report_text.config(state=tk.DISABLED)

    def _show_avg_duration(self):
        """Show average booking duration."""
        rs = ReportService()
        report = rs.get_summary_report()
        rs.close()

        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END,
                                f"Overall Average Booking Duration: {report['average_duration']} minutes\n\n")

        for campus in report["campus_comparison"]:
            avg = round(campus["avg_duration"], 1) if campus["avg_duration"] else 0
            self.report_text.insert(tk.END,
                                    f"  {campus['campus_name']}: {avg} minutes average\n")

        self.report_text.config(state=tk.DISABLED)

    def _build_comparison_tab(self):
        """Build cross-campus comparison view."""
        columns = ("campus", "total", "resources", "users", "avg_duration")
        self.comparison_tree = ttk.Treeview(self.comparison_tab, columns=columns,
                                             show="headings", height=10)

        self.comparison_tree.heading("campus", text="Campus")
        self.comparison_tree.heading("total", text="Total Bookings")
        self.comparison_tree.heading("resources", text="Unique Resources Used")
        self.comparison_tree.heading("users", text="Unique Users")
        self.comparison_tree.heading("avg_duration", text="Avg Duration (min)")

        self.comparison_tree.column("campus", width=180)
        self.comparison_tree.column("total", width=120)
        self.comparison_tree.column("resources", width=150)
        self.comparison_tree.column("users", width=100)
        self.comparison_tree.column("avg_duration", width=130)

        self.comparison_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        ttk.Button(self.comparison_tab, text="Refresh Comparison",
                   command=self._refresh_comparison, width=20).pack(pady=5)

        self._refresh_comparison()

    def _refresh_comparison(self):
        """Refresh cross-campus comparison data."""
        for item in self.comparison_tree.get_children():
            self.comparison_tree.delete(item)

        rs = ReportService()
        comparison = rs.get_cross_campus_comparison()
        rs.close()

        for c in comparison:
            avg = round(c["avg_duration"], 1) if c["avg_duration"] else 0
            self.comparison_tree.insert("", tk.END, values=(
                c["campus_name"], c["total_bookings"],
                c["unique_resources_used"], c["unique_users"], avg
            ))

    def _logout(self):
        """Logout."""
        self.frame.destroy()
        from gui.login_screen import LoginScreen
        LoginScreen(self.root)