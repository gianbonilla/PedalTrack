"""
App root — initializes the window, applies the theme, and controls navigation.
"""

import tkinter as tk
from tkinter import ttk


COLORS = {
    "bg":                "#F7F6F2",
    "surface":           "#FFFFFF",
    "sidebar_bg":        "#1A1A18",
    "sidebar_text":      "#A8A89E",
    "sidebar_active_bg": "#2C2C28",
    "sidebar_active_txt":"#F0EFEA",
    "accent":            "#2D6A4F",
    "accent_light":      "#D8F3DC",
    "accent_text":       "#1B4332",
    "text":              "#1C1C1A",
    "text_muted":        "#6B6B63",
    "text_hint":         "#A8A89E",
    "border":            "#E8E6E0",
    "danger":            "#C0392B",
    "danger_light":      "#FDECEA",
    "warning":           "#B7770D",
    "warning_light":     "#FEF3C7",
    "success":           "#1B7A4A",
    "success_light":     "#D1FAE5",
    "info":              "#1E5EA8",
    "info_light":        "#DBEAFE",
    "row_alt":           "#FAFAF8",
}


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PedalTrack — Bike Rental")
        self.root.geometry("1120x700")
        self.root.minsize(960, 620)
        self.root.configure(bg=COLORS["bg"])

        from db.database import Database
        from db.seed import seed_database
        self.db = Database()
        seed_database(self.db)

        self.current_staff = None
        self.current_view = None
        self.sidebar = None
        self.content_frame = None

        self._setup_styles()
        self._show_login()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame",         background=COLORS["bg"])
        style.configure("Surface.TFrame", background=COLORS["surface"])

        style.configure("TLabel",
            background=COLORS["bg"], foreground=COLORS["text"],
            font=("Helvetica Neue", 12))
        style.configure("Surface.TLabel",
            background=COLORS["surface"], foreground=COLORS["text"],
            font=("Helvetica Neue", 12))
        style.configure("Muted.TLabel",
            background=COLORS["surface"], foreground=COLORS["text_muted"],
            font=("Helvetica Neue", 11))

        style.configure("Accent.TButton",
            background=COLORS["accent"], foreground="#FFFFFF",
            font=("Helvetica Neue", 11, "bold"),
            borderwidth=0, focusthickness=0, padding=(14, 8))
        style.map("Accent.TButton",
            background=[("active", COLORS["accent_text"])])

        style.configure("Ghost.TButton",
            background=COLORS["surface"], foreground=COLORS["text"],
            font=("Helvetica Neue", 11), borderwidth=1,
            relief="solid", padding=(12, 7))
        style.map("Ghost.TButton",
            background=[("active", COLORS["bg"])])

        style.configure("Treeview",
            background=COLORS["surface"], foreground=COLORS["text"],
            fieldbackground=COLORS["surface"],
            font=("Helvetica Neue", 12), rowheight=34, borderwidth=0)
        style.configure("Treeview.Heading",
            background=COLORS["bg"], foreground=COLORS["text_muted"],
            font=("Helvetica Neue", 11, "bold"), borderwidth=0, relief="flat")
        style.map("Treeview",
            background=[("selected", COLORS["accent_light"])],
            foreground=[("selected", COLORS["accent_text"])])

        style.configure("TEntry",
            fieldbackground=COLORS["surface"], foreground=COLORS["text"],
            font=("Helvetica Neue", 12), padding=(8, 6))
        style.configure("TCombobox",
            fieldbackground=COLORS["surface"], foreground=COLORS["text"],
            font=("Helvetica Neue", 12), padding=(8, 6))
        style.configure("TScrollbar",
            background=COLORS["border"], troughcolor=COLORS["bg"],
            borderwidth=0, arrowsize=12)

    def _show_login(self):
        for w in self.root.winfo_children():
            w.destroy()
        from views.login_view import LoginView
        LoginView(self.root, self)

    def login(self, staff: dict):
        self.current_staff = staff
        self._build_main_layout()
        self.navigate("dashboard")

    def logout(self):
        self.current_staff = None
        self._show_login()

    def _build_main_layout(self):
        for w in self.root.winfo_children():
            w.destroy()
        wrapper = tk.Frame(self.root, bg=COLORS["sidebar_bg"])
        wrapper.pack(fill="both", expand=True)

        from components.sidebar import Sidebar
        self.sidebar = Sidebar(wrapper, self)
        self.sidebar.pack(side="left", fill="y")

        self.content_frame = tk.Frame(wrapper, bg=COLORS["bg"])
        self.content_frame.pack(side="left", fill="both", expand=True)

    def navigate(self, view_name: str):
        if self.content_frame is None:
            return
        for w in self.content_frame.winfo_children():
            w.destroy()

        from views.dashboard_view   import DashboardView
        from views.customers_view   import CustomersView
        from views.bikes_view       import BikesView
        from views.rentals_view     import RentalsView
        from views.payments_view    import PaymentsView
        from views.maintenance_view import MaintenanceView
        from views.staff_view       import StaffView

        views = {
            "dashboard":   DashboardView,
            "customers":   CustomersView,
            "bikes":       BikesView,
            "rentals":     RentalsView,
            "payments":    PaymentsView,
            "maintenance": MaintenanceView,
            "staff":       StaffView,
        }
        cls = views.get(view_name)
        if cls:
            self.current_view = cls(self.content_frame, self)
            self.current_view.pack(fill="both", expand=True)
        if self.sidebar:
            self.sidebar.set_active(view_name)
