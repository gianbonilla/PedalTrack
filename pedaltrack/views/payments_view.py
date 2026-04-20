import tkinter as tk
from tkinter import ttk
from datetime import date
from components.widgets import C, build_tree, stat_card


class PaymentsView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()
        self._load()

    def _build(self):
        pad = tk.Frame(self, bg=C["bg"])
        pad.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(pad, text="Payments", font=("Georgia", 16, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(anchor="w", pady=(0, 16))

        cf = tk.Frame(pad, bg=C["bg"])
        cf.pack(fill="x", pady=(0, 16))
        for i in range(3):
            cf.columnconfigure(i, weight=1)

        self._c_total = stat_card(cf, "Total collected", "₱0",   C["success"])
        self._c_count = stat_card(cf, "Transactions",    "0",    C["text"])
        self._c_today = stat_card(cf, "Today's revenue", "₱0",   C["info"])
        self._c_total.grid(row=0, column=0, sticky="ew", padx=(0,10))
        self._c_count.grid(row=0, column=1, sticky="ew", padx=(0,10))
        self._c_today.grid(row=0, column=2, sticky="ew")

        cols = ("pid","customer","bike","amount","method","status","date")
        tf = tk.Frame(pad, bg=C["surface"],
                      highlightthickness=1, highlightbackground=C["border"])
        tf.pack(fill="both", expand=True)

        self.tree, sb = build_tree(tf, cols)
        for col, txt, w, st in [
            ("pid","#",50,False),("customer","Customer",180,True),
            ("bike","Bike",110,False),("amount","Amount",90,False),
            ("method","Method",90,False),("status","Status",90,False),
            ("date","Date",140,False)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, stretch=st)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self._stat_labels = {}
        for card, key in [(self._c_total,"total"),(self._c_count,"count"),(self._c_today,"today")]:
            for w in card.winfo_children():
                if isinstance(w, tk.Label):
                    try:
                        f = w.cget("font")
                        if "Georgia" in str(f):
                            self._stat_labels[key] = w
                    except Exception:
                        pass

    def _load(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        payments = self.app.db.get_all_payments()
        total = today_total = 0.0
        today_str = date.today().strftime("%Y-%m-%d")
        for i, p in enumerate(payments):
            amt = float(p["amount_paid"])
            total += amt
            if p["payment_date"][:10] == today_str:
                today_total += amt
            tag = "alt" if i % 2 else ""
            self.tree.insert("", "end", values=(
                p["payment_id"], p["customer_name"], p["bike_code"],
                f"₱{amt:.0f}", p["payment_method"].title(),
                p["payment_status"].title(), p["payment_date"][:16]
            ), tags=(tag,))
        if "total" in self._stat_labels:
            self._stat_labels["total"].config(text=f"₱{total:.0f}")
        if "count" in self._stat_labels:
            self._stat_labels["count"].config(text=str(len(payments)))
        if "today" in self._stat_labels:
            self._stat_labels["today"].config(text=f"₱{today_total:.0f}")
