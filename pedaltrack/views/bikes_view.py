import tkinter as tk
from tkinter import ttk, messagebox
from components.widgets import C, accent_btn, ghost_btn, build_tree, badge_colors, FormDialog


class BikesView(tk.Frame):
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
        tk.Label(hdr, text="Bikes", font=("Georgia", 16, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(side="left")
        accent_btn(hdr, "+ Add bike", self._add).pack(side="right")

        # Filters
        bar = tk.Frame(pad, bg=C["bg"])
        bar.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load())
        ttk.Entry(bar, textvariable=self.search_var,
                  font=("Helvetica Neue", 12), width=30).pack(side="left")

        tk.Label(bar, text="  Status:", font=("Helvetica Neue", 11),
                 bg=C["bg"], fg=C["text_muted"]).pack(side="left", padx=(12, 4))
        self.status_var = tk.StringVar(value="all")
        status_cb = ttk.Combobox(bar, textvariable=self.status_var, width=18,
                                 state="readonly",
                                 values=["all", "available", "rented", "under_maintenance"])
        status_cb.pack(side="left")
        self.status_var.trace_add("write", lambda *_: self._load())

        # Table
        cols = ("code", "brand_model", "size", "color", "status")
        tf = tk.Frame(pad, bg=C["surface"],
                      highlightthickness=1, highlightbackground=C["border"])
        tf.pack(fill="both", expand=True)

        self.tree, sb = build_tree(tf, cols)
        for col, txt, w, stretch in [
            ("code",       "Code",        80,  False),
            ("brand_model","Brand / Model",220, True),
            ("size",       "Size",        80,  False),
            ("color",      "Color",       90,  False),
            ("status",     "Status",      140, False)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, stretch=stretch)

        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self._on_double_click)

    def _load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        bikes = self.app.db.get_all_bikes(self.search_var.get(), self.status_var.get())
        for i, b in enumerate(bikes):
            tag = "alt" if i % 2 else ""
            status_disp = b["status"].replace("_", " ").title()
            self.tree.insert("", "end", iid=str(b["bike_id"]),
                values=(b["bike_code"], f"{b['brand']} {b['model']}",
                        b["size"].title(), b["color"], status_disp),
                tags=(tag,))

    def _on_double_click(self, event):
        sel = self.tree.selection()
        if sel:
            bike = self.app.db.get_bike(int(sel[0]))
            if bike and bike["status"] != "rented":
                BikeFormDialog(self, self.app, int(sel[0]), self._load)
            elif bike and bike["status"] == "rented":
                messagebox.showinfo("Bike rented", "This bike is currently rented. Return it first before editing.", parent=self)

    def _add(self):
        BikeFormDialog(self, self.app, None, self._load)


class BikeFormDialog(FormDialog):
    def __init__(self, parent, app, bike_id, on_save):
        self.app = app
        self.bike_id = bike_id
        self.on_save = on_save
        title = "Edit bike" if bike_id else "Add bike"
        super().__init__(parent, title, width=440, height=430)
        self._build()
        if bike_id:
            self._populate()

    def _build(self):
        p = tk.Frame(self, bg=C["surface"])
        p.pack(fill="both", expand=True, padx=28, pady=24)

        tk.Label(p, text=self.title(), font=("Georgia", 14, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w", pady=(0, 18))

        # Row: code + brand
        row1 = tk.Frame(p, bg=C["surface"])
        row1.pack(fill="x", pady=(0, 10))
        for label, attr, side_pad in [("Bike code", "_code", 8), ("Brand", "_brand", 0)]:
            col = tk.Frame(row1, bg=C["surface"])
            tk.Label(col, text=label, font=("Helvetica Neue", 11),
                     bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0, 3))
            e = ttk.Entry(col, font=("Helvetica Neue", 12))
            e.pack(fill="x")
            col.pack(side="left", expand=True, fill="x", padx=(0, side_pad))
            setattr(self, attr, e)

        self._model = self.entry(p, "Model")

        # Row: size + color
        row2 = tk.Frame(p, bg=C["surface"])
        row2.pack(fill="x", pady=(0, 10))
        for label, attr, vals, side_pad in [
            ("Size", "_size_var", ["small","medium","large"], 8),
            ("Color", "_color", None, 0)]:
            col = tk.Frame(row2, bg=C["surface"])
            tk.Label(col, text=label, font=("Helvetica Neue", 11),
                     bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0, 3))
            if vals:
                v = tk.StringVar()
                w = ttk.Combobox(col, textvariable=v, values=vals, state="readonly",
                                 font=("Helvetica Neue", 12))
                w.pack(fill="x")
                setattr(self, attr, v)
            else:
                e = ttk.Entry(col, font=("Helvetica Neue", 12))
                e.pack(fill="x")
                setattr(self, attr, e)
            col.pack(side="left", expand=True, fill="x", padx=(0, side_pad))

        self.btn_bar(p, "Save bike", self._save)

    def _populate(self):
        b = self.app.db.get_bike(self.bike_id)
        if b:
            self._code.insert(0, b["bike_code"])
            self._brand.insert(0, b["brand"])
            self._model.insert(0, b["model"])
            self._size_var.set(b["size"])
            self._color.insert(0, b["color"])

    def _save(self):
        data = {
            "bike_code": self._code.get().strip(),
            "brand":     self._brand.get().strip(),
            "model":     self._model.get().strip(),
            "size":      self._size_var.get(),
            "color":     self._color.get().strip(),
        }
        if not all(data.values()):
            messagebox.showwarning("Missing fields", "All fields are required.", parent=self)
            return
        try:
            if self.bike_id:
                self.app.db.update_bike(self.bike_id, data)
                self.app.db.log_action(self.app.current_staff["staff_id"], "UPDATE_BIKE", "bike", self.bike_id)
            else:
                bid = self.app.db.create_bike(data)
                self.app.db.log_action(self.app.current_staff["staff_id"], "CREATE_BIKE", "bike", bid)
            self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
