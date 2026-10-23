# gui/lecturer_dashboard.py
"""
Lecturer Dashboard Module
Allows lecturers to book resources, view bookings, and cancel bookings.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from services.booking_service import BookingService
from database.queries import QueryManager
from policies.booking_policies import PolicyFactory


class LecturerDashboard:
    """Lecturer dashboard with booking management."""

    def __init__(self, root, user):
        """Initialize lecturer dashboard."""
        self.root = root
        self.user = user
        self.booking_service = BookingService()
        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        """Build the lecturer dashboard UI with tabbed interface."""
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text=f"Lecturer Dashboard - {self.user.full_name}",
                  font=("Helvetica", 14, "bold")).pack(side=tk.LEFT)

        btn_right = ttk.Frame(header_frame)
        btn_right.pack(side=tk.RIGHT)
        ttk.Button(btn_right, text="Back", command=self._back).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_right, text="Logout", command=self._logout).pack(side=tk.LEFT, padx=3)

        # Get campus name
        qm = QueryManager()
        campus = qm.get_campus_by_id(self.user.campus_id)
        qm.close()
        campus_name = campus["campus_name"] if campus else "Unknown"

        ttk.Label(self.frame, text=f"Campus: {campus_name}",
                  font=("Helvetica", 10)).pack(anchor=tk.W)

        # Notebook (tabs)
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tab 1: Book Resource
        self.book_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.book_tab, text="Book Resource")
        self._build_booking_form()

        # Tab 2: My Bookings
        self.bookings_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.bookings_tab, text="My Bookings")
        self._build_bookings_view()

    def _build_booking_form(self):
        """Build the resource booking form."""
        form = ttk.LabelFrame(self.book_tab, text="New Booking", padding=10)
        form.pack(fill=tk.X, pady=5)

        # Resource selection
        ttk.Label(form, text="Resource:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.resource_var = tk.StringVar()
        self.resource_combo = ttk.Combobox(form, textvariable=self.resource_var,
                                            width=35, state="readonly")
        self.resource_combo.grid(row=0, column=1, pady=4, padx=(10, 0))

        # Load resources
        self._resources = self.booking_service.get_resources_for_campus(self.user.campus_id)
        resource_names = [f"{r['resource_uid']} - {r['resource_name']} ({r['resource_type']})"
                         for r in self._resources]
        self.resource_combo["values"] = resource_names

        # Date
        ttk.Label(form, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.date_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.date_var, width=37).grid(
            row=1, column=1, pady=4, padx=(10, 0))

        # Start Time
        ttk.Label(form, text="Start Time (HH:MM):").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.start_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.start_var, width=37).grid(
            row=2, column=1, pady=4, padx=(10, 0))

        # End Time
        ttk.Label(form, text="End Time (HH:MM):").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.end_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.end_var, width=37).grid(
            row=3, column=1, pady=4, padx=(10, 0))

        # Purpose
        ttk.Label(form, text="Purpose:").grid(row=4, column=0, sticky=tk.W, pady=4)
        self.purpose_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.purpose_var, width=37).grid(
            row=4, column=1, pady=4, padx=(10, 0))

        # Submit button
        ttk.Button(form, text="Book Now", command=self._submit_booking,
                   width=20).grid(row=5, column=0, columnspan=2, pady=(10, 0))

        # Policy info
        policy = self.booking_service.get_campus_policy(self.user.campus_id)
        policy_lbl = ttk.LabelFrame(self.book_tab, text="Campus Booking Policy", padding=10)
        policy_lbl.pack(fill=tk.X, pady=10)
        ttk.Label(policy_lbl, text=policy.get_policy_info(),
                  font=("Courier", 9), justify=tk.LEFT).pack(anchor=tk.W)

    def _build_bookings_view(self):
        """Build the view showing user's bookings."""
        # Treeview for bookings
        columns = ("id", "resource", "date", "start", "end", "campus", "purpose")
        self.bookings_tree = ttk.Treeview(self.bookings_tab, columns=columns,
                                           show="headings", height=12)

        self.bookings_tree.heading("id", text="ID")
        self.bookings_tree.heading("resource", text="Resource")
        self.bookings_tree.heading("date", text="Date")
        self.bookings_tree.heading("start", text="Start")
        self.bookings_tree.heading("end", text="End")
        self.bookings_tree.heading("campus", text="Campus")
        self.bookings_tree.heading("purpose", text="Purpose")

        self.bookings_tree.column("id", width=40)
        self.bookings_tree.column("resource", width=150)
        self.bookings_tree.column("date", width=90)
        self.bookings_tree.column("start", width=60)
        self.bookings_tree.column("end", width=60)
        self.bookings_tree.column("campus", width=120)
        self.bookings_tree.column("purpose", width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.bookings_tab, orient=tk.VERTICAL,
                                   command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)

        self.bookings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        # Buttons
        btn_frame = ttk.Frame(self.bookings_tab)
        btn_frame.pack(side=tk.RIGHT, padx=10, anchor=tk.N)

        ttk.Button(btn_frame, text="Refresh", command=self._refresh_bookings,
                   width=15).pack(pady=5)
        ttk.Button(btn_frame, text="Cancel Booking", command=self._cancel_booking,
                   width=15).pack(pady=5)

        # Load bookings
        self._refresh_bookings()

    def _submit_booking(self):
        """Submit a new booking."""
        # Get selected resource
        idx = self.resource_combo.current()
        if idx < 0:
            messagebox.showwarning("Validation", "Please select a resource.")
            return

        resource = self._resources[idx]

        success, message = self.booking_service.create_booking(
            resource["resource_id"],
            self.user.user_id,
            self.user.campus_id,
            self.date_var.get().strip(),
            self.start_var.get().strip(),
            self.end_var.get().strip(),
            self.purpose_var.get().strip()
        )

        if success:
            messagebox.showinfo("Success", message)
            # Clear form
            self.date_var.set("")
            self.start_var.set("")
            self.end_var.set("")
            self.purpose_var.set("")
            self.resource_combo.set("")
            self._refresh_bookings()
        else:
            messagebox.showerror("Booking Error", message)

    def _refresh_bookings(self):
        """Refresh the bookings treeview."""
        # Clear existing items
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)

        # Reload bookings - need fresh connection
        bs = BookingService()
        bookings = bs.get_user_bookings(self.user.user_id)
        bs.close()

        for b in bookings:
            self.bookings_tree.insert("", tk.END, values=(
                b["booking_id"], b["resource_name"],
                b["booking_date"], b["start_time"], b["end_time"],
                b["campus_name"], b["purpose"] or ""
            ))

    def _cancel_booking(self):
        """Cancel the selected booking."""
        selected = self.bookings_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a booking to cancel.")
            return

        item = self.bookings_tree.item(selected[0])
        booking_id = item["values"][0]

        if messagebox.askyesno("Confirm", "Are you sure you want to cancel this booking?"):
            bs = BookingService()
            success, message = bs.cancel_booking(booking_id, self.user.user_id)
            bs.close()

            if success:
                messagebox.showinfo("Success", message)
                self._refresh_bookings()
            else:
                messagebox.showerror("Error", message)

    def _back(self):
        """Go back to campus selection."""
        self.booking_service.close()
        self.frame.destroy()
        from gui.campus_selection import CampusSelectionScreen
        CampusSelectionScreen(self.root, self.user)

    def _logout(self):
        """Logout and return to login screen."""
        self.booking_service.close()
        self.frame.destroy()
        from gui.login_screen import LoginScreen
        LoginScreen(self.root)