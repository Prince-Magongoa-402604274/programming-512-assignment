# gui/admin_dashboard.py
"""
Administrator Dashboard Module
Allows campus administrators to manage resources and view campus bookings.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.queries import QueryManager
from services.booking_service import BookingService
import uuid


class AdminDashboard:
    """Campus Administrator dashboard with resource management."""

    def __init__(self, root, user):
        """Initialize admin dashboard."""
        self.root = root
        self.user = user
        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        """Build the admin dashboard with tabs."""
        # Header
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text=f"Admin Dashboard - {self.user.full_name}",
                  font=("Helvetica", 14, "bold")).pack(side=tk.LEFT)

        btn_right = ttk.Frame(header_frame)
        btn_right.pack(side=tk.RIGHT)
        ttk.Button(btn_right, text="Back", command=self._back).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_right, text="Logout", command=self._logout).pack(side=tk.LEFT, padx=3)

        qm = QueryManager()
        campus = qm.get_campus_by_id(self.user.campus_id)
        qm.close()
        campus_name = campus["campus_name"] if campus else "Unknown"

        ttk.Label(self.frame, text=f"Campus: {campus_name}",
                  font=("Helvetica", 10)).pack(anchor=tk.W)

        # Notebook
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Tab 1: Manage Resources
        self.resources_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.resources_tab, text="Manage Resources")
        self._build_resources_tab()

        # Tab 2: Campus Bookings
        self.bookings_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.bookings_tab, text="Campus Bookings")
        self._build_bookings_tab()

    def _build_resources_tab(self):
        """Build resource management interface."""
        # Top: Add/Edit form
        form = ttk.LabelFrame(self.resources_tab, text="Add / Edit Resource", padding=10)
        form.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.res_name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.res_name_var, width=25).grid(
            row=0, column=1, pady=3, padx=(5, 10))

        ttk.Label(form, text="Type:").grid(row=0, column=2, sticky=tk.W, pady=3)
        self.res_type_var = tk.StringVar()
        type_combo = ttk.Combobox(form, textvariable=self.res_type_var, width=15, state="readonly")
        type_combo["values"] = ["Lecture Hall", "Lab", "Meeting Room", "Computer Lab",
                                 "Library Room", "Workshop", "Auditorium"]
        type_combo.grid(row=0, column=3, pady=3, padx=(5, 10))

        ttk.Label(form, text="Capacity:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.res_cap_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.res_cap_var, width=25).grid(
            row=1, column=1, pady=3, padx=(5, 10))

        ttk.Label(form, text="Description:").grid(row=1, column=2, sticky=tk.W, pady=3)
        self.res_desc_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.res_desc_var, width=18).grid(
            row=1, column=3, pady=3, padx=(5, 10))

        # Buttons
        btn_form = ttk.Frame(form)
        btn_form.grid(row=2, column=0, columnspan=4, pady=(8, 0))

        ttk.Button(btn_form, text="Add Resource", command=self._add_resource,
                   width=15).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_form, text="Update Selected", command=self._update_resource,
                   width=15).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_form, text="Remove Selected", command=self._remove_resource,
                   width=15).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_form, text="Clear Form", command=self._clear_form,
                   width=12).pack(side=tk.LEFT, padx=3)

        # Resources list
        columns = ("id", "uid", "name", "type", "capacity", "description")
        self.resources_tree = ttk.Treeview(self.resources_tab, columns=columns,
                                            show="headings", height=10)

        self.resources_tree.heading("id", text="ID")
        self.resources_tree.heading("uid", text="UID")
        self.resources_tree.heading("name", text="Name")
        self.resources_tree.heading("type", text="Type")
        self.resources_tree.heading("capacity", text="Capacity")
        self.resources_tree.heading("description", text="Description")

        self.resources_tree.column("id", width=40)
        self.resources_tree.column("uid", width=100)
        self.resources_tree.column("name", width=150)
        self.resources_tree.column("type", width=100)
        self.resources_tree.column("capacity", width=70)
        self.resources_tree.column("description", width=200)

        self.resources_tree.bind("<<TreeviewSelect>>", self._on_resource_select)

        scrollbar = ttk.Scrollbar(self.resources_tab, orient=tk.VERTICAL,
                                   command=self.resources_tree.yview)
        self.resources_tree.configure(yscrollcommand=scrollbar.set)
        self.resources_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self._refresh_resources()

    def _build_bookings_tab(self):
        """Build campus bookings view."""
        columns = ("id", "resource", "user", "date", "start", "end", "purpose")
        self.bookings_tree = ttk.Treeview(self.bookings_tab, columns=columns,
                                           show="headings", height=14)

        self.bookings_tree.heading("id", text="ID")
        self.bookings_tree.heading("resource", text="Resource")
        self.bookings_tree.heading("user", text="Booked By")
        self.bookings_tree.heading("date", text="Date")
        self.bookings_tree.heading("start", text="Start")
        self.bookings_tree.heading("end", text="End")
        self.bookings_tree.heading("purpose", text="Purpose")

        self.bookings_tree.column("id", width=40)
        self.bookings_tree.column("resource", width=130)
        self.bookings_tree.column("user", width=120)
        self.bookings_tree.column("date", width=90)
        self.bookings_tree.column("start", width=60)
        self.bookings_tree.column("end", width=60)
        self.bookings_tree.column("purpose", width=150)

        scrollbar = ttk.Scrollbar(self.bookings_tab, orient=tk.VERTICAL,
                                   command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)
        self.bookings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        # Refresh button
        ttk.Button(self.bookings_tab, text="Refresh",
                   command=self._refresh_bookings, width=12).pack(side=tk.RIGHT, anchor=tk.N, padx=10)

        self._refresh_bookings()

    def _refresh_resources(self):
        """Refresh the resources treeview."""
        for item in self.resources_tree.get_children():
            self.resources_tree.delete(item)

        qm = QueryManager()
        resources = qm.get_resources_by_campus(self.user.campus_id)
        qm.close()

        for r in resources:
            self.resources_tree.insert("", tk.END, values=(
                r["resource_id"], r["resource_uid"], r["resource_name"],
                r["resource_type"], r["capacity"], r["description"] or ""
            ))

    def _refresh_bookings(self):
        """Refresh the bookings treeview."""
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)

        bs = BookingService()
        bookings = bs.get_campus_bookings(self.user.campus_id)
        bs.close()

        for b in bookings:
            self.bookings_tree.insert("", tk.END, values=(
                b["booking_id"], b["resource_name"], b["full_name"],
                b["booking_date"], b["start_time"], b["end_time"],
                b["purpose"] or ""
            ))

    def _on_resource_select(self, event):
        """Populate form when a resource is selected."""
        selected = self.resources_tree.selection()
        if selected:
            item = self.resources_tree.item(selected[0])
            values = item["values"]
            self.res_name_var.set(values[2])
            self.res_type_var.set(values[3])
            self.res_cap_var.set(str(values[4]))
            self.res_desc_var.set(values[5])

    def _add_resource(self):
        """Add a new resource."""
        name = self.res_name_var.get().strip()
        res_type = self.res_type_var.get().strip()
        cap_str = self.res_cap_var.get().strip()
        desc = self.res_desc_var.get().strip()

        if not name:
            messagebox.showwarning("Validation", "Resource name is required.")
            return
        if not res_type:
            messagebox.showwarning("Validation", "Resource type is required.")
            return

        try:
            capacity = int(cap_str) if cap_str else 0
            if capacity < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Capacity must be a non-negative number.")
            return

        # Generate unique ID
        resource_uid = f"RES-{uuid.uuid4().hex[:8].upper()}"

        qm = QueryManager()
        result = qm.add_resource(resource_uid, name, res_type, self.user.campus_id,
                                  capacity, desc)
        qm.close()

        if result:
            messagebox.showinfo("Success", f"Resource added with UID: {resource_uid}")
            self._clear_form()
            self._refresh_resources()
        else:
            messagebox.showerror("Error", "Failed to add resource. UID may already exist.")

    def _update_resource(self):
        """Update the selected resource."""
        selected = self.resources_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a resource to update.")
            return

        item = self.resources_tree.item(selected[0])
        resource_id = item["values"][0]

        name = self.res_name_var.get().strip()
        res_type = self.res_type_var.get().strip()
        cap_str = self.res_cap_var.get().strip()
        desc = self.res_desc_var.get().strip()

        if not name:
            messagebox.showwarning("Validation", "Resource name is required.")
            return
        if not res_type:
            messagebox.showwarning("Validation", "Resource type is required.")
            return

        try:
            capacity = int(cap_str) if cap_str else 0
            if capacity < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Capacity must be a non-negative number.")
            return

        qm = QueryManager()
        success = qm.update_resource(resource_id, name, res_type, capacity, desc)
        qm.close()

        if success:
            messagebox.showinfo("Success", "Resource updated successfully.")
            self._refresh_resources()
        else:
            messagebox.showerror("Error", "Failed to update resource.")

    def _remove_resource(self):
        """Remove (soft-delete) the selected resource."""
        selected = self.resources_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a resource to remove.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to remove this resource?"):
            item = self.resources_tree.item(selected[0])
            resource_id = item["values"][0]

            qm = QueryManager()
            success = qm.remove_resource(resource_id)
            qm.close()

            if success:
                messagebox.showinfo("Success", "Resource removed successfully.")
                self._clear_form()
                self._refresh_resources()
            else:
                messagebox.showerror("Error", "Failed to remove resource.")

    def _clear_form(self):
        """Clear the resource form fields."""
        self.res_name_var.set("")
        self.res_type_var.set("")
        self.res_cap_var.set("")
        self.res_desc_var.set("")

    def _back(self):
        """Go back to campus selection."""
        self.frame.destroy()
        from gui.campus_selection import CampusSelectionScreen
        CampusSelectionScreen(self.root, self.user)

    def _logout(self):
        """Logout."""
        self.frame.destroy()
        from gui.login_screen import LoginScreen
        LoginScreen(self.root)