import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from components.widgets import C


def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()


class LoginView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=C["bg"])
        self.pack(fill="both", expand=True)
        self.app = app
        self._build()

    def _build(self):
        # Centered card
        outer = tk.Frame(self, bg=C["bg"])
        outer.place(relx=0.5, rely=0.5, anchor="center")

        card = tk.Frame(outer, bg=C["surface"],
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(padx=0, pady=0)

        inner = tk.Frame(card, bg=C["surface"])
        inner.pack(padx=44, pady=40)

        # Brand
        tk.Label(inner, text="PedalTrack", font=("Georgia", 22, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w")
        tk.Label(inner, text="Bike Rental Management", font=("Helvetica Neue", 12),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(2, 24))

        tk.Frame(inner, height=1, bg=C["border"]).pack(fill="x", pady=(0, 24))

        # Username
        tk.Label(inner, text="Username", font=("Helvetica Neue", 11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0, 4))
        self.username_var = tk.StringVar()
        ttk.Entry(inner, textvariable=self.username_var, width=32,
                  font=("Helvetica Neue", 13)).pack(fill="x", pady=(0, 14))

        # Password
        tk.Label(inner, text="Password", font=("Helvetica Neue", 11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0, 4))
        self.password_var = tk.StringVar()
        pw = ttk.Entry(inner, textvariable=self.password_var, show="•", width=32,
                       font=("Helvetica Neue", 13))
        pw.pack(fill="x", pady=(0, 6))
        pw.bind("<Return>", lambda e: self._login())

        self.err_label = tk.Label(inner, text="", font=("Helvetica Neue", 11),
                                  bg=C["surface"], fg=C["danger"])
        self.err_label.pack(anchor="w", pady=(0, 10))

        # Button
        tk.Button(inner, text="Sign in",
                  command=self._login,
                  bg=C["accent"], fg="#FFFFFF",
                  font=("Helvetica Neue", 12, "bold"),
                  relief="flat", bd=0, padx=0, pady=10,
                  cursor="hand2", width=28).pack(fill="x")

        tk.Label(inner, text="Default: admin / admin1234",
                 font=("Helvetica Neue", 10),
                 bg=C["surface"], fg=C["text_hint"]).pack(pady=(14, 0))

    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            self.err_label.config(text="Please enter your username and password.")
            return
        staff = self.app.db.get_staff_by_username(username)
        if staff and staff["password_hash"] == hash_password(password):
            self.app.db.log_action(staff["staff_id"], "LOGIN")
            self.app.login(staff)
        else:
            self.err_label.config(text="Incorrect username or password.")
            self.password_var.set("")
