import tkinter as tk
from tkinter import ttk, messagebox
from components.widgets import C, accent_btn, ghost_btn, build_tree, badge_colors, FormDialog


class CustomersView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build()
        self._load()

    def _build(self):
        pad = tk.Frame(self, bg=C["bg"])
        pad.pack(fill="both", expand=True, padx=28, pady=24)

        # Header
        hdr = tk.Frame(pad, bg=C["bg"])
        hdr.pack(fill="x", pady=(0, 16))
        tk.Label(hdr, text="Customers", font=("Georgia", 16, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(side="left")
        accent_btn(hdr, "+ Add customer", self._add).pack(side="right")

        # Search bar
        bar = tk.Frame(pad, bg=C["bg"])
        bar.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load())
        ttk.Entry(bar, textvariable=self.search_var,
                  font=("Helvetica Neue", 12), width=40).pack(side="left")
        tk.Label(bar, text="  Search by name, email or contact",
                 font=("Helvetica Neue", 11), bg=C["bg"],
                 fg=C["text_hint"]).pack(side="left")

        # Table
        cols = ("name", "contact", "email", "registered", "actions")
        tf = tk.Frame(pad, bg=C["surface"],
                      highlightthickness=1, highlightbackground=C["border"])
        tf.pack(fill="both", expand=True)

        self.tree, sb = build_tree(tf, cols)
        for col, txt, w in [
            ("name","Name",200), ("contact","Contact",140),
            ("email","Email",200), ("registered","Registered",110),
            ("actions","",80)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, stretch=(col in ("name","email")))

        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self._on_double_click)

    def _load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        customers = self.app.db.get_all_customers(self.search_var.get())
        for i, c in enumerate(customers):
            name = f"{c['first_name']} {c['last_name']}"
            email = c["email"] or "—"
            tag = "alt" if i % 2 else ""
            self.tree.insert("", "end", iid=str(c["customer_id"]),
                values=(name, c["contact_number"], email,
                        c["date_registered"], "View / Edit"),
                tags=(tag,))

    def _on_double_click(self, event):
        sel = self.tree.selection()
        if sel:
            CustomerProfileDialog(self, self.app, int(sel[0]), self._load)

    def _add(self):
        CustomerFormDialog(self, self.app, None, self._load)


class CustomerFormDialog(FormDialog):
    def __init__(self, parent, app, customer_id, on_save):
        self.app = app
        self.customer_id = customer_id
        self.on_save = on_save
        title = "Edit customer" if customer_id else "Add customer"
        super().__init__(parent, title, width=440, height=400)
        self._build()
        if customer_id:
            self._populate()

    def _build(self):
        p = tk.Frame(self, bg=C["surface"])
        p.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(p, text=self.title(), font=("Georgia", 14, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(0, 18))

        row1 = tk.Frame(p, bg=C["surface"])
        row1.pack(fill="x", pady=(0, 10))
        for label, attr in [("First name", "fn"), ("Last name", "ln")]:
            col = tk.Frame(row1, bg=C["surface"])
            tk.Label(col, text=label, font=("Helvetica Neue", 11),
                     bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0, 3))
            e = ttk.Entry(col, font=("Helvetica Neue", 12))
            e.pack(fill="x")
            col.pack(side="left", expand=True, fill="x", padx=(0, 8 if attr == "fn" else 0))
            setattr(self, f"_{attr}", e)

        self._contact = self.entry(p, "Contact number")
        self._email   = self.entry(p, "Email (optional)")

        self.btn_bar(p, "Save customer", self._save)

    def _populate(self):
        c = self.app.db.get_customer(self.customer_id)
        if c:
            self._fn.insert(0, c["first_name"])
            self._ln.insert(0, c["last_name"])
            self._contact.insert(0, c["contact_number"])
            self._email.insert(0, c["email"] or "")

    def _save(self):
        data = {
            "first_name":     self._fn.get().strip(),
            "last_name":      self._ln.get().strip(),
            "contact_number": self._contact.get().strip(),
            "email":          self._email.get().strip() or None,
        }
        if not data["first_name"] or not data["last_name"] or not data["contact_number"]:
            messagebox.showwarning("Missing fields", "First name, last name and contact are required.", parent=self)
            return
        if self.customer_id:
            self.app.db.update_customer(self.customer_id, data)
            self.app.db.log_action(self.app.current_staff["staff_id"], "UPDATE_CUSTOMER", "customer", self.customer_id)
        else:
            cid = self.app.db.create_customer(data)
            self.app.db.log_action(self.app.current_staff["staff_id"], "CREATE_CUSTOMER", "customer", cid)
        self.on_save()
        self.destroy()


class CustomerProfileDialog(tk.Toplevel):
    def __init__(self, parent, app, customer_id, on_close):
        root = parent.winfo_toplevel()
        super().__init__(root)
        self.app = app
        self.customer_id = customer_id
        self.on_close = on_close
        self.title("Customer profile")
        self.configure(bg=C["surface"])
        self.resizable(False, False)
        self.grab_set()
        w, h = 480, 520
        px = root.winfo_x() + root.winfo_width()//2 - w//2
        py = root.winfo_y() + root.winfo_height()//2 - h//2
        self.geometry(f"{w}x{h}+{px}+{py}")
        self._build()

    def _build(self):
        c = self.app.db.get_customer(self.customer_id)
        stats = self.app.db.get_customer_stats(self.customer_id)
        rentals = self.app.db.get_customer_rentals(self.customer_id)

        p = tk.Frame(self, bg=C["surface"])
        p.pack(fill="both", expand=True, padx=28, pady=24)

        # Header
        hdr = tk.Frame(p, bg=C["surface"])
        hdr.pack(fill="x", pady=(0, 16))
        name = f"{c['first_name']} {c['last_name']}"
        initials = f"{c['first_name'][0]}{c['last_name'][0]}".upper()

        av = tk.Label(hdr, text=initials, width=3,
                      font=("Helvetica Neue", 13, "bold"),
                      bg=C["accent_light"], fg=C["accent_text"])
        av.pack(side="left")

        info = tk.Frame(hdr, bg=C["surface"])
        info.pack(side="left", padx=(10, 0), fill="x", expand=True)
        tk.Label(info, text=name, font=("Georgia", 14, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w")
        tk.Label(info, text=f"Since {c['date_registered']}",
                 font=("Helvetica Neue", 10),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w")

        accent_btn(hdr, "Edit",
                   lambda: CustomerFormDialog(self, self.app, self.customer_id,
                                              self._refresh)).pack(side="right")

        tk.Frame(p, height=1, bg=C["border"]).pack(fill="x", pady=(0, 14))

        # Stats
        sc = tk.Frame(p, bg=C["surface"])
        sc.pack(fill="x", pady=(0, 14))
        for lbl, val in [("Total rentals", str(stats["total_rentals"])),
                          ("Total spent",   f"₱{stats['total_spent']:.0f}")]:
            box = tk.Frame(sc, bg=C["bg"],
                           highlightthickness=1, highlightbackground=C["border"])
            tk.Label(box, text=lbl, font=("Helvetica Neue", 10),
                     bg=C["bg"], fg=C["text_muted"]).pack(anchor="w", padx=12, pady=(8,2))
            tk.Label(box, text=val, font=("Georgia", 20, "bold"),
                     bg=C["bg"], fg=C["text"]).pack(anchor="w", padx=12, pady=(0,8))
            box.pack(side="left", expand=True, fill="x", padx=(0, 8))

        # Contact info
        for lbl, val in [("Contact", c["contact_number"]), ("Email", c["email"] or "—")]:
            row = tk.Frame(p, bg=C["surface"])
            tk.Label(row, text=lbl, font=("Helvetica Neue", 11),
                     bg=C["surface"], fg=C["text_muted"], width=10, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=("Helvetica Neue", 11),
                     bg=C["surface"], fg=C["text"]).pack(side="left")
            row.pack(anchor="w", pady=2)

        tk.Frame(p, height=1, bg=C["border"]).pack(fill="x", pady=(12, 10))

        tk.Label(p, text="Recent rentals", font=("Georgia", 12, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(0, 8))

        rf = tk.Frame(p, bg=C["surface"],
                      highlightthickness=1, highlightbackground=C["border"])
        rf.pack(fill="both", expand=True)

        cols = ("date", "bike", "amount")
        tree = ttk.Treeview(rf, columns=cols, show="headings", height=5)
        tree.heading("date", text="Date")
        tree.heading("bike", text="Bike")
        tree.heading("amount", text="Amount")
        tree.column("date", width=110)
        tree.column("bike", width=170)
        tree.column("amount", width=90)
        tree.tag_configure("alt", background=C["row_alt"])

        for i, r in enumerate(rentals):
            amt = f"₱{r['total_amount']:.0f}" if r["total_amount"] else r["status"].title()
            tag = "alt" if i % 2 else ""
            tree.insert("", "end",
                values=(r["rental_start"][:10],
                        f"{r['bike_code']} · {r['brand']}",
                        amt),
                tags=(tag,))
        tree.pack(fill="both", expand=True)

    def _refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
        self.on_close()
