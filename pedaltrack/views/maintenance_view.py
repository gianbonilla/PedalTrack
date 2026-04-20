import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from components.widgets import C, accent_btn, build_tree, FormDialog


class MaintenanceView(tk.Frame):
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
        tk.Label(hdr, text="Maintenance", font=("Georgia", 16, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(side="left")
        accent_btn(hdr, "+ Log maintenance", self._add).pack(side="right")

        cols = ("mid","bike","type","date","outcome","staff","desc")
        tf = tk.Frame(pad, bg=C["surface"],
                      highlightthickness=1, highlightbackground=C["border"])
        tf.pack(fill="both", expand=True)

        self.tree, sb = build_tree(tf, cols)
        for col, txt, w, st in [
            ("mid","#",44,False),("bike","Bike",120,False),
            ("type","Type",90,False),("date","Date",100,False),
            ("outcome","Outcome",110,False),("staff","Staff",140,False),
            ("desc","Description",260,True)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, stretch=st)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self._on_double_click)
        tk.Label(pad, text="Double-click a record to edit outcome.",
                 font=("Helvetica Neue", 10), bg=C["bg"],
                 fg=C["text_hint"]).pack(anchor="w", pady=(8,0))

    def _load(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        records = self.app.db.get_all_maintenance()
        for i, m in enumerate(records):
            tag = "alt" if i % 2 else ""
            self.tree.insert("", "end", iid=str(m["maintenance_id"]),
                values=(m["maintenance_id"],
                        f"{m['bike_code']} {m['brand']}",
                        m["maintenance_type"].title(),
                        m["maintenance_date"],
                        m["outcome"].replace("_"," ").title(),
                        m["staff_name"],
                        m["description"]),
                tags=(tag,))

    def _on_double_click(self, event):
        sel = self.tree.selection()
        if sel:
            mid = int(sel[0])
            records = self.app.db.get_all_maintenance()
            rec = next((r for r in records if r["maintenance_id"] == mid), None)
            if rec:
                MaintenanceEditDialog(self, self.app, rec, self._load)

    def _add(self):
        MaintenanceFormDialog(self, self.app, self._load)


class MaintenanceFormDialog(FormDialog):
    def __init__(self, parent, app, on_save):
        self.app = app
        self.on_save = on_save
        self._bikes = app.db.get_bikes_for_maintenance()
        super().__init__(parent, "Log maintenance", width=460, height=460)
        if not self._bikes:
            messagebox.showwarning("No bikes",
                "No bikes available for maintenance logging.", parent=parent)
            self.destroy()
            return
        self._build()

    def _build(self):
        p = tk.Frame(self, bg=C["surface"])
        p.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(p, text="Log maintenance", font=("Georgia", 14, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(0, 18))

        bike_labels = [f"{b['bike_code']} · {b['brand']} {b['model']}" for b in self._bikes]
        self._bike_var, _ = self.combo(p, "Bike", bike_labels)

        row = tk.Frame(p, bg=C["surface"])
        row.pack(fill="x", pady=(0, 10))
        # Type
        col1 = tk.Frame(row, bg=C["surface"])
        tk.Label(col1, text="Type", font=("Helvetica Neue", 11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0,3))
        self._type_var = tk.StringVar()
        ttk.Combobox(col1, textvariable=self._type_var,
                     values=["routine","repair","inspection"],
                     state="readonly", font=("Helvetica Neue", 12)).pack(fill="x")
        col1.pack(side="left", expand=True, fill="x", padx=(0, 8))
        # Date
        col2 = tk.Frame(row, bg=C["surface"])
        tk.Label(col2, text="Date", font=("Helvetica Neue", 11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0,3))
        self._date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(col2, textvariable=self._date_var,
                  font=("Helvetica Neue", 12)).pack(fill="x")
        col2.pack(side="left", expand=True, fill="x")

        # Description
        tk.Label(p, text="Description", font=("Helvetica Neue", 11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(10,3))
        self._desc = tk.Text(p, height=3, font=("Helvetica Neue", 12),
                             bg=C["surface"], fg=C["text"],
                             relief="solid", bd=1,
                             highlightthickness=1,
                             highlightbackground=C["border"])
        self._desc.pack(fill="x", pady=(0,10))

        # Outcome
        self._outcome_var, _ = self.combo(p, "Outcome",
                                          ["resolved","parts_needed","retired"])

        s = self.app.current_staff
        tk.Label(p, text=f"Performed by: {s['first_name']} {s['last_name']}",
                 font=("Helvetica Neue", 10), bg=C["surface"],
                 fg=C["text_hint"]).pack(anchor="w", pady=(0, 10))

        self.btn_bar(p, "Save record", self._save)

    def _save(self):
        bike_label = self._bike_var.get()
        mtype      = self._type_var.get()
        outcome    = self._outcome_var.get()
        desc       = self._desc.get("1.0", "end-1c").strip()
        mdate      = self._date_var.get().strip()

        if not bike_label or not mtype or not outcome or not desc:
            messagebox.showwarning("Missing fields", "All fields are required.", parent=self)
            return

        bike_labels = [f"{b['bike_code']} · {b['brand']} {b['model']}" for b in self._bikes]
        bike_idx = bike_labels.index(bike_label)

        data = {
            "bike_id":          self._bikes[bike_idx]["bike_id"],
            "staff_id":         self.app.current_staff["staff_id"],
            "maintenance_date": mdate,
            "maintenance_type": mtype,
            "description":      desc,
            "outcome":          outcome,
        }
        try:
            mid = self.app.db.create_maintenance(data)
            self.app.db.log_action(self.app.current_staff["staff_id"],
                                   "CREATE_MAINTENANCE", "maintenance", mid)
            self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)


class MaintenanceEditDialog(FormDialog):
    def __init__(self, parent, app, record, on_save):
        self.app = app
        self.record = record
        self.on_save = on_save
        super().__init__(parent, "Edit maintenance record", width=440, height=320)
        self._build()

    def _build(self):
        p = tk.Frame(self, bg=C["surface"])
        p.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(p, text="Edit record", font=("Georgia", 14, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(0, 6))
        r = self.record
        tk.Label(p, text=f"{r['bike_code']} · {r['brand']} {r['model']} — {r['maintenance_date']}",
                 font=("Helvetica Neue", 11), bg=C["surface"],
                 fg=C["text_muted"]).pack(anchor="w", pady=(0, 14))

        tk.Label(p, text="Description", font=("Helvetica Neue", 11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0,3))
        self._desc = tk.Text(p, height=4, font=("Helvetica Neue", 12),
                             bg=C["surface"], fg=C["text"],
                             relief="solid", bd=1,
                             highlightthickness=1,
                             highlightbackground=C["border"])
        self._desc.insert("1.0", r["description"])
        self._desc.pack(fill="x", pady=(0, 10))

        self._outcome_var, _ = self.combo(p, "Outcome",
                                          ["resolved","parts_needed","retired"])
        self._outcome_var.set(r["outcome"])

        self.btn_bar(p, "Update record", self._save)

    def _save(self):
        data = {
            "maintenance_type": self.record["maintenance_type"],
            "description":      self._desc.get("1.0","end-1c").strip(),
            "outcome":          self._outcome_var.get(),
        }
        self.app.db.update_maintenance(self.record["maintenance_id"], data)
        self.app.db.log_action(self.app.current_staff["staff_id"],
                               "UPDATE_MAINTENANCE", "maintenance",
                               self.record["maintenance_id"])
        self.on_save()
        self.destroy()
