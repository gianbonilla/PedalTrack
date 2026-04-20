import tkinter as tk
from components.widgets import C

NAV_ITEMS = [
    ("dashboard",   "Dashboard",   "⬛"),
    ("customers",   "Customers",   "👤"),
    ("bikes",       "Bikes",       "⊙"),
    ("rentals",     "Rentals",     "⊞"),
    ("payments",    "Payments",    "₱"),
    ("maintenance", "Maintenance", "⚙"),
    ("staff",       "Staff",       "⊕"),
]

ADMIN_ONLY = {"staff"}


class Sidebar(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["sidebar_bg"], width=190)
        self.pack_propagate(False)
        self.app = app
        self._buttons = {}
        self._build()

    def _build(self):
        # Logo
        logo = tk.Frame(self, bg=C["sidebar_bg"])
        logo.pack(fill="x", pady=(20, 4), padx=18)
        tk.Label(logo, text="PedalTrack", font=("Georgia", 15, "bold"),
                 bg=C["sidebar_bg"], fg="#F0EFEA").pack(anchor="w")
        tk.Label(logo, text="Bike Rental System", font=("Helvetica Neue", 10),
                 bg=C["sidebar_bg"], fg=C["sidebar_text"]).pack(anchor="w")

        tk.Frame(self, height=1, bg="#2C2C28").pack(fill="x", padx=18, pady=(10, 14))

        # Nav items
        nav = tk.Frame(self, bg=C["sidebar_bg"])
        nav.pack(fill="x")

        role = self.app.current_staff.get("role", "cashier") if self.app.current_staff else ""

        for key, label, icon in NAV_ITEMS:
            if key in ADMIN_ONLY and role != "admin":
                continue
            btn = tk.Button(nav,
                text=f"  {label}",
                font=("Helvetica Neue", 12),
                bg=C["sidebar_bg"], fg=C["sidebar_text"],
                activebackground=C["sidebar_active_bg"],
                activeforeground=C["sidebar_active_txt"],
                relief="flat", bd=0,
                anchor="w", padx=14, pady=9,
                cursor="hand2",
                command=lambda k=key: self.app.navigate(k))
            btn.pack(fill="x")
            self._buttons[key] = btn

        # Spacer
        tk.Frame(self, bg=C["sidebar_bg"]).pack(fill="both", expand=True)

        # Divider
        tk.Frame(self, height=1, bg="#2C2C28").pack(fill="x", padx=18, pady=(0, 10))

        # Staff info + logout
        info = tk.Frame(self, bg=C["sidebar_bg"])
        info.pack(fill="x", padx=14, pady=(0, 16))

        if self.app.current_staff:
            s = self.app.current_staff
            name = f"{s['first_name']} {s['last_name']}"
            role_disp = s["role"].title()
            tk.Label(info, text=name, font=("Helvetica Neue", 11, "bold"),
                     bg=C["sidebar_bg"], fg="#D0CFC8",
                     anchor="w").pack(anchor="w")
            tk.Label(info, text=role_disp, font=("Helvetica Neue", 10),
                     bg=C["sidebar_bg"], fg=C["sidebar_text"],
                     anchor="w").pack(anchor="w", pady=(0, 6))

        tk.Button(info, text="Sign out",
                  font=("Helvetica Neue", 10),
                  bg=C["sidebar_bg"], fg=C["sidebar_text"],
                  activebackground=C["sidebar_active_bg"],
                  activeforeground="#F0EFEA",
                  relief="flat", bd=0, anchor="w",
                  cursor="hand2",
                  command=self.app.logout).pack(anchor="w")

    def set_active(self, key: str):
        for k, btn in self._buttons.items():
            if k == key:
                btn.configure(bg=C["sidebar_active_bg"], fg=C["sidebar_active_txt"])
            else:
                btn.configure(bg=C["sidebar_bg"], fg=C["sidebar_text"])
