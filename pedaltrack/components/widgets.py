import tkinter as tk
from tkinter import ttk

C = {
    "bg":"#F7F6F2","surface":"#FFFFFF","sidebar_bg":"#1A1A18",
    "sidebar_text":"#A8A89E","sidebar_active_bg":"#2C2C28","sidebar_active_txt":"#F0EFEA",
    "accent":"#2D6A4F","accent_light":"#D8F3DC","accent_text":"#1B4332",
    "text":"#1C1C1A","text_muted":"#6B6B63","text_hint":"#A8A89E","border":"#E8E6E0",
    "danger":"#C0392B","danger_light":"#FDECEA","warning":"#B7770D","warning_light":"#FEF3C7",
    "success":"#1B7A4A","success_light":"#D1FAE5","info":"#1E5EA8","info_light":"#DBEAFE",
    "row_alt":"#FAFAF8",
}

STATUS_BADGE = {
    "available":         (C["success_light"], C["success"]),
    "rented":            (C["info_light"],    C["info"]),
    "under_maintenance": (C["warning_light"], C["warning"]),
    "active":            (C["info_light"],    C["info"]),
    "returned":          (C["success_light"], C["success"]),
    "overdue":           (C["danger_light"],  C["danger"]),
    "paid":              (C["success_light"], C["success"]),
    "pending":           (C["warning_light"], C["warning"]),
    "refunded":          (C["danger_light"],  C["danger"]),
    "resolved":          (C["success_light"], C["success"]),
    "parts_needed":      (C["warning_light"], C["warning"]),
    "retired":           (C["danger_light"],  C["danger"]),
    "admin":             ("#EEEDFE",          "#3C3489"),
    "cashier":           ("#EAF3DE",          "#27500A"),
    "mechanic":          ("#FEF3C7",          "#92400E"),
    "inactive":          ("#F1EFE8",          "#6B6B63"),
}

def badge_colors(key):
    return STATUS_BADGE.get(str(key).lower().replace(" ","_"), (C["bg"], C["text_muted"]))

def accent_btn(parent, text, cmd, danger=False):
    bg = C["danger"] if danger else C["accent"]
    b = tk.Button(parent, text=text, command=cmd,
                  bg=bg, fg="#FFFFFF", font=("Helvetica Neue",11,"bold"),
                  relief="flat", padx=14, pady=7, cursor="hand2", bd=0)
    return b

def ghost_btn(parent, text, cmd):
    b = tk.Button(parent, text=text, command=cmd,
                  bg=C["surface"], fg=C["text_muted"],
                  font=("Helvetica Neue",11), relief="flat",
                  padx=14, pady=7, cursor="hand2", bd=0,
                  highlightthickness=1, highlightbackground=C["border"])
    return b

def section_label(parent, text, bg=None):
    bg = bg or C["bg"]
    return tk.Label(parent, text=text,
                    font=("Georgia",14,"bold"),
                    bg=bg, fg=C["text"])

def muted_label(parent, text, bg=None):
    bg = bg or C["bg"]
    return tk.Label(parent, text=text,
                    font=("Helvetica Neue",11),
                    bg=bg, fg=C["text_muted"])

def field_label(parent, text, bg=None):
    bg = bg or C["surface"]
    return tk.Label(parent, text=text,
                    font=("Helvetica Neue",11),
                    bg=bg, fg=C["text_muted"])

def stat_card(parent, label, value, color=None):
    color = color or C["text"]
    f = tk.Frame(parent, bg=C["surface"],
                 highlightthickness=1, highlightbackground=C["border"])
    tk.Label(f, text=label, font=("Helvetica Neue",10),
             bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", padx=14, pady=(12,2))
    tk.Label(f, text=value, font=("Georgia",24,"bold"),
             bg=C["surface"], fg=color).pack(anchor="w", padx=14, pady=(0,12))
    return f

def hsep(parent, bg=None):
    return tk.Frame(parent, height=1, bg=bg or C["border"])

def build_tree(parent, columns, show="headings"):
    tree = ttk.Treeview(parent, columns=columns, show=show, selectmode="browse")
    sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.tag_configure("alt", background=C["row_alt"])
    return tree, sb


class FormDialog(tk.Toplevel):
    def __init__(self, parent_widget, title, width=460, height=520):
        root = parent_widget.winfo_toplevel()
        super().__init__(root)
        self.title(title)
        self.configure(bg=C["surface"])
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()
        self.update_idletasks()
        px = root.winfo_x() + root.winfo_width()//2 - width//2
        py = root.winfo_y() + root.winfo_height()//2 - height//2
        self.geometry(f"{width}x{height}+{px}+{py}")

    def lf(self, parent, label):
        tk.Label(parent, text=label, font=("Helvetica Neue",11),
                 bg=C["surface"], fg=C["text_muted"]).pack(anchor="w", pady=(0,3))

    def entry(self, parent, label, **kw):
        f = tk.Frame(parent, bg=C["surface"])
        self.lf(f, label)
        e = ttk.Entry(f, **kw)
        e.pack(fill="x")
        f.pack(fill="x", pady=(0,10))
        return e

    def combo(self, parent, label, values, **kw):
        f = tk.Frame(parent, bg=C["surface"])
        self.lf(f, label)
        v = tk.StringVar()
        cb = ttk.Combobox(f, textvariable=v, values=values, state="readonly", **kw)
        cb.pack(fill="x")
        f.pack(fill="x", pady=(0,10))
        return v, cb

    def btn_bar(self, parent, ok_text, ok_cmd, cancel_cmd=None):
        bar = tk.Frame(parent, bg=C["surface"])
        accent_btn(bar, ok_text, ok_cmd).pack(side="left")
        ghost_btn(bar, "Cancel", cancel_cmd or self.destroy).pack(side="left", padx=(8,0))
        bar.pack(anchor="w", pady=(8,0))
