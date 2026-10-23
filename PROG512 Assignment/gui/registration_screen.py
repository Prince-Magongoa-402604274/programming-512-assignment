# gui/registration_screen.py
"""
Registration Screen Module
Allows new users to create an account.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from services.auth_service import AuthService
from database.queries import QueryManager


class RegistrationScreen:
    """Registration form GUI."""

    def __init__(self, root):
        """Initialize registration screen."""
        self.root = root
        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self._load_campuses()
        self._build_ui()

    def _load_campuses(self):
        """Load available campuses from database."""
        qm = QueryManager()
        self.campuses = qm.get_all_campuses()
        qm.close()

    def _build_ui(self):
        """Build the registration form."""
        # Title
        title = ttk.Label(self.frame, text="Create New Account",
                          font=("Helvetica", 18, "bold"))
        title.pack(pady=(10, 20))

        # Form frame
        form_frame = ttk.LabelFrame(self.frame, text="Registration Details", padding=15)
        form_frame.pack(padx=80, fill=tk.X)

        row = 0

        # Username
        ttk.Label(form_frame, text="Username*:").grid(row=row, column=0, sticky=tk.W, pady=4)
        self.username_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.username_var, width=30).grid(
            row=row, column=1, pady=4, padx=(10, 0))

        row += 1

        # Full Name
        ttk.Label(form_frame, text="Full Name*:").grid(row=row, column=0, sticky=tk.W, pady=4)
        self.fullname_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.fullname_var, width=30).grid(
            row=row, column=1, pady=4, padx=(10, 0))

        row += 1

        # Email
        ttk.Label(form_frame, text="Email*:").grid(row=row, column=0, sticky=tk.W, pady=4)
        self.email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.email_var, width=30).grid(
            row=row, column=1, pady=4, padx=(10, 0))

        row += 1

        # Password
        ttk.Label(form_frame, text="Password*:").grid(row=row, column=0, sticky=tk.W, pady=4)
        self.password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=30).grid(
            row=row, column=1, pady=4, padx=(10, 0))

        row += 1

        # Confirm Password
        ttk.Label(form_frame, text="Confirm Password*:").grid(row=row, column=0, sticky=tk.W, pady=4)
        self.confirm_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.confirm_var, show="*", width=30).grid(
            row=row, column=1, pady=4, padx=(10, 0))

        row += 1

        # Role
        ttk.Label(form_frame, text="Role*:").grid(row=row, column=0, sticky=tk.W, pady=4)
        self.role_var = tk.StringVar()
        role_combo = ttk.Combobox(form_frame, textvariable=self.role_var, width=27,
                                   state="readonly")
        role_combo["values"] = ["lecturer", "administrator", "operator"]
        role_combo.grid(row=row, column=1, pady=4, padx=(10, 0))
        role_combo.bind("<<ComboboxSelected>>", self._on_role_change)

        row += 1

        # Campus
        ttk.Label(form_frame, text="Campus*:").grid(row=row, column=0, sticky=tk.W, pady=4)
        self.campus_var = tk.StringVar()
        self.campus_combo = ttk.Combobox(form_frame, textvariable=self.campus_var, width=27,
                                          state="readonly")
        campus_names = [c["campus_name"] for c in self.campuses]
        self.campus_combo["values"] = campus_names
        self.campus_combo.grid(row=row, column=1, pady=4, padx=(10, 0))

        row += 1

        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=(15, 5))

        ttk.Button(btn_frame, text="Register", command=self._handle_register, width=15).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Back to Login", command=self._back_to_login, width=15).pack(
            side=tk.LEFT, padx=5)

    def _on_role_change(self, event):
        """Enable/disable campus selection based on role."""
        if self.role_var.get() == "operator":
            self.campus_combo.set("")
            self.campus_combo.config(state="disabled")
        else:
            self.campus_combo.config(state="readonly")

    def _handle_register(self):
        """Process registration."""
        role = self.role_var.get()
        campus_id = None

        if role != "operator":
            # Find campus ID from selected name
            campus_name = self.campus_var.get()
            for c in self.campuses:
                if c["campus_name"] == campus_name:
                    campus_id = c["campus_id"]
                    break

        auth = AuthService()
        success, message = auth.register(
            self.username_var.get(),
            self.password_var.get(),
            self.confirm_var.get(),
            self.fullname_var.get(),
            self.email_var.get(),
            role,
            campus_id
        )
        auth.close()

        if success:
            messagebox.showinfo("Success", message)
            self._back_to_login()
        else:
            messagebox.showerror("Registration Error", message)

    def _back_to_login(self):
        """Return to login screen."""
        self.frame.destroy()
        from gui.login_screen import LoginScreen
        LoginScreen(self.root)