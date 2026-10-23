# gui/campus_selection.py
"""
Campus Selection Screen Module
Shows the user's active campus and its booking policy.
"""

import tkinter as tk
from tkinter import ttk
from database.queries import QueryManager
from policies.booking_policies import PolicyFactory


class CampusSelectionScreen:
    """Campus selection and policy information screen."""

    def __init__(self, root, user):
        """Initialize campus selection for the logged-in user."""
        self.root = root
        self.user = user
        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        """Build the campus selection UI."""
        # Header
        header = ttk.Label(self.frame,
                           text=f"Welcome, {self.user.full_name}",
                           font=("Helvetica", 16, "bold"))
        header.pack(pady=(10, 5))

        role_label = ttk.Label(self.frame,
                               text=f"Role: {self.user.role.title()}",
                               font=("Helvetica", 11))
        role_label.pack(pady=(0, 15))

        # Load campus info
        qm = QueryManager()
        campus = qm.get_campus_by_id(self.user.campus_id)
        campuses = qm.get_all_campuses()
        qm.close()

        if campus:
            # Campus info frame
            campus_frame = ttk.LabelFrame(self.frame, text="Your Campus", padding=15)
            campus_frame.pack(padx=60, fill=tk.X, pady=5)

            ttk.Label(campus_frame, text=f"Campus: {campus['campus_name']}",
                      font=("Helvetica", 12, "bold")).pack(anchor=tk.W)
            ttk.Label(campus_frame, text=f"Location: {campus['location']}").pack(anchor=tk.W)
            ttk.Label(campus_frame, text=f"Policy Type: {campus['policy_type'].replace('_', ' ').title()}").pack(
                anchor=tk.W)

            # Policy details
            policy = PolicyFactory.get_policy(campus["policy_type"])
            policy_frame = ttk.LabelFrame(self.frame, text="Booking Policy Details", padding=15)
            policy_frame.pack(padx=60, fill=tk.X, pady=10)

            policy_text = tk.Text(policy_frame, height=7, width=50, wrap=tk.WORD,
                                   font=("Courier", 10))
            policy_text.insert(tk.END, policy.get_policy_info())
            policy_text.config(state=tk.DISABLED)
            policy_text.pack(fill=tk.X)

        # All campuses overview
        all_frame = ttk.LabelFrame(self.frame, text="All Campuses", padding=10)
        all_frame.pack(padx=60, fill=tk.BOTH, expand=True, pady=5)

        columns = ("name", "location", "policy")
        tree = ttk.Treeview(all_frame, columns=columns, show="headings", height=4)
        tree.heading("name", text="Campus Name")
        tree.heading("location", text="Location")
        tree.heading("policy", text="Policy Type")
        tree.column("name", width=180)
        tree.column("location", width=200)
        tree.column("policy", width=150)

        for c in campuses:
            tag = "active" if campus and c["campus_id"] == campus["campus_id"] else ""
            tree.insert("", tk.END, values=(
                c["campus_name"], c["location"],
                c["policy_type"].replace("_", " ").title()
            ), tags=(tag,))

        tree.tag_configure("active", background="#d4edda")
        tree.pack(fill=tk.BOTH, expand=True)

        # Button to proceed to dashboard
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="Go to Dashboard", command=self._go_to_dashboard,
                   width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Logout", command=self._logout,
                   width=15).pack(side=tk.LEFT, padx=5)

    def _go_to_dashboard(self):
        """Navigate to the appropriate role-based dashboard."""
        self.frame.destroy()

        if self.user.role == "lecturer":
            from gui.lecturer_dashboard import LecturerDashboard
            LecturerDashboard(self.root, self.user)
        elif self.user.role == "administrator":
            from gui.admin_dashboard import AdminDashboard
            AdminDashboard(self.root, self.user)
        elif self.user.role == "operator":
            from gui.operator_dashboard import OperatorDashboard
            OperatorDashboard(self.root, self.user)

    def _logout(self):
        """Return to login screen."""
        self.frame.destroy()
        from gui.login_screen import LoginScreen
        LoginScreen(self.root)