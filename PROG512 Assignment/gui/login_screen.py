# gui/login_screen.py
"""
Login Screen Module
Provides the login interface for the Smart Campus Booking System.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from services.auth_service import AuthService


class LoginScreen:
    """Login screen GUI using Tkinter."""

    def __init__(self, root):
        """Initialize the login screen."""
        self.root = root
        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self._build_ui()

    def _build_ui(self):
        """Build the login form UI."""
        # Clear frame
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Title
        title_label = ttk.Label(
            self.frame, text="Smart Campus\nResource Booking System",
            font=("Helvetica", 20, "bold"), justify=tk.CENTER
        )
        title_label.pack(pady=(30, 10))

        subtitle = ttk.Label(
            self.frame, text="Please log in to continue",
            font=("Helvetica", 11)
        )
        subtitle.pack(pady=(0, 30))

        # Login form frame
        form_frame = ttk.LabelFrame(self.frame, text="Login", padding=20)
        form_frame.pack(padx=100, fill=tk.X)

        # Username
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=self.username_var, width=30)
        username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        username_entry.focus()

        # Password
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=30)
        password_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        # Bind Enter key
        password_entry.bind("<Return>", lambda e: self._handle_login())

        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0))

        login_btn = ttk.Button(btn_frame, text="Login", command=self._handle_login, width=15)
        login_btn.pack(side=tk.LEFT, padx=5)

        register_btn = ttk.Button(btn_frame, text="Register", command=self._show_register, width=15)
        register_btn.pack(side=tk.LEFT, padx=5)

        # Info label
        info_label = ttk.Label(
            self.frame,
            text="Default operator: username='operator', password='admin123'",
            font=("Helvetica", 9), foreground="gray"
        )
        info_label.pack(pady=(20, 0))

    def _handle_login(self):
        """Process the login attempt."""
        username = self.username_var.get()
        password = self.password_var.get()

        auth = AuthService()
        user, message = auth.login(username, password)
        auth.close()

        if user is None:
            messagebox.showerror("Login Failed", message)
            return

        messagebox.showinfo("Welcome", f"Welcome, {user.full_name}!")

        # Navigate to campus selection or dashboard based on role
        self.frame.destroy()

        if user.role == "operator":
            from gui.operator_dashboard import OperatorDashboard
            OperatorDashboard(self.root, user)
        else:
            from gui.campus_selection import CampusSelectionScreen
            CampusSelectionScreen(self.root, user)

    def _show_register(self):
        """Switch to registration screen."""
        self.frame.destroy()
        from gui.registration_screen import RegistrationScreen
        RegistrationScreen(self.root)