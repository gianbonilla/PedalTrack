import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from components.widgets import C, accent_btn, ghost_btn, build_tree, FormDialog


class RentalsView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()
        self._load()

    def _build(self):
        pad = tk.Frame(self, bg=C["bg"])
        pad.pack(fill="both", expand=True, padx=28, pady=24)

        hdr = tk.Frame(pad, bg=C["bg"])
        hdr.pack(fill="x", pady=(0, 16))
        tk.Label(hdr, text="Rentals", font=("Georgia", 16, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(side="left")
        accent_btn(hdr, "+ New rental", self._new_rental).pack(side="right")

        # Filters
        bar = tk.Frame(pad, bg=C["bg"])
        bar.pack(fill="x", pady=(0, 12))
        tk.Label(bar, text="Filter:", font=("Helvetica Neue", 11),
                 bg=C["bg"], fg=C["text_muted"]).pack(side="left", padx=(0, 6))
        self.status_var = tk.StringVar(value="all")
        cb = ttk.Combobox(bar, textvariable=self.status_var, width=16, state="readonly",
                          values=["all", "active", "returned", "overdue"])
        cb.pack(side="left")
        self.status_var.trace_add("write", lambda *_: self._load())

        # Table
        cols = ("id", "customer", "bike", "start", "end", "amount", "status")
        tf = tk.Frame(pad, bg=C["surface"],
                      highlightthickness=1, highlightbackground=C["border"])
        tf.pack(fill="both", expand=True)

        self.tree, sb = build_tree(tf, cols)
        for col, txt, w in [
            ("id","#",40), ("customer","Customer",180), ("bike","Bike",150),
            ("start","Started",130), ("end","Returned",130),
            ("amount","Amount",90), ("status","Status",100)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, stretch=(col in ("customer","bike")))

        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self._on_double_click)

        tk.Label(pad, text="Double-click an active rental to process return & payment.",
                 font=("Helvetica Neue", 10), bg=C["bg"], fg=C["text_hint"]).pack(anchor="w", pady=(8, 0))

    def _load(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rentals = self.app.db.get_all_rentals(self.status_var.get())
        for i, r in enumerate(rentals):
            tag = "alt" if i % 2 else ""
            amt = f"₱{r['total_amount']:.0f}" if r["total_amount"] else "—"
            self.tree.insert("", "end", iid=str(r["rental_id"]),
                values=(r["rental_id"], r["customer_name"],
                        f"{r['bike_code']} · {r['brand']}",
                        r["rental_start"][:16],
                        r["rental_end"][:16] if r["rental_end"] else "—",
                        amt, r["status"].title()),
                tags=(tag,))

    def _on_double_click(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        rental = self.app.db.get_rental(int(sel[0]))
        if rental and rental["status"] == "active":
            ReturnPaymentDialog(self, self.app, rental, self._load)
        elif rental and rental["status"] == "returned":
            messagebox.showinfo("Already returned",
                "This rental has already been returned and paid.", parent=self)

    def _new_rental(self):
        NewRentalDialog(self, self.app, self._load)


class NewRentalDialog(FormDialog):
    def __init__(self, parent, app, on_save):
        self.app = app
        self.on_save = on_save
        self._customers = app.db.get_all_customers()
        self._bikes = app.db.get_available_bikes()
        super().__init__(parent, "New rental", width=460, height=440)
        if not self._bikes:
            messagebox.showwarning("No bikes available",
                "There are no available bikes right now.", parent=parent)
            self.destroy()
            return
        self._build()

    def _build(self):
        p = tk.Frame(self, bg=C["surface"])
        p.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(p, text="New rental", font=("Georgia", 14, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(0, 18))

        # Customer
        cust_names = [f"{c['first_name']} {c['last_name']}" for c in self._customers]
        self._cust_var, _ = self.combo(p, "Customer", cust_names)

        # Bike
        bike_labels = [f"{b['bike_code']} · {b['brand']} {b['model']} ({b['size'].title()})"
                       for b in self._bikes]
        self._bike_var, _ = self.combo(p, "Bike", bike_labels)

        # Rate
        rate_row = tk.Frame(p, bg=C["surface"])
        rate_row.pack(fill="x", pady=(0, 10))
        tk.Label(rate_row, text="Rate per hour (₱)", font=("Helvetica Neue", 11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0, 3))
        self._rate_var = tk.StringVar(value="30")
        ttk.Entry(rate_row, textvariable=self._rate_var,
                  font=("Helvetica Neue", 12)).pack(fill="x")
        rate_row.pack(fill="x", pady=(0, 10))

        # Notes
        tk.Label(p, text="Notes (optional)", font=("Helvetica Neue", 11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0, 3))
        self._notes = tk.Text(p, height=3, font=("Helvetica Neue", 12),
                              bg=C["surface"], fg=C["text"],
                              relief="solid", bd=1,
                              highlightthickness=1,
                              highlightbackground=C["border"])
        self._notes.pack(fill="x", pady=(0, 14))

        # Info
        s = self.app.current_staff
        tk.Label(p, text=f"Processed by: {s['first_name']} {s['last_name']} ({s['role'].title()})",
                 font=("Helvetica Neue", 10), bg=C["surface"],
                 fg=C["text_hint"]).pack(anchor="w", pady=(0, 12))

        self.btn_bar(p, "Confirm rental", self._save)

    def _save(self):
        ci = self._cust_var.get()
        bi = self._bike_var.get()
        rate = self._rate_var.get().strip()

        if not ci or not bi:
            messagebox.showwarning("Missing", "Please select a customer and bike.", parent=self)
            return
        try:
            rate_val = float(rate)
        except ValueError:
            messagebox.showwarning("Invalid rate", "Enter a valid hourly rate.", parent=self)
            return

        cust_idx = [f"{c['first_name']} {c['last_name']}" for c in self._customers].index(ci)
        bike_labels = [f"{b['bike_code']} · {b['brand']} {b['model']} ({b['size'].title()})"
                       for b in self._bikes]
        bike_idx = bike_labels.index(bi)

        data = {
            "customer_id":  self._customers[cust_idx]["customer_id"],
            "bike_id":      self._bikes[bike_idx]["bike_id"],
            "staff_id":     self.app.current_staff["staff_id"],
            "rental_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rental_rate":  rate_val,
            "notes":        self._notes.get("1.0", "end-1c").strip() or None,
        }
        try:
            rid = self.app.db.create_rental(data)
            self.app.db.log_action(self.app.current_staff["staff_id"],
                                   "CREATE_RENTAL", "rental", rid)
            self.on_save()
            self.destroy()
            messagebox.showinfo("Rental started", f"Rental #{rid} created successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)


class ReturnPaymentDialog(tk.Toplevel):
    def __init__(self, parent, app, rental, on_save):
        root = parent.winfo_toplevel()
        super().__init__(root)
        self.app = app
        self.rental = rental
        self.on_save = on_save
        self.title("Process return")
        self.configure(bg=C["surface"])
        self.resizable(False, False)
        self.grab_set()
        w, h = 440, 500
        px = root.winfo_x() + root.winfo_width()//2 - w//2
        py = root.winfo_y() + root.winfo_height()//2 - h//2
        self.geometry(f"{w}x{h}+{px}+{py}")
        self._build()

    def _build(self):
        r = self.rental
        now = datetime.now()
        start = datetime.strptime(r["rental_start"], "%Y-%m-%d %H:%M:%S")
        duration_hours = max((now - start).total_seconds() / 3600, 0)
        billed_hours = max(1, int(duration_hours) + (1 if duration_hours % 1 > 0 else 0))
        total = billed_hours * float(r["rental_rate"])

        p = tk.Frame(self, bg=C["surface"])
        p.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(p, text="Process return", font=("Georgia", 14, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(0, 16))

        # Rental summary card
        summary = tk.Frame(p, bg=C["bg"],
                           highlightthickness=1, highlightbackground=C["border"])
        summary.pack(fill="x", pady=(0, 14))
        sp = tk.Frame(summary, bg=C["bg"])
        sp.pack(padx=14, pady=12, fill="x")

        for label, val in [
            ("Customer", r["customer_name"]),
            ("Bike",     f"{r['bike_code']} · {r['brand']} {r['model']}"),
            ("Started",  r["rental_start"][:16]),
            ("Duration", f"{duration_hours:.1f} hrs → billed {billed_hours} hr(s)"),
        ]:
            row = tk.Frame(sp, bg=C["bg"])
            tk.Label(row, text=label, font=("Helvetica Neue", 11),
                     bg=C["bg"], fg=C["text_muted"], width=10, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=("Helvetica Neue", 11),
                     bg=C["bg"], fg=C["text"]).pack(side="left")
            row.pack(anchor="w", pady=2)

        # Total
        tk.Frame(p, height=1, bg=C["border"]).pack(fill="x", pady=(0, 12))
        total_row = tk.Frame(p, bg=C["surface"])
        total_row.pack(fill="x", pady=(0, 16))
        tk.Label(total_row, text="Total due", font=("Helvetica Neue", 12),
                 bg=C["surface"], fg=C["text_muted"]).pack(side="left")
        tk.Label(total_row, text=f"₱{total:.0f}",
                 font=("Georgia", 22, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="right")

        # Payment method
        tk.Label(p, text="Payment method", font=("Helvetica Neue", 11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0, 8))
        self._method_var = tk.StringVar(value="cash")
        method_row = tk.Frame(p, bg=C["surface"])
        method_row.pack(fill="x", pady=(0, 18))
        for method in ["cash", "gcash", "card"]:
            rb = tk.Radiobutton(method_row, text=method.title(),
                               variable=self._method_var, value=method,
                               font=("Helvetica Neue", 11),
                               bg=C["surface"], fg=C["text"],
                               activebackground=C["surface"],
                               selectcolor=C["accent_light"],
                               cursor="hand2")
            rb.pack(side="left", padx=(0, 16))

        # Confirm button
        def confirm():
            end_time = now.strftime("%Y-%m-%d %H:%M:%S")
            self.app.db.return_rental(r["rental_id"], end_time, total)
            self.app.db.create_payment({
                "rental_id":      r["rental_id"],
                "amount_paid":    total,
                "payment_method": self._method_var.get(),
            })
            self.app.db.log_action(self.app.current_staff["staff_id"],
                                   "RETURN_RENTAL", "rental", r["rental_id"])
            self.on_save()
            self.destroy()
            messagebox.showinfo("Return complete",
                f"Rental #{r['rental_id']} returned.\n"
                f"Payment of ₱{total:.0f} via {self._method_var.get().title()} recorded.")

        tk.Button(p, text="Confirm return & payment",
                  command=confirm,
                  bg=C["accent"], fg="#FFFFFF",
                  font=("Helvetica Neue", 12, "bold"),
                  relief="flat", bd=0, pady=10,
                  cursor="hand2").pack(fill="x")
