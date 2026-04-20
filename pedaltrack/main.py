"""
PedalTrack — Bike Rental Management System
Run this file to start the application.
  python main.py

Default login: admin / admin1234
"""

import tkinter as tk
from app import App

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
