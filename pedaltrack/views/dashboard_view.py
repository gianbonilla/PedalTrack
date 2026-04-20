import tkinter as tk
from tkinter import ttk
from components.widgets import C, stat_card, hsep, build_tree, accent_btn


class DashboardView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()

    def _build(self):
        pad = tk.Frame(self, bg=C["bg"])
        pad.pack(fill="both", expand=True, padx=28, pady=24)

        # Header
        hdr = tk.Frame(pad, bg=C["bg"])
        hdr.pack(fill="x", pady=(0, 20))
        s = self.app.current_staff
        greeting = f"Welcome back, {s['first_name']}." if s else "Dashboard"
        tk.Label(hdr, text=greeting, font=("Georgia", 16, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(anchor="w")
        tk.Label(hdr, text="Here's what's happening today.",
                 font=("Helvetica Neue", 11),
                 bg=C["bg"], fg=C["text_muted"]).pack(anchor="w")

        # Stat cards
        stats = self.app.db.get_dashboard_stats()
        cards_frame = tk.Frame(pad, bg=C["bg"])
        cards_frame.pack(fill="x", pady=(0, 24))
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)

        items = [
            ("Active rentals",  str(stats["active_rentals"]), C["info"]),
            ("Bikes available", str(stats["bikes_available"]),C["success"]),
            ("Overdue",         str(stats["overdue"]),        C["danger"]),
            ("Revenue today",   f"₱{stats['revenue_today']:.0f}", C["text"]),
        ]
        for i, (lbl, val, col) in enumerate(items):
            card = stat_card(cards_frame, lbl, val, col)
            card.grid(row=0, column=i, sticky="ew", padx=(0, 10 if i < 3 else 0), ipady=2)

        # Active rentals table
        row_hdr = tk.Frame(pad, bg=C["bg"])
        row_hdr.pack(fill="x", pady=(0, 8))
        tk.Label(row_hdr, text="Active rentals", font=("Georgia", 13, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(side="left")
        accent_btn(row_hdr, "+ New rental",
                   lambda: self.app.navigate("rentals")).pack(side="right")

        # Treeview
        cols = ("customer", "bike", "started", "status")
        table_frame = tk.Frame(pad, bg=C["surface"],
                               highlightthickness=1, highlightbackground=C["border"])
        table_frame.pack(fill="both", expand=True)

        tree, sb = build_tree(table_frame, cols)
        tree.heading("customer", text="Customer")
        tree.heading("bike",     text="Bike")
        tree.heading("started",  text="Started")
        tree.heading("status",   text="Status")
        tree.column("customer", width=200)
        tree.column("bike",     width=160)
        tree.column("started",  width=140)
        tree.column("status",   width=100)

        rentals = self.app.db.get_active_rentals()
        for i, r in enumerate(rentals):
            tag = "alt" if i % 2 else ""
            tree.insert("", "end", values=(
                r["customer_name"],
                f"{r['bike_code']} · {r['brand']} {r['model']}",
                r["rental_start"][:16],
                r["status"].title()
            ), tags=(tag,))

        if not rentals:
            tree.insert("", "end", values=("No active rentals", "", "", ""))

        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
