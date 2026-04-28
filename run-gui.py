"""
Tkinter GUI — Dynamic Web Scraper
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from webscraper.scrapers.jobs import scrape_jobs
from webscraper.scrapers.products import scrape_products
from webscraper.scrapers.news import scrape_news
from webscraper.storage import save_data

SCRAPERS = {
    "Jobs": scrape_jobs,
    "Products": scrape_products,
    "News": scrape_news,
}

COLUMNS = {
    "Jobs": ["title", "company", "location", "tags", "date", "source"],
    "Products": ["name", "price", "rating", "category", "source"],
    "News": ["title", "description", "source", "published_date", "author"],
}

# Color palette
BG = "#0d1117"
SURFACE = "#161b22"
SURFACE2 = "#21262d"
ACCENT = "#58a6ff"
ACCENT2 = "#3fb950"
TEXT = "#e6edf3"
TEXT_DIM = "#8b949e"
RED = "#f85149"
YELLOW = "#d29922"
BORDER = "#30363d"


class WebScraperGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🕷 Dynamic Web Scraper")
        self.root.geometry("1200x780")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self._data: list = []
        self._filtered: list = []
        self._scraping = False

        self._setup_styles()
        self._build_ui()

    # ── Styles ────────────────────────────────────────────────────
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=BG, foreground=TEXT, font=("Consolas", 10))
        style.configure("TFrame", background=BG)
        style.configure("Surface.TFrame", background=SURFACE)
        style.configure("Surface2.TFrame", background=SURFACE2)

        style.configure("TLabel", background=BG, foreground=TEXT, font=("Consolas", 10))
        style.configure("Dim.TLabel", background=BG, foreground=TEXT_DIM, font=("Consolas", 9))
        style.configure("Header.TLabel", background=BG, foreground=ACCENT,
                        font=("Consolas", 20, "bold"))
        style.configure("Sub.TLabel", background=BG, foreground=TEXT_DIM, font=("Consolas", 10))
        style.configure("Status.TLabel", background=SURFACE2, foreground=ACCENT2,
                        font=("Consolas", 9))
        style.configure("Count.TLabel", background=BG, foreground=YELLOW, font=("Consolas", 11, "bold"))

        style.configure("Accent.TButton", background=ACCENT, foreground="#000000",
                        font=("Consolas", 10, "bold"), borderwidth=0, focuscolor="none")
        style.map("Accent.TButton",
                  background=[("active", "#79c0ff"), ("pressed", "#388bfd")])

        style.configure("Danger.TButton", background=RED, foreground="white",
                        font=("Consolas", 10, "bold"), borderwidth=0)
        style.map("Danger.TButton", background=[("active", "#ff7b72")])

        style.configure("Save.TButton", background=ACCENT2, foreground="#000000",
                        font=("Consolas", 10, "bold"), borderwidth=0)
        style.map("Save.TButton", background=[("active", "#56d364")])

        style.configure("TCombobox", fieldbackground=SURFACE2, background=SURFACE2,
                        foreground=TEXT, selectbackground=ACCENT, font=("Consolas", 10))
        style.map("TCombobox", fieldbackground=[("readonly", SURFACE2)])

        style.configure("TEntry", fieldbackground=SURFACE2, foreground=TEXT,
                        insertcolor=ACCENT, font=("Consolas", 10))

        style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE,
                        foreground=TEXT, rowheight=26, font=("Consolas", 9))
        style.configure("Treeview.Heading", background=SURFACE2, foreground=ACCENT,
                        font=("Consolas", 9, "bold"), relief="flat")
        style.map("Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#000000")])

        style.configure("TProgressbar", troughcolor=SURFACE2, background=ACCENT,
                        bordercolor=BORDER, lightcolor=ACCENT, darkcolor=ACCENT)

        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=SURFACE2, foreground=TEXT_DIM,
                        font=("Consolas", 10), padding=[12, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", SURFACE)],
                  foreground=[("selected", ACCENT)])

    # ── UI Build ──────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill="x", padx=20, pady=(16, 4))
        ttk.Label(header, text="🕷 WEB SCRAPER", style="Header.TLabel").pack(side="left")
        ttk.Label(header, text="  Jobs · Products · News", style="Sub.TLabel").pack(side="left", pady=(6, 0))

        # Divider
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(4, 10))

        # Main layout
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Left panel
        left = ttk.Frame(main, style="Surface.TFrame", width=260)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)
        self._build_left_panel(left)

        # Right panel
        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)
        self._build_right_panel(right)

        # Status bar
        self._status_var = tk.StringVar(value="Ready. Select a category and click Scrape.")
        status_bar = ttk.Frame(self.root, style="Surface2.TFrame")
        status_bar.pack(fill="x", side="bottom")
        ttk.Label(status_bar, textvariable=self._status_var, style="Status.TLabel",
                  padding=(12, 4)).pack(side="left")
        self._count_var = tk.StringVar(value="0 records")
        ttk.Label(status_bar, textvariable=self._count_var, style="Status.TLabel",
                  padding=(0, 4, 12, 4)).pack(side="right")

    def _build_left_panel(self, parent):
        pad = dict(padx=14, pady=6)

        # Section: Scrape
        ttk.Label(parent, text="── SCRAPE ──", foreground=TEXT_DIM,
                  background=SURFACE, font=("Consolas", 9)).pack(pady=(14, 4), padx=14, anchor="w")

        ttk.Label(parent, text="Category", background=SURFACE, font=("Consolas", 9),
                  foreground=TEXT_DIM).pack(anchor="w", **pad)
        self._cat_var = tk.StringVar(value="Jobs")
        self._cat_cb = ttk.Combobox(parent, textvariable=self._cat_var,
                                    values=list(SCRAPERS.keys()), state="readonly", width=22)
        self._cat_cb.pack(**pad)
        self._cat_cb.bind("<<ComboboxSelected>>", lambda e: self._update_columns())

        ttk.Label(parent, text="Max Pages", background=SURFACE, font=("Consolas", 9),
                  foreground=TEXT_DIM).pack(anchor="w", **pad)
        self._pages_var = tk.IntVar(value=2)
        pages_frame = ttk.Frame(parent, style="Surface.TFrame")
        pages_frame.pack(**pad)
        ttk.Scale(pages_frame, from_=1, to=10, orient="horizontal",
                  variable=self._pages_var, length=180).pack(side="left")
        self._pages_lbl = ttk.Label(pages_frame, textvariable=self._pages_var,
                                    background=SURFACE, foreground=ACCENT, font=("Consolas", 10, "bold"))
        self._pages_lbl.pack(side="left", padx=(6, 0))

        self._scrape_btn = ttk.Button(parent, text="▶  SCRAPE NOW", style="Accent.TButton",
                                      command=self._start_scrape, width=24)
        self._scrape_btn.pack(padx=14, pady=10)

        self._progress = ttk.Progressbar(parent, mode="indeterminate", length=200)
        self._progress.pack(**pad)

        # Divider
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=14, pady=8)

        # Section: Filter
        ttk.Label(parent, text="── FILTER ──", foreground=TEXT_DIM,
                  background=SURFACE, font=("Consolas", 9)).pack(pady=(4, 4), padx=14, anchor="w")

        ttk.Label(parent, text="Keyword", background=SURFACE, font=("Consolas", 9),
                  foreground=TEXT_DIM).pack(anchor="w", **pad)
        self._kw_var = tk.StringVar()
        kw_entry = ttk.Entry(parent, textvariable=self._kw_var, width=24)
        kw_entry.pack(**pad)
        kw_entry.bind("<Return>", lambda e: self._apply_filter())

        ttk.Button(parent, text="🔍  SEARCH", style="Accent.TButton",
                   command=self._apply_filter, width=24).pack(**pad)
        ttk.Button(parent, text="✕  CLEAR FILTER", style="Danger.TButton",
                   command=self._clear_filter, width=24).pack(**pad)

        # Divider
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=14, pady=8)

        # Section: Save
        ttk.Label(parent, text="── SAVE ──", foreground=TEXT_DIM,
                  background=SURFACE, font=("Consolas", 9)).pack(pady=(4, 4), padx=14, anchor="w")

        ttk.Label(parent, text="Format", background=SURFACE, font=("Consolas", 9),
                  foreground=TEXT_DIM).pack(anchor="w", **pad)
        self._fmt_var = tk.StringVar(value="both")
        fmt_cb = ttk.Combobox(parent, textvariable=self._fmt_var, state="readonly", width=22,
                               values=["json", "csv", "excel", "both", "all"])
        fmt_cb.pack(**pad)

        ttk.Button(parent, text="💾  SAVE DATA", style="Save.TButton",
                   command=self._save_data, width=24).pack(padx=14, pady=10)

    def _build_right_panel(self, parent):
        # Stats row
        stats = ttk.Frame(parent)
        stats.pack(fill="x", pady=(0, 8))

        self._stat_total = self._make_stat(stats, "TOTAL", "0")
        self._stat_filtered = self._make_stat(stats, "FILTERED", "0")
        self._stat_source = self._make_stat(stats, "SOURCES", "—")
        self._stat_time = self._make_stat(stats, "LAST RUN", "—")

        # Treeview
        tree_frame = ttk.Frame(parent, style="Surface.TFrame")
        tree_frame.pack(fill="both", expand=True)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        self._tree = ttk.Treeview(tree_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set,
                                  selectmode="browse", show="headings")
        self._tree.pack(fill="both", expand=True)
        vsb.config(command=self._tree.yview)
        hsb.config(command=self._tree.xview)

        # Zebra stripe tag
        self._tree.tag_configure("odd", background="#1c2128")
        self._tree.tag_configure("even", background=SURFACE)

        # Log panel
        log_frame = ttk.Frame(parent, style="Surface2.TFrame", height=120)
        log_frame.pack(fill="x", pady=(8, 0))
        log_frame.pack_propagate(False)
        ttk.Label(log_frame, text="  LOG", background=SURFACE2, foreground=TEXT_DIM,
                  font=("Consolas", 8)).pack(anchor="w", padx=8, pady=(4, 0))
        self._log_text = tk.Text(log_frame, bg=SURFACE2, fg=TEXT_DIM, font=("Consolas", 8),
                                 relief="flat", state="disabled", height=5, wrap="word")
        self._log_text.pack(fill="both", expand=True, padx=8, pady=(0, 4))

        self._update_columns()

    def _make_stat(self, parent, label, value):
        frame = ttk.Frame(parent, style="Surface2.TFrame")
        frame.pack(side="left", fill="x", expand=True, padx=4, pady=2, ipady=8)
        tk.Label(frame, text=value, bg=SURFACE2, fg=ACCENT, font=("Consolas", 18, "bold")).pack()
        tk.Label(frame, text=label, bg=SURFACE2, fg=TEXT_DIM, font=("Consolas", 8)).pack()

        # Store reference to value label
        val_label = frame.winfo_children()[0]
        return val_label

    # ── Helpers ────────────────────────────────────────────────────
    def _log(self, msg: str):
        self._log_text.config(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_text.insert("end", f"[{ts}] {msg}\n")
        self._log_text.see("end")
        self._log_text.config(state="disabled")

    def _set_status(self, msg: str):
        self._status_var.set(msg)

    def _update_columns(self):
        cat = self._cat_var.get()
        cols = COLUMNS.get(cat, [])
        self._tree.config(columns=cols)
        for col in cols:
            self._tree.heading(col, text=col.replace("_", " ").upper())
            self._tree.column(col, width=160, anchor="w", stretch=True)
        self._tree.delete(*self._tree.get_children())

    def _populate_tree(self, data: list):
        self._tree.delete(*self._tree.get_children())
        cat = self._cat_var.get()
        cols = COLUMNS.get(cat, [])
        for i, item in enumerate(data):
            values = [str(item.get(c, ""))[:80] for c in cols]
            tag = "odd" if i % 2 else "even"
            self._tree.insert("", "end", values=values, tags=(tag,))

        # Update stats
        sources = {item.get("source", "?") for item in data}
        self._stat_total["text"] = str(len(self._data))
        self._stat_filtered["text"] = str(len(data))
        self._stat_source["text"] = ", ".join(sorted(sources)) if sources else "—"
        self._count_var.set(f"{len(data)} records shown")

    # ── Actions ────────────────────────────────────────────────────
    def _start_scrape(self):
        if self._scraping:
            return
        self._scraping = True
        self._scrape_btn.config(state="disabled", text="⏳  SCRAPING...")
        self._progress.start(12)
        self._set_status("Scraping in progress — please wait...")
        threading.Thread(target=self._scrape_worker, daemon=True).start()

    def _scrape_worker(self):
        cat = self._cat_var.get()
        pages = self._pages_var.get()
        scraper = SCRAPERS[cat]
        start = datetime.now()
        try:
            self._log(f"Starting {cat} scrape (max_pages={pages})...")
            data = scraper(keyword="", max_pages=pages)
            self._data = data
            self._filtered = data[:]
            elapsed = (datetime.now() - start).seconds
            self.root.after(0, self._scrape_done, data, elapsed)
        except Exception as e:
            self.root.after(0, self._scrape_error, str(e))

    def _scrape_done(self, data: list, elapsed: int):
        self._scraping = False
        self._scrape_btn.config(state="normal", text="▶  SCRAPE NOW")
        self._progress.stop()
        self._populate_tree(data)
        self._stat_time["text"] = datetime.now().strftime("%H:%M")
        self._set_status(f"✅ Scraped {len(data)} records in {elapsed}s.")
        self._log(f"Done. {len(data)} records scraped.")
        self._update_columns()
        self._populate_tree(data)

    def _scrape_error(self, err: str):
        self._scraping = False
        self._scrape_btn.config(state="normal", text="▶  SCRAPE NOW")
        self._progress.stop()
        self._set_status(f"❌ Error: {err}")
        self._log(f"ERROR: {err}")
        messagebox.showerror("Scraping Error", err)

    def _apply_filter(self):
        if not self._data:
            messagebox.showwarning("No Data", "Please scrape data first.")
            return
        kw = self._kw_var.get().lower().strip()
        if not kw:
            self._filtered = self._data[:]
        else:
            self._filtered = [
                item for item in self._data
                if any(kw in str(v).lower() for v in item.values())
            ]
        self._populate_tree(self._filtered)
        self._set_status(f"🔍 Filter '{kw}': {len(self._filtered)} results.")
        self._log(f"Filter '{kw}' → {len(self._filtered)} results.")

    def _clear_filter(self):
        self._kw_var.set("")
        self._filtered = self._data[:]
        self._populate_tree(self._filtered)
        self._set_status("Filter cleared.")

    def _save_data(self):
        if not self._filtered:
            messagebox.showwarning("No Data", "Nothing to save yet.")
            return
        fmt = self._fmt_var.get()
        cat = self._cat_var.get().lower()
        try:
            saved = save_data(self._filtered, cat, fmt)
            paths = "\n".join(f"  {k.upper()}: {v}" for k, v in saved.items())
            messagebox.showinfo("Saved!", f"Data saved:\n\n{paths}")
            self._log(f"Saved {len(self._filtered)} records as {fmt.upper()}.")
            self._set_status(f"💾 Saved {len(self._filtered)} records.")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))


def main():
    root = tk.Tk()
    app = WebScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
