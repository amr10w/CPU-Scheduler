import tkinter as tk
from tkinter import ttk, messagebox
from collections import OrderedDict

from core.process import Process
from core.engine import Engine
from core.fcfs import FCFS
from core.sjf import SJFScheduler
from core.priority import PriorityScheduler
from core.roundroubin import RoundRobinScheduler


class MainWindow:

    # ── Theme ─────────────────────────────────────────────────────────
    THEME = {
        "bg":           "#0d1117",
        "bg2":          "#161b22",
        "surface":      "#1c2333",
        "surface2":     "#242d3d",
        "surface3":     "#2d3748",
        "accent":       "#6366f1",
        "accent_glow":  "#818cf8",
        "accent_dark":  "#4f46e5",
        "green":        "#22c55e",
        "green_dark":   "#16a34a",
        "red":          "#ef4444",
        "red_dark":     "#dc2626",
        "orange":       "#f97316",
        "orange_dark":  "#ea580c",
        "cyan":         "#06b6d4",
        "cyan_dark":    "#0891b2",
        "pink":         "#ec4899",
        "yellow":       "#eab308",
        "text":         "#f1f5f9",
        "text2":        "#94a3b8",
        "text3":        "#64748b",
        "border":       "#2a3444",
        "input_bg":     "#1e2736",
        "row1":         "#1c2333",
        "row2":         "#212b3d",
        "idle":         "#374151",
    }

    GANTT_PALETTE = [
        "#6366f1", "#22c55e", "#f97316", "#ec4899", "#06b6d4",
        "#eab308", "#a855f7", "#14b8a6", "#f43f5e", "#3b82f6",
        "#84cc16", "#e11d48", "#0ea5e9", "#d946ef", "#fb923c",
    ]

    ALGO_OPTIONS = [
        "FCFS",
        "SJF (Non-Preemptive)",
        "SJF (Preemptive / SRTF)",
        "Priority (Non-Preemptive)",
        "Priority (Preemptive)",
        "Round Robin",
    ]

    ALGO_FIELDS = {
        "FCFS":                       ["arrival", "burst"],
        "SJF (Non-Preemptive)":       ["arrival", "burst"],
        "SJF (Preemptive / SRTF)":    ["arrival", "burst"],
        "Priority (Non-Preemptive)":  ["arrival", "burst", "priority"],
        "Priority (Preemptive)":      ["arrival", "burst", "priority"],
        "Round Robin":                ["arrival", "burst"],
    }

    SPEED_OPTIONS = OrderedDict([
        ("0.25x (4s)", 4000),
        ("0.5x  (2s)", 2000),
        ("1x    (1s)", 1000),
        ("2x  (0.5s)", 500),
        ("4x (0.25s)", 250),
    ])

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("⚡ CPU Scheduler Simulator")
        self.root.configure(bg=self.THEME["bg"])

        # Center window on screen, large default size
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        ww = min(1400, sw - 100)
        wh = min(900, sh - 80)
        x = (sw - ww) // 2
        y = (sh - wh) // 2 - 20
        self.root.geometry(f"{ww}x{wh}+{x}+{y}")
        self.root.minsize(900, 650)

        self.pid_counter = 1
        self.process_data = []
        self.engine = None
        self.sim_timer = None
        self.is_playing = False
        self.is_paused = False
        self.sim_speed = 1000
        self.pid_colors = {}
        self.color_idx = 0
        self.dashboard_built = False

        self._setup_styles()
        self._build()
        self._on_algo_change()

    # ══════════════════════════════════════════════════════════════════
    #  STYLES
    # ══════════════════════════════════════════════════════════════════

    def _setup_styles(self):
        T = self.THEME
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=T["bg"])
        style.configure("TLabel", background=T["bg"], foreground=T["text"],
                        font=("Segoe UI", 10))
        style.configure("TCombobox",
                        fieldbackground=T["input_bg"],
                        background=T["surface2"],
                        foreground=T["text"],
                        borderwidth=1, arrowcolor=T["text2"])
        style.map("TCombobox",
                  fieldbackground=[("readonly", T["input_bg"])],
                  selectbackground=[("readonly", T["input_bg"])],
                  selectforeground=[("readonly", T["text"])])
        style.configure("TEntry",
                        fieldbackground=T["input_bg"],
                        foreground=T["text"],
                        insertcolor=T["text"], borderwidth=1)
        style.configure("Horizontal.TProgressbar",
                        background=T["accent"],
                        troughcolor=T["surface2"],
                        borderwidth=0, thickness=6)

    # ══════════════════════════════════════════════════════════════════
    #  RESPONSIVE SCROLLABLE LAYOUT
    # ══════════════════════════════════════════════════════════════════

    def _build(self):
        T = self.THEME

        # Outer container fills the entire window
        outer = tk.Frame(self.root, bg=T["bg"])
        outer.pack(fill=tk.BOTH, expand=True)

        # Canvas + scrollbar
        self.main_canvas = tk.Canvas(outer, bg=T["bg"], highlightthickness=0)
        vsb = tk.Scrollbar(outer, orient=tk.VERTICAL, command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Inner frame inside canvas
        self.scroll_inner = tk.Frame(self.main_canvas, bg=T["bg"])
        self.canvas_window = self.main_canvas.create_window(
            (0, 0), window=self.scroll_inner, anchor=tk.NW
        )

        # Make scroll_inner always match canvas width
        def _on_canvas_resize(event):
            self.main_canvas.itemconfig(self.canvas_window, width=event.width)
        self.main_canvas.bind("<Configure>", _on_canvas_resize)

        self.scroll_inner.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        # Mousewheel
        def _mw(e):
            self.main_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        self.main_canvas.bind_all("<MouseWheel>", _mw)
        self.main_canvas.bind_all("<Button-4>",
            lambda e: self.main_canvas.yview_scroll(-1, "units"))
        self.main_canvas.bind_all("<Button-5>",
            lambda e: self.main_canvas.yview_scroll(1, "units"))

        # Content with padding — expands to full width
        self.content = tk.Frame(self.scroll_inner, bg=T["bg"])
        self.content.pack(fill=tk.BOTH, expand=True, padx=32, pady=24)

        # Build all sections
        self._build_header()
        self._build_setup_section()
        self._build_process_input()
        self._build_process_table()
        self._build_controls()
        self._build_live_dashboard()

    # ── Header ────────────────────────────────────────────────────────

    def _build_header(self):
        T = self.THEME
        hdr = tk.Frame(self.content, bg=T["bg"])
        hdr.pack(fill=tk.X, pady=(0, 22))

        left = tk.Frame(hdr, bg=T["bg"])
        left.pack(side=tk.LEFT)
        tk.Label(left, text="⚡", bg=T["bg"], fg=T["accent_glow"],
                 font=("Segoe UI", 30)).pack(side=tk.LEFT, padx=(0, 10))
        tb = tk.Frame(left, bg=T["bg"])
        tb.pack(side=tk.LEFT)
        tk.Label(tb, text="CPU Scheduler Simulator", bg=T["bg"],
                 fg=T["text"], font=("Segoe UI", 22, "bold")).pack(anchor=tk.W)
        tk.Label(tb, text="Visualize scheduling algorithms in real-time",
                 bg=T["bg"], fg=T["text3"], font=("Segoe UI", 10)).pack(anchor=tk.W)

        # Status badge — right side
        self.status_frame = tk.Frame(hdr, bg=T["bg"])
        self.status_frame.pack(side=tk.RIGHT)
        self.status_dot = tk.Canvas(self.status_frame, width=14, height=14,
                                    bg=T["bg"], highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(0, 6))
        self.status_dot.create_oval(2, 2, 12, 12, fill=T["text3"], outline="", tags="dot")
        self.status_label = tk.Label(self.status_frame, text="Ready",
                                     bg=T["bg"], fg=T["text3"],
                                     font=("Segoe UI", 11, "bold"))
        self.status_label.pack(side=tk.LEFT)

    def _set_status(self, text, color):
        self.status_dot.delete("dot")
        self.status_dot.create_oval(2, 2, 12, 12, fill=color, outline="", tags="dot")
        self.status_label.configure(text=text, fg=color)

    # ── Configuration ─────────────────────────────────────────────────

    def _build_setup_section(self):
        T = self.THEME
        card = self._card(self.content)
        card.pack(fill=tk.X, pady=(0, 14))

        inner = tk.Frame(card, bg=T["surface"])
        inner.pack(fill=tk.X, padx=24, pady=18)

        tk.Label(inner, text="⚙  Configuration", bg=T["surface"], fg=T["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor=tk.W, pady=(0, 14))

        row = tk.Frame(inner, bg=T["surface"])
        row.pack(fill=tk.X)

        # Algorithm
        self.algo_grp = self._field_group(row, "ALGORITHM")
        self.algo_var = tk.StringVar(value="FCFS")
        ttk.Combobox(self.algo_grp, textvariable=self.algo_var,
                     values=self.ALGO_OPTIONS, state="readonly",
                     width=30).pack(fill=tk.X)
        self.algo_grp.children_combo = self.algo_grp.winfo_children()[-1]
        self.algo_grp.children_combo.bind("<<ComboboxSelected>>", self._on_algo_change)
        self.algo_grp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 16))

        # Time Quantum
        self.tq_grp = self._field_group(row, "TIME QUANTUM")
        self.tq_var = tk.StringVar(value="2")
        ttk.Entry(self.tq_grp, textvariable=self.tq_var, width=10).pack(fill=tk.X)

        # Speed
        self.speed_grp = self._field_group(row, "SIMULATION SPEED")
        self.speed_var = tk.StringVar(value="1x    (1s)")
        cb = ttk.Combobox(self.speed_grp, textvariable=self.speed_var,
                          values=list(self.SPEED_OPTIONS.keys()),
                          state="readonly", width=16)
        cb.pack(fill=tk.X)
        cb.bind("<<ComboboxSelected>>", self._on_speed_change)
        self.speed_grp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 16))

        # Generate
        gen_grp = self._field_group(row, "QUICK GENERATE")
        gen_row = tk.Frame(gen_grp, bg=T["surface"])
        gen_row.pack(fill=tk.X)
        self.count_var = tk.StringVar(value="3")
        ttk.Entry(gen_row, textvariable=self.count_var, width=5).pack(side=tk.LEFT, padx=(0, 6))
        self._sm_btn(gen_row, "Generate", T["accent"], T["accent_dark"],
                     self._generate_inputs).pack(side=tk.LEFT, fill=tk.X, expand=True)
        gen_grp.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _on_algo_change(self, _=None):
        algo = self.algo_var.get()
        if algo == "Round Robin":
            self.tq_grp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 16),
                             after=self.algo_grp)
        else:
            self.tq_grp.pack_forget()
        self._update_input_fields()
        self._rebuild_table_header()
        self._rebuild_table_rows()

    def _on_speed_change(self, _=None):
        self.sim_speed = self.SPEED_OPTIONS.get(self.speed_var.get(), 1000)

    # ── Add Process ───────────────────────────────────────────────────

    def _build_process_input(self):
        T = self.THEME
        card = self._card(self.content)
        card.pack(fill=tk.X, pady=(0, 14))

        inner = tk.Frame(card, bg=T["surface"])
        inner.pack(fill=tk.X, padx=24, pady=18)

        top = tk.Frame(inner, bg=T["surface"])
        top.pack(fill=tk.X, pady=(0, 14))
        tk.Label(top, text="➕  Add Process", bg=T["surface"], fg=T["text"],
                 font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)
        tk.Label(top, text="(can add while simulation is running)",
                 bg=T["surface"], fg=T["text3"],
                 font=("Segoe UI", 9, "italic")).pack(side=tk.LEFT, padx=(12, 0))

        self.input_row = tk.Frame(inner, bg=T["surface"])
        self.input_row.pack(fill=tk.X)

        self.field_widgets = {}
        self.input_vars = {}

        for key, label, default in [("arrival", "ARRIVAL TIME", "0"),
                                     ("burst", "BURST TIME", "1"),
                                     ("priority", "PRIORITY", "0")]:
            grp = self._field_group(self.input_row, label)
            var = tk.StringVar(value=default)
            e = ttk.Entry(grp, textvariable=var, width=12)
            e.pack(fill=tk.X)
            e.bind("<Return>", lambda ev: self._add_process())
            self.input_vars[key] = var
            self.field_widgets[key] = grp

        # Buttons
        self.input_btn_grp = tk.Frame(self.input_row, bg=T["surface"])
        btn_inner = tk.Frame(self.input_btn_grp, bg=T["surface"])
        btn_inner.pack(side=tk.BOTTOM, pady=(0, 0))
        self._sm_btn(btn_inner, "＋ Add Process", T["green"], T["green_dark"],
                     self._add_process).pack(side=tk.LEFT, padx=(0, 8))
        self._sm_btn(btn_inner, "🗑 Clear All", T["red"], T["red_dark"],
                     self._clear_all).pack(side=tk.LEFT)

        self._update_input_fields()

    def _update_input_fields(self):
        algo = self.algo_var.get()
        needed = self.ALGO_FIELDS.get(algo, ["arrival", "burst"])

        for key, grp in self.field_widgets.items():
            grp.pack_forget()
        self.input_btn_grp.pack_forget()

        for key in ["arrival", "burst", "priority"]:
            if key in needed:
                self.field_widgets[key].pack(
                    side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 16))

        self.input_btn_grp.pack(side=tk.LEFT, padx=(8, 0), pady=(16, 0))

    # ── Process Table ─────────────────────────────────────────────────

    def _build_process_table(self):
        T = self.THEME
        card = self._card(self.content)
        card.pack(fill=tk.X, pady=(0, 14))

        inner = tk.Frame(card, bg=T["surface"])
        inner.pack(fill=tk.BOTH, expand=True, padx=24, pady=18)

        top = tk.Frame(inner, bg=T["surface"])
        top.pack(fill=tk.X, pady=(0, 10))
        tk.Label(top, text="📋  Process Queue", bg=T["surface"], fg=T["text"],
                 font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)
        self.proc_count_lbl = tk.Label(top, text="0 processes", bg=T["surface"],
                                        fg=T["text3"], font=("Segoe UI", 10))
        self.proc_count_lbl.pack(side=tk.RIGHT)

        # Header
        self.tbl_hdr_frame = tk.Frame(inner, bg=T["surface3"])
        self.tbl_hdr_frame.pack(fill=tk.X)
        self._rebuild_table_header()

        # Scrollable body
        cf = tk.Frame(inner, bg=T["surface"], height=140)
        cf.pack(fill=tk.BOTH, expand=True)
        cf.pack_propagate(False)

        self.tbl_canvas = tk.Canvas(cf, bg=T["surface"], highlightthickness=0)
        sb = tk.Scrollbar(cf, orient=tk.VERTICAL, command=self.tbl_canvas.yview)
        self.tbl_body = tk.Frame(self.tbl_canvas, bg=T["surface"])
        self.tbl_body.bind("<Configure>",
            lambda e: self.tbl_canvas.configure(scrollregion=self.tbl_canvas.bbox("all")))
        self.tbl_canvas_win = self.tbl_canvas.create_window(
            (0, 0), window=self.tbl_body, anchor=tk.NW)

        # Make body stretch to canvas width
        def _tbl_resize(event):
            self.tbl_canvas.itemconfig(self.tbl_canvas_win, width=event.width)
        self.tbl_canvas.bind("<Configure>", _tbl_resize)

        self.tbl_canvas.configure(yscrollcommand=sb.set)
        self.tbl_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tbl_empty = tk.Label(self.tbl_body,
            text="No processes yet — add one above or click Generate",
            bg=T["surface"], fg=T["text3"], font=("Segoe UI", 10), pady=28)
        self.tbl_empty.pack(fill=tk.X)
        self.tbl_rows = []

    def _rebuild_table_header(self):
        T = self.THEME
        for w in self.tbl_hdr_frame.winfo_children():
            w.destroy()
        algo = self.algo_var.get()
        needs_prio = "priority" in self.ALGO_FIELDS.get(algo, [])
        headers = ["PID", "Arrival", "Burst"]
        if needs_prio:
            headers.append("Priority")
        headers.append("")
        for h in headers:
            tk.Label(self.tbl_hdr_frame, text=h, bg=T["surface3"],
                     fg=T["text2"], font=("Segoe UI", 9, "bold"),
                     pady=8).pack(side=tk.LEFT, expand=True, fill=tk.X)

    def _insert_table_row(self, d):
        T = self.THEME
        if self.tbl_empty.winfo_ismapped():
            self.tbl_empty.pack_forget()

        idx = len(self.tbl_rows)
        bg = T["row1"] if idx % 2 == 0 else T["row2"]
        row = tk.Frame(self.tbl_body, bg=bg)
        row.pack(fill=tk.X)

        algo = self.algo_var.get()
        needs_prio = "priority" in self.ALGO_FIELDS.get(algo, [])

        vals = [d["pid"], str(d["arrival"]), str(d["burst"])]
        if needs_prio:
            vals.append(str(d["priority"]))

        for v in vals:
            tk.Label(row, text=v, bg=bg, fg=T["text"], font=("Segoe UI", 10),
                     pady=6).pack(side=tk.LEFT, expand=True, fill=tk.X)

        tk.Button(row, text="✕", bg=T["red"], fg="white",
                  font=("Segoe UI", 8, "bold"), bd=0, padx=10, pady=3,
                  cursor="hand2", activebackground=T["red_dark"],
                  command=lambda i=idx: self._remove_process(i)
        ).pack(side=tk.LEFT, expand=True, padx=6, pady=3)

        self.tbl_rows.append(row)
        self.proc_count_lbl.configure(text=f"{len(self.tbl_rows)} processes")

    def _remove_process(self, idx):
        if 0 <= idx < len(self.process_data):
            self.process_data.pop(idx)
            self._rebuild_table_rows()

    def _rebuild_table_rows(self):
        for r in self.tbl_rows:
            r.destroy()
        self.tbl_rows.clear()
        if not self.process_data:
            self.tbl_empty.pack(fill=tk.X)
        else:
            self.tbl_empty.pack_forget()
            for d in self.process_data:
                self._insert_table_row(d)
        self.proc_count_lbl.configure(text=f"{len(self.tbl_rows)} processes")

    # ── Controls ──────────────────────────────────────────────────────

    def _build_controls(self):
        T = self.THEME
        bar = tk.Frame(self.content, bg=T["bg"])
        bar.pack(fill=tk.X, pady=(6, 18))

        # Center the buttons
        center = tk.Frame(bar, bg=T["bg"])
        center.pack(anchor=tk.CENTER)

        self.play_btn = self._btn(center, "▶  Live Run", T["green"],
                                  T["green_dark"], self._toggle_play)
        self.play_btn.pack(side=tk.LEFT, padx=6)

        self.pause_btn = self._btn(center, "⏸  Pause", T["orange"],
                                   T["orange_dark"], self._toggle_pause)
        self.pause_btn.pack(side=tk.LEFT, padx=6)
        self.pause_btn.configure(state=tk.DISABLED)

        self.step_btn = self._btn(center, "⏭  Step", T["accent"],
                                  T["accent_dark"], self._step_once)
        self.step_btn.pack(side=tk.LEFT, padx=6)

        self.instant_btn = self._btn(center, "⚡ Run Instant", T["orange"],
                                     T["orange_dark"], self._run_instant)
        self.instant_btn.pack(side=tk.LEFT, padx=6)

        self.reset_btn = self._btn(center, "↺  Reset", T["red"],
                                   T["red_dark"], self._reset_sim)
        self.reset_btn.pack(side=tk.LEFT, padx=6)

    # ── Dashboard (results area) ──────────────────────────────────────

    def _build_live_dashboard(self):
        T = self.THEME
        self.dash_frame = tk.Frame(self.content, bg=T["bg"])
        self.dash_frame.pack(fill=tk.BOTH, expand=True)

        self.dash_placeholder = tk.Label(self.dash_frame,
            text="Run the simulation to see live results here",
            bg=T["bg"], fg=T["text3"], font=("Segoe UI", 12), pady=50)
        self.dash_placeholder.pack(fill=tk.X)

    def _init_dashboard(self):
        T = self.THEME
        if self.dashboard_built:
            return
        self.dash_placeholder.pack_forget()

        # ── Metrics ──────────────────────────────────────────────────
        self.metrics_frame = tk.Frame(self.dash_frame, bg=T["bg"])
        self.metrics_frame.pack(fill=tk.X, pady=(0, 14))

        self.metric_cards = {}
        defs = [
            ("clock",     "🕐 Clock",    "0",    T["cyan"]),
            ("running",   "▶ Running",   "—",    T["green"]),
            ("avg_wt",    "⏳ Avg WT",    "0.00", T["accent_glow"]),
            ("avg_tat",   "⏱ Avg TAT",   "0.00", T["pink"]),
            ("completed", "✓ Completed", "0/0",  T["yellow"]),
        ]
        for key, label, default, color in defs:
            card = tk.Frame(self.metrics_frame, bg=T["surface"],
                            highlightthickness=2, highlightbackground=color)
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 10))
            val_lbl = tk.Label(card, text=default, bg=T["surface"], fg=color,
                               font=("Segoe UI", 24, "bold"))
            val_lbl.pack(pady=(12, 2))
            tk.Label(card, text=label, bg=T["surface"], fg=T["text2"],
                     font=("Segoe UI", 9)).pack(pady=(0, 12))
            self.metric_cards[key] = val_lbl

        # ── Remaining Burst ──────────────────────────────────────────
        rbt_card = self._card(self.dash_frame)
        rbt_card.pack(fill=tk.X, pady=(0, 14))
        rbt_inner = tk.Frame(rbt_card, bg=T["surface"])
        rbt_inner.pack(fill=tk.X, padx=24, pady=16)
        tk.Label(rbt_inner, text="📊  Remaining Burst Times (Live)",
                 bg=T["surface"], fg=T["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor=tk.W, pady=(0, 10))
        self.rbt_container = tk.Frame(rbt_inner, bg=T["surface"])
        self.rbt_container.pack(fill=tk.X)

        # ── Gantt Chart ──────────────────────────────────────────────
        gantt_card = self._card(self.dash_frame)
        gantt_card.pack(fill=tk.X, pady=(0, 14))
        gantt_inner = tk.Frame(gantt_card, bg=T["surface"])
        gantt_inner.pack(fill=tk.X, padx=24, pady=16)
        tk.Label(gantt_inner, text="📈  Gantt Chart (Live)",
                 bg=T["surface"], fg=T["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor=tk.W, pady=(0, 10))
        gcf = tk.Frame(gantt_inner, bg=T["surface"])
        gcf.pack(fill=tk.X)
        self.gantt_canvas = tk.Canvas(gcf, bg=T["surface"], height=100,
                                      highlightthickness=0)
        self.gantt_hsb = tk.Scrollbar(gcf, orient=tk.HORIZONTAL,
                                      command=self.gantt_canvas.xview)
        self.gantt_canvas.configure(xscrollcommand=self.gantt_hsb.set)
        self.gantt_canvas.pack(fill=tk.X)
        self.gantt_hsb.pack(fill=tk.X)

        # ── Results Table ────────────────────────────────────────────
        res_card = self._card(self.dash_frame)
        res_card.pack(fill=tk.X, pady=(0, 14))
        res_inner = tk.Frame(res_card, bg=T["surface"])
        res_inner.pack(fill=tk.X, padx=24, pady=16)
        tk.Label(res_inner, text="📋  Process Results",
                 bg=T["surface"], fg=T["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor=tk.W, pady=(0, 10))
        self.res_table_frame = tk.Frame(res_inner, bg=T["surface"])
        self.res_table_frame.pack(fill=tk.X)

        self.dashboard_built = True

    # ══════════════════════════════════════════════════════════════════
    #  ACTIONS
    # ══════════════════════════════════════════════════════════════════

    def _add_process(self):
        algo = self.algo_var.get()
        needed = self.ALGO_FIELDS.get(algo, ["arrival", "burst"])
        try:
            a = int(self.input_vars["arrival"].get())
            b = int(self.input_vars["burst"].get())
            p = int(self.input_vars["priority"].get()) if "priority" in needed else 0
            if b <= 0:
                messagebox.showerror("Error", "Burst time must be > 0"); return
            if a < 0:
                messagebox.showerror("Error", "Arrival time must be >= 0"); return
        except ValueError:
            messagebox.showerror("Error", "Enter valid integers"); return

        pid_str = f"P{self.pid_counter}"
        self.pid_counter += 1
        d = {"pid": pid_str, "arrival": a, "burst": b, "priority": p}
        self.process_data.append(d)
        self._insert_table_row(d)

        # Inject into running engine
        if self.engine is not None and not self.engine.is_done():
            proc = Process(pid_str, a, b, p)
            self.engine.processes.append(proc)
            self.engine.scheduler.add_process(proc)

    def _clear_all(self):
        self._stop_timer()
        self.is_playing = False
        self.play_btn.configure(text="▶  Live Run", bg=self.THEME["green"],
                                activebackground=self.THEME["green_dark"])
        self.process_data.clear()
        self.pid_counter = 1
        self._rebuild_table_rows()
        self.engine = None
        self._clear_dashboard()
        self._set_status("Ready", self.THEME["text3"])

    def _generate_inputs(self):
        try:
            n = int(self.count_var.get())
            if n <= 0 or n > 50:
                messagebox.showerror("Error", "Enter 1-50"); return
        except ValueError:
            messagebox.showerror("Error", "Invalid number"); return

        import random
        algo = self.algo_var.get()
        needs_prio = "priority" in self.ALGO_FIELDS.get(algo, [])
        for _ in range(n):
            pid = f"P{self.pid_counter}"
            self.pid_counter += 1
            d = {
                "pid": pid,
                "arrival": random.randint(0, n * 2),
                "burst": random.randint(1, 10),
                "priority": random.randint(1, 5) if needs_prio else 0,
            }
            self.process_data.append(d)
            self._insert_table_row(d)

    # ── Engine ────────────────────────────────────────────────────────

    def _build_engine(self):
        algo = self.algo_var.get()
        engine = Engine()
        for d in self.process_data:
            engine.add_process(d["pid"], d["arrival"], d["burst"], d["priority"])

        if algo == "FCFS":
            s = FCFS()
        elif algo == "SJF (Non-Preemptive)":
            s = SJFScheduler(preemptive=False)
        elif algo == "SJF (Preemptive / SRTF)":
            s = SJFScheduler(preemptive=True)
        elif algo == "Priority (Non-Preemptive)":
            s = PriorityScheduler(preemptive=False)
        elif algo == "Priority (Preemptive)":
            s = PriorityScheduler(preemptive=True)
        elif algo == "Round Robin":
            try:
                q = int(self.tq_var.get())
                if q <= 0: raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Time quantum must be positive integer")
                return None
            s = RoundRobinScheduler(quantum=q)
        else:
            return None

        engine.set_scheduler(s)
        return engine

    def _ensure_engine(self):
        if not self.process_data:
            messagebox.showwarning("Warning", "Add at least one process"); return False
        if self.engine is None or self.engine.is_done():
            self.engine = self._build_engine()
            if self.engine is None: return False
            self.pid_colors.clear()
            self.color_idx = 0
            self.engine.start()
            self._init_dashboard()
        return True

    # ── Play / Pause ──────────────────────────────────────────────────

    def _toggle_play(self):
        if self.is_playing:
            self._pause()
        else:
            self._play()

    def _play(self):
        if not self._ensure_engine(): return
        self.is_playing = True
        self.is_paused = False
        self.play_btn.configure(text="⏹  Stop", bg=self.THEME["red"],
                                activebackground=self.THEME["red_dark"])
        self.pause_btn.configure(state=tk.NORMAL)
        self._set_status("Running", self.THEME["green"])
        self._tick_loop()

    def _pause(self):
        self._stop_timer()
        self.is_playing = False
        self.play_btn.configure(text="▶  Live Run", bg=self.THEME["green"],
                                activebackground=self.THEME["green_dark"])
        self.pause_btn.configure(state=tk.DISABLED)
        self.is_paused = False
        self._set_status("Stopped", self.THEME["yellow"])

    def _toggle_pause(self):
        if self.is_paused:
            self._resume_from_pause()
        else:
            self._pause_simulation()

    def _pause_simulation(self):
        self._stop_timer()
        self.is_paused = True
        self.pause_btn.configure(text="▶  Resume", bg=self.THEME["green"],
                                 activebackground=self.THEME["green_dark"])
        self._set_status("Paused", self.THEME["yellow"])

    def _resume_from_pause(self):
        self.is_paused = False
        self.pause_btn.configure(text="⏸  Pause", bg=self.THEME["orange"],
                                 activebackground=self.THEME["orange_dark"])
        self._set_status("Running", self.THEME["green"])
        self._tick_loop()

    def _tick_loop(self):
    def _tick_loop(self):
        if not self.is_playing or self.is_paused or self.engine is None: return
        if self.engine.is_done():
            self.is_playing = False
            self.is_paused = False
            self.play_btn.configure(text="▶  Live Run", bg=self.THEME["green"],
                                    activebackground=self.THEME["green_dark"])
            self.pause_btn.configure(text="⏸  Pause", bg=self.THEME["orange"],
                                     activebackground=self.THEME["orange_dark"],
                                     state=tk.DISABLED)
            self._set_status("Completed ✓", self.THEME["green"])
            self._update_dashboard()
            return
        self.engine.step()
        self._update_dashboard()
        self.sim_timer = self.root.after(self.sim_speed, self._tick_loop)

    # ── Step ──────────────────────────────────────────────────────────

    def _step_once(self):
        if not self._ensure_engine(): return
        if self.engine.is_done():
            self._set_status("Completed ✓", self.THEME["green"]); return
        self._set_status("Stepping", self.THEME["cyan"])
        self.engine.step()
        self._update_dashboard()
        if self.engine.is_done():
            self._set_status("Completed ✓", self.THEME["green"])

    # ── Instant ───────────────────────────────────────────────────────

    def _run_instant(self):
        if not self.process_data:
            messagebox.showwarning("Warning", "Add at least one process"); return
        self._stop_timer()
        self.is_playing = False
        self.is_paused = False
        self.play_btn.configure(text="▶  Live Run", bg=self.THEME["green"],
                                activebackground=self.THEME["green_dark"])
        self.pause_btn.configure(state=tk.DISABLED)
        self.engine = self._build_engine()
        if self.engine is None: return
        self.pid_colors.clear()
        self.color_idx = 0
        self._init_dashboard()
        try:
            self.engine.run_all()
        except Exception as ex:
            messagebox.showerror("Error", str(ex)); return
        self._set_status("Completed ✓", self.THEME["green"])
        self._update_dashboard()

    # ── Reset ─────────────────────────────────────────────────────────

    def _reset_sim(self):
        self._stop_timer()
        self.is_playing = False
        self.is_paused = False
        self.play_btn.configure(text="▶  Live Run", bg=self.THEME["green"],
                                activebackground=self.THEME["green_dark"])
        self.pause_btn.configure(text="⏸  Pause", bg=self.THEME["orange"],
                                 activebackground=self.THEME["orange_dark"],
                                 state=tk.DISABLED)
        self.engine = None
        self.pid_colors.clear()
        self.color_idx = 0
        self._clear_dashboard()
        self._set_status("Ready", self.THEME["text3"])

    def _stop_timer(self):
        if self.sim_timer is not None:
            self.root.after_cancel(self.sim_timer)
            self.sim_timer = None

    # ══════════════════════════════════════════════════════════════════
    #  DASHBOARD UPDATE
    # ══════════════════════════════════════════════════════════════════

    def _clear_dashboard(self):
        if not self.dashboard_built: return
        for lbl in self.metric_cards.values():
            lbl.configure(text="—")
        for w in self.rbt_container.winfo_children(): w.destroy()
        self.gantt_canvas.delete("all")
        for w in self.res_table_frame.winfo_children(): w.destroy()

    def _update_dashboard(self):
        if self.engine is None or not self.dashboard_built: return
        T = self.THEME
        sched = self.engine.scheduler
        stats = self.engine.get_stats()
        ptable = self.engine.get_process_table()

        total = len(self.engine.processes)
        done = sum(1 for p in self.engine.processes if p.is_completed)
        running_pid = sched.current_process.pid if sched.current_process else "—"

        self.metric_cards["clock"].configure(text=str(sched.current_time))
        self.metric_cards["running"].configure(text=running_pid)
        self.metric_cards["avg_wt"].configure(text=f"{stats['avg_waiting']:.2f}")
        self.metric_cards["avg_tat"].configure(text=f"{stats['avg_turnaround']:.2f}")
        self.metric_cards["completed"].configure(text=f"{done}/{total}")

        # ── Remaining Burst Table ────────────────────────────────────
        for w in self.rbt_container.winfo_children(): w.destroy()

        hdr = tk.Frame(self.rbt_container, bg=T["surface3"])
        hdr.pack(fill=tk.X)
        for h in ("PID", "Burst", "Remaining", "Progress"):
            tk.Label(hdr, text=h, bg=T["surface3"], fg=T["text2"],
                     font=("Segoe UI", 9, "bold"), pady=7).pack(
                side=tk.LEFT, expand=True, fill=tk.X)

        for i, p in enumerate(self.engine.processes):
            bg = T["row1"] if i % 2 == 0 else T["row2"]
            r = tk.Frame(self.rbt_container, bg=bg)
            r.pack(fill=tk.X)

            is_running = sched.current_process and sched.current_process.pid == p.pid
            pid_fg = T["green"] if is_running else (T["text3"] if p.is_completed else T["text"])
            prefix = "▶ " if is_running else ("✓ " if p.is_completed else "  ")

            tk.Label(r, text=prefix + p.pid, bg=bg, fg=pid_fg,
                     font=("Segoe UI", 10, "bold"), pady=5).pack(
                side=tk.LEFT, expand=True, fill=tk.X)
            tk.Label(r, text=str(p.burst_time), bg=bg, fg=T["text"],
                     font=("Segoe UI", 10), pady=5).pack(
                side=tk.LEFT, expand=True, fill=tk.X)

            rem = "Done" if p.is_completed else str(p.remaining_time)
            rem_fg = T["green"] if p.is_completed else (
                T["orange"] if p.remaining_time < p.burst_time else T["text"])
            tk.Label(r, text=rem, bg=bg, fg=rem_fg,
                     font=("Segoe UI", 10, "bold"), pady=5).pack(
                side=tk.LEFT, expand=True, fill=tk.X)

            pf = tk.Frame(r, bg=bg)
            pf.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(8, 16), pady=5)
            pct = ((p.burst_time - p.remaining_time) / p.burst_time * 100) if p.burst_time > 0 else 0
            pb = ttk.Progressbar(pf, length=140, mode="determinate")
            pb.pack(fill=tk.X)
            pb["value"] = pct

        # ── Gantt ────────────────────────────────────────────────────
        self._draw_gantt(stats["gantt"])

        # ── Results Table ────────────────────────────────────────────
        for w in self.res_table_frame.winfo_children(): w.destroy()

        algo = self.algo_var.get()
        needs_prio = "priority" in self.ALGO_FIELDS.get(algo, [])

        hdrs = ["PID", "Arrival", "Burst"]
        if needs_prio: hdrs.append("Priority")
        hdrs.extend(["Completion", "Waiting", "Turnaround"])

        hrow = tk.Frame(self.res_table_frame, bg=T["surface3"])
        hrow.pack(fill=tk.X)
        for h in hdrs:
            tk.Label(hrow, text=h, bg=T["surface3"], fg=T["text2"],
                     font=("Segoe UI", 9, "bold"), pady=7).pack(
                side=tk.LEFT, expand=True, fill=tk.X)

        for i, p in enumerate(ptable):
            bg = T["row1"] if i % 2 == 0 else T["row2"]
            r = tk.Frame(self.res_table_frame, bg=bg)
            r.pack(fill=tk.X)
            vals = [p["pid"], str(p["arrival"]), str(p["burst"])]
            if needs_prio: vals.append(str(p["priority"]))
            c = p["completion"]
            vals.extend([
                str(c) if c > 0 else "—",
                str(p["waiting"]) if c > 0 else "—",
                str(p["turnaround"]) if c > 0 else "—",
            ])
            for v in vals:
                fg = T["text"] if v != "—" else T["text3"]
                tk.Label(r, text=v, bg=bg, fg=fg, font=("Segoe UI", 10),
                         pady=5).pack(side=tk.LEFT, expand=True, fill=tk.X)

    def _draw_gantt(self, gantt_data):
        T = self.THEME
        self.gantt_canvas.delete("all")
        if not gantt_data: return

        blocks = []
        for entry in gantt_data:
            pid, t = entry["pid"], entry["time"]
            if blocks and blocks[-1]["pid"] == pid:
                blocks[-1]["end"] = t + 1
            else:
                blocks.append({"pid": pid, "start": t, "end": t + 1})

        max_t = blocks[-1]["end"]
        unit_w = 52
        total_w = max_t * unit_w + 80
        self.gantt_canvas.configure(scrollregion=(0, 0, total_w, 100))

        x0, y1, y2 = 30, 16, 58

        for b in blocks:
            pid = b["pid"]
            if pid not in self.pid_colors:
                self.pid_colors[pid] = (
                    T["idle"] if pid == "Idle"
                    else self.GANTT_PALETTE[self.color_idx % len(self.GANTT_PALETTE)]
                )
                if pid != "Idle": self.color_idx += 1

            lx = x0 + b["start"] * unit_w
            rx = x0 + b["end"] * unit_w
            col = self.pid_colors[pid]

            self.gantt_canvas.create_rectangle(lx, y1, rx, y2, fill=col,
                                               outline=T["bg"], width=2)
            self.gantt_canvas.create_text((lx+rx)/2, (y1+y2)/2, text=pid,
                                          fill="white", font=("Segoe UI", 10, "bold"))
            self.gantt_canvas.create_text(lx, y2+14, text=str(b["start"]),
                                          fill=T["text2"], font=("Segoe UI", 8))

        self.gantt_canvas.create_text(x0 + max_t * unit_w, y2+14,
                                      text=str(max_t), fill=T["text2"],
                                      font=("Segoe UI", 8))
        self.gantt_canvas.xview_moveto(1.0)

    # ══════════════════════════════════════════════════════════════════
    #  WIDGET HELPERS
    # ══════════════════════════════════════════════════════════════════

    def _card(self, parent):
        T = self.THEME
        return tk.Frame(parent, bg=T["surface"], highlightthickness=1,
                        highlightbackground=T["border"])

    def _field_group(self, parent, label):
        T = self.THEME
        grp = tk.Frame(parent, bg=T["surface"])
        tk.Label(grp, text=label, bg=T["surface"], fg=T["text3"],
                 font=("Segoe UI", 8, "bold")).pack(anchor=tk.W, pady=(0, 4))
        return grp

    def _btn(self, parent, text, bg, bg_h, cmd):
        b = tk.Button(parent, text=text, bg=bg, fg="white",
                      font=("Segoe UI", 11, "bold"), bd=0,
                      padx=22, pady=10, cursor="hand2", command=cmd,
                      activebackground=bg_h, activeforeground="white")
        b.bind("<Enter>", lambda e, b=b, c=bg_h: b.configure(bg=c))
        b.bind("<Leave>", lambda e, b=b, c=bg: b.configure(bg=c))
        return b

    def _sm_btn(self, parent, text, bg, bg_h, cmd):
        b = tk.Button(parent, text=text, bg=bg, fg="white",
                      font=("Segoe UI", 9, "bold"), bd=0,
                      padx=14, pady=6, cursor="hand2", command=cmd,
                      activebackground=bg_h, activeforeground="white")
        b.bind("<Enter>", lambda e, b=b, c=bg_h: b.configure(bg=c))
        b.bind("<Leave>", lambda e, b=b, c=bg: b.configure(bg=c))
        return b

    def run(self):
        self.root.mainloop()
