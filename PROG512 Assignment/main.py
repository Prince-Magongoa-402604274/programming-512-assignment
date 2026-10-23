# main.py
"""
Smart Campus Resource Booking System
Entry point for the application.
Initializes the database and launches the GUI.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from gui.login_screen import LoginScreen
import tkinter as tk


def main():
    """Main entry point - initialize DB and launch application."""
    # Initialize the database and create all tables
    db = DatabaseManager()
    db.initialize_database()
    db.seed_default_data()
    db.close()

    # Launch the Tkinter application
    root = tk.Tk()
    root.title("Smart Campus Resource Booking System")
    root.geometry("900x650")
    root.resizable(True, True)

    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (900 // 2)
    y = (root.winfo_screenheight() // 2) - (650 // 2)
    root.geometry(f"900x650+{x}+{y}")

    # Start with the login screen
    app = LoginScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()