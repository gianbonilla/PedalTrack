import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from components.widgets import C, accent_btn, ghost_btn, build_tree, FormDialog


def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()


class StaffView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        if app.current_staff and app.current_staff.get("role") != "admin":
            tk.Label(self, text="Access denied. Admin only.",
                     font=("Georgia", 14), bg=C["bg"],
                     fg=C["danger"]).pack(expand=True)
            return
        self._build()
        self._load()

    def _build(self):
        pad = tk.Frame(self, bg=C["bg"])
        pad.pack(fill="both", expand=True, padx=28, pady=24)

        hdr = tk.Frame(pad, bg=C["bg"])
        hdr.pack(fill="x", pady=(0, 6))
        tk.Label(hdr, text="Staff accounts", font=("Georgia", 16, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(side="left")
        accent_btn(hdr, "+ Add staff", self._add).pack(side="right")

        tk.Label(pad, text="Admin access only",
                 font=("Helvetica Neue", 11), bg=C["bg"],
                 fg=C["text_muted"]).pack(anchor="w", pady=(0, 14))

        # Filters
        bar = tk.Frame(pad, bg=C["bg"])
        bar.pack(fill="x", pady=(0, 12))
        tk.Label(bar, text="Role:", font=("Helvetica Neue", 11),
                 bg=C["bg"], fg=C["text_muted"]).pack(side="left", padx=(0, 6))
        self.role_var = tk.StringVar(value="all")
        ttk.Combobox(bar, textvariable=self.role_var, width=14, state="readonly",
                     values=["all","admin","cashier","mechanic"]).pack(side="left")
        self.role_var.trace_add("write", lambda *_: self._load())

        # Table
        cols = ("sid","name","username","role","contact","status","actions")
        tf = tk.Frame(pad, bg=C["surface"],
                      highlightthickness=1, highlightbackground=C["border"])
        tf.pack(fill="both", expand=True)

        self.tree, sb = build_tree(tf, cols)
        for col, txt, w, st in [
            ("sid","#",40,False),("name","Name",180,True),
            ("username","Username",110,False),("role","Role",90,False),
            ("contact","Contact",130,False),("status","Status",80,False),
            ("actions","",100,False)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, stretch=st)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self._on_double_click)

    def _load(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        staff_list = self.app.db.get_all_staff()
        role_filter = self.role_var.get()
        for i, s in enumerate(staff_list):
            if role_filter != "all" and s["role"] != role_filter:
                continue
            tag = "alt" if i % 2 else ""
            name = f"{s['first_name']} {s['last_name']}"
            action = "Disable" if s["status"] == "active" else "Enable"
            self.tree.insert("", "end", iid=str(s["staff_id"]),
                values=(s["staff_id"], name, s["username"],
                        s["role"].title(), s["contact_number"],
                        s["status"].title(), action),
                tags=(tag,))

    def _on_double_click(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        sid = int(sel[0])
        if sid == self.app.current_staff["staff_id"]:
            messagebox.showinfo("Cannot edit", "Use the profile settings to edit your own account.")
            return
        staff_list = self.app.db.get_all_staff()
        s = next((x for x in staff_list if x["staff_id"] == sid), None)
        if s:
            StaffFormDialog(self, self.app, s, self._load)

    def _add(self):
        StaffFormDialog(self, self.app, None, self._load)


class StaffFormDialog(FormDialog):
    def __init__(self, parent, app, staff_data, on_save):
        self.app = app
        self.staff_data = staff_data
        self.on_save = on_save
        title = "Edit staff" if staff_data else "Add staff account"
        height = 540 if not staff_data else 480
        super().__init__(parent, title, width=460, height=height)
        self._build()

    def _build(self):
        p = tk.Frame(self, bg=C["surface"])
        p.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(p, text=self.title(), font=("Georgia", 14, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(0, 18))

        # First / Last name row
        row1 = tk.Frame(p, bg=C["surface"])
        row1.pack(fill="x", pady=(0, 10))
        for label, attr, side_pad in [("First name","_fn",8),("Last name","_ln",0)]:
            col = tk.Frame(row1, bg=C["surface"])
            tk.Label(col, text=label, font=("Helvetica Neue", 11),
                     bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0,3))
            e = ttk.Entry(col, font=("Helvetica Neue", 12))
            e.pack(fill="x")
            col.pack(side="left", expand=True, fill="x", padx=(0, side_pad))
            setattr(self, attr, e)

        # Username + role row
        row2 = tk.Frame(p, bg=C["surface"])
        row2.pack(fill="x", pady=(0, 10))
        col_u = tk.Frame(row2, bg=C["surface"])
        tk.Label(col_u, text="Username", font=("Helvetica Neue", 11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0,3))
        self._username = ttk.Entry(col_u, font=("Helvetica Neue", 12))
        self._username.pack(fill="x")
        col_u.pack(side="left", expand=True, fill="x", padx=(0,8))

        col_r = tk.Frame(row2, bg=C["surface"])
        tk.Label(col_r, text="Role", font=("Helvetica Neue", 11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0,3))
        self._role_var = tk.StringVar()
        ttk.Combobox(col_r, textvariable=self._role_var,
                     values=["admin","cashier","mechanic"],
                     state="readonly", font=("Helvetica Neue", 12)).pack(fill="x")
        col_r.pack(side="left", expand=True, fill="x")

        self._contact = self.entry(p, "Contact number")

        if self.staff_data:
            # Status toggle
            self._status_var, _ = self.combo(p, "Status", ["active","inactive"])
            self._status_var.set(self.staff_data["status"])

        # Password section
        tk.Frame(p, height=1, bg=C["border"]).pack(fill="x", pady=(4, 10))
        pw_title = "Password" if not self.staff_data else "New password (leave blank to keep)"
        tk.Label(p, text=pw_title, font=("Helvetica Neue", 11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0,3))
        self._pw = ttk.Entry(p, show="•", font=("Helvetica Neue", 12))
        self._pw.pack(fill="x", pady=(0, 8))

        if not self.staff_data:
            tk.Label(p, text="Confirm password",
                     font=("Helvetica Neue", 11),
                     bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0,3))
            self._pw2 = ttk.Entry(p, show="•", font=("Helvetica Neue", 12))
            self._pw2.pack(fill="x", pady=(0, 12))

        if self.staff_data:
            self._fn.insert(0, self.staff_data["first_name"])
            self._ln.insert(0, self.staff_data["last_name"])
            self._username.insert(0, self.staff_data["username"])
            self._role_var.set(self.staff_data["role"])
            self._contact.insert(0, self.staff_data["contact_number"])

        self.btn_bar(p, "Save account", self._save)

    def _save(self):
        fn      = self._fn.get().strip()
        ln      = self._ln.get().strip()
        uname   = self._username.get().strip()
        role    = self._role_var.get()
        contact = self._contact.get().strip()
        pw      = self._pw.get()

        if not all([fn, ln, uname, role, contact]):
            messagebox.showwarning("Missing fields", "All fields except password are required.", parent=self)
            return

        if not self.staff_data:
            pw2 = self._pw2.get()
            if not pw:
                messagebox.showwarning("Password required", "Please set a password.", parent=self)
                return
            if pw != pw2:
                messagebox.showwarning("Password mismatch", "Passwords do not match.", parent=self)
                return

        data = {
            "username":      uname,
            "first_name":    fn,
            "last_name":     ln,
            "role":          role,
            "contact_number":contact,
            "status":        self._status_var.get() if self.staff_data else "active",
            "password_hash": hash_password(pw) if pw else (
                self.staff_data["password_hash"] if self.staff_data else ""),
        }

        try:
            if self.staff_data:
                self.app.db.update_staff(self.staff_data["staff_id"], data)
                if pw:
                    self.app.db.update_staff_password(self.staff_data["staff_id"], data["password_hash"])
                self.app.db.log_action(self.app.current_staff["staff_id"],
                                       "UPDATE_STAFF", "staff", self.staff_data["staff_id"])
            else:
                sid = self.app.db.create_staff(data)
                self.app.db.log_action(self.app.current_staff["staff_id"],
                                       "CREATE_STAFF", "staff", sid)
            self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
