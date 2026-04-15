"""
Main Application - Connects all GUI components to core/ engine.
Scrollable, responsive, with live simulation support.
Includes built-in test cases for each scheduler.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import platform

from core.process import Process
from core.base_scheduler import BaseScheduler
from core.fcfs import FCFS
from core.sjf import SJFScheduler
from core.priority import PriorityScheduler
from core.roundroubin import RoundRobinScheduler
from ui.input_panel import InputPanel
from ui.gantt_chart import GanttChart
from ui.process_table import ProcessTable
from ui.stats_panel import StatsPanel
from ui.test_cases import TEST_CASES, get_test_case, get_all_test_names


class CPUSchedulerApp:

    SCHEDULER_TYPES = {
        "FCFS": "fcfs",
        "SJF (Non-Preemptive)": "sjf_np",
        "SJF (Preemptive)": "sjf_p",
        "Priority (Non-Preemptive)": "priority_np",
        "Priority (Preemptive)": "priority_p",
        "Round Robin": "rr",
    }

    SCHEDULER_NAMES = {
        "fcfs": "FCFS",
        "sjf_np": "SJF (Non-Preemptive)",
        "sjf_p": "SJF (Preemptive / SRTF)",
        "priority_np": "Priority (Non-Preemptive)",
        "priority_p": "Priority (Preemptive)",
        "rr": "Round Robin",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduler Simulator")
        self.root.configure(bg="#2d2d30")

        # Center on screen
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        ww = min(1350, sw - 80)
        wh = min(880, sh - 80)
        x = (sw - ww) // 2
        y = (sh - wh) // 2 - 20
        self.root.geometry(f"{ww}x{wh}+{x}+{y}")
        self.root.minsize(1100, 700)

        # State
        self.scheduler = None
        self.sched_type_key = None
        self.is_live_running = False
        self.is_paused = False
        self.sim_timer = None
        self.process_counter = 0

        # Build
        self._build_scrollable_container()
        self._build_control_bar()
        self._build_input_area()
        self._build_button_bar()
        self._build_gantt_chart()
        self._build_bottom_area()

    # ══════════════════════════════════════════════════════════════════
    #  SCROLLABLE CONTAINER
    # ══════════════════════════════════════════════════════════════════

    def _build_scrollable_container(self):
        self.outer_frame = tk.Frame(self.root, bg="#2d2d30")
        self.outer_frame.pack(fill=tk.BOTH, expand=True)

        self.main_canvas = tk.Canvas(
            self.outer_frame, bg="#2d2d30", highlightthickness=0
        )
        self.v_scrollbar = ttk.Scrollbar(
            self.outer_frame, orient=tk.VERTICAL,
            command=self.main_canvas.yview
        )
        self.main_frame = tk.Frame(self.main_canvas, bg="#2d2d30")

        self.main_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )
        self.canvas_window = self.main_canvas.create_window(
            (0, 0), window=self.main_frame, anchor="nw"
        )
        self.main_canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.main_canvas.bind("<Configure>", self._on_canvas_configure)
        self._bind_mousewheel()

    def _on_canvas_configure(self, event):
        self.main_canvas.itemconfig(self.canvas_window, width=event.width)

    def _bind_mousewheel(self):
        system = platform.system()
        if system == "Windows":
            self.main_canvas.bind_all(
                "<MouseWheel>",
                lambda e: self.main_canvas.yview_scroll(
                    int(-1 * (e.delta / 120)), "units"
                )
            )
        elif system == "Darwin":
            self.main_canvas.bind_all(
                "<MouseWheel>",
                lambda e: self.main_canvas.yview_scroll(
                    int(-1 * e.delta), "units"
                )
            )
        else:
            self.main_canvas.bind_all(
                "<Button-4>",
                lambda e: self.main_canvas.yview_scroll(-1, "units")
            )
            self.main_canvas.bind_all(
                "<Button-5>",
                lambda e: self.main_canvas.yview_scroll(1, "units")
            )

    # ══════════════════════════════════════════════════════════════════
    #  GUI BUILD
    # ══════════════════════════════════════════════════════════════════

    def _build_control_bar(self):
        frame = tk.Frame(self.main_frame, bg="#3c3c3c", padx=10, pady=8)
        frame.pack(fill=tk.X, padx=5, pady=(5, 2))

        # Row 1: Scheduler + Quantum + Num Processes + SetUp
        row1 = tk.Frame(frame, bg="#3c3c3c")
        row1.pack(fill=tk.X)

        tk.Label(
            row1, text="Scheduler:", bg="#3c3c3c", fg="white",
            font=("Segoe UI", 11)
        ).pack(side=tk.LEFT, padx=(5, 3))

        self.scheduler_var = tk.StringVar(value="FCFS")
        self.scheduler_combo = ttk.Combobox(
            row1, textvariable=self.scheduler_var,
            values=list(self.SCHEDULER_TYPES.keys()),
            state="readonly", width=25, font=("Segoe UI", 10)
        )
        self.scheduler_combo.pack(side=tk.LEFT, padx=5)
        self.scheduler_combo.bind("<<ComboboxSelected>>", self._on_scheduler_change)

        self.quantum_frame = tk.Frame(row1, bg="#3c3c3c")
        tk.Label(
            self.quantum_frame, text="Time Quantum:", bg="#3c3c3c",
            fg="white", font=("Segoe UI", 11)
        ).pack(side=tk.LEFT, padx=(10, 3))
        self.quantum_entry = tk.Entry(
            self.quantum_frame, width=5,
            font=("Segoe UI", 10), justify=tk.CENTER
        )
        self.quantum_entry.pack(side=tk.LEFT, padx=3)
        self.quantum_entry.insert(0, "2")

        tk.Label(
            row1, text="Number of Processes:", bg="#3c3c3c",
            fg="white", font=("Segoe UI", 11)
        ).pack(side=tk.LEFT, padx=(30, 3))

        self.num_processes_entry = tk.Entry(
            row1, width=5, font=("Segoe UI", 10), justify=tk.CENTER
        )
        self.num_processes_entry.pack(side=tk.LEFT, padx=3)

        tk.Button(
            row1, text="Set Up", command=self._setup_processes,
            bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
            padx=12, pady=2, cursor="hand2"
        ).pack(side=tk.LEFT, padx=10)

        # Separator
        tk.Frame(frame, bg="#555555", height=1).pack(fill=tk.X, pady=(8, 6))

        # Row 2: Test Case loader
        row2 = tk.Frame(frame, bg="#3c3c3c")
        row2.pack(fill=tk.X)

        tk.Label(
            row2, text="📝 Load Test Case:", bg="#3c3c3c", fg="#FFEAA7",
            font=("Segoe UI", 10, "bold")
        ).pack(side=tk.LEFT, padx=(5, 6))

        test_names = [f"{k}" for k in TEST_CASES.keys()]
        self.test_var = tk.StringVar(value="")
        self.test_combo = ttk.Combobox(
            row2, textvariable=self.test_var,
            values=test_names,
            state="readonly", width=28, font=("Segoe UI", 10)
        )
        self.test_combo.pack(side=tk.LEFT, padx=3)
        self.test_combo.set("-- Select a test case --")

        tk.Button(
            row2, text="Load & Run Live",
            command=lambda: self._load_test_case(instant=False),
            bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"),
            padx=10, pady=2, cursor="hand2"
        ).pack(side=tk.LEFT, padx=6)

        tk.Button(
            row2, text="Load & Run Instant",
            command=lambda: self._load_test_case(instant=True),
            bg="#FF9800", fg="white", font=("Segoe UI", 10, "bold"),
            padx=10, pady=2, cursor="hand2"
        ).pack(side=tk.LEFT, padx=3)

        tk.Button(
            row2, text="ℹ Info",
            command=self._show_test_info,
            bg="#607D8B", fg="white", font=("Segoe UI", 10, "bold"),
            padx=8, pady=2, cursor="hand2"
        ).pack(side=tk.LEFT, padx=3)

    def _build_input_area(self):
        self.input_panel = InputPanel(self.main_frame)
        self.input_panel.pack(fill=tk.X, padx=5, pady=2)

    def _build_button_bar(self):
        frame = tk.Frame(self.main_frame, bg="#2d2d30", pady=5)
        frame.pack(fill=tk.X, padx=5, pady=2)

        btn_style = {
            "font": ("Segoe UI", 11, "bold"),
            "padx": 15, "pady": 5,
            "cursor": "hand2",
            "relief": tk.FLAT,
        }

        self.start_btn = tk.Button(
            frame, text="▶  Start Live",
            command=self._start_live,
            bg="#2196F3", fg="white", **btn_style
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.instant_btn = tk.Button(
            frame, text="⚡  Run Instantly",
            command=self._run_instant,
            bg="#FF9800", fg="white", **btn_style
        )
        self.instant_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(
            frame, text="⏹  Stop",
            command=self._stop_simulation,
            bg="#f44336", fg="white",
            state=tk.DISABLED, **btn_style
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = tk.Button(
            frame, text="⏸  Pause",
            command=self._toggle_pause,
            bg="#FF9800", fg="white",
            state=tk.DISABLED, **btn_style
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.add_btn = tk.Button(
            frame, text="➕  Add Process",
            command=self._add_process_dynamic,
            bg="#9C27B0", fg="white", **btn_style
        )
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = tk.Button(
            frame, text="🔄  Reset",
            command=self._reset,
            bg="#607D8B", fg="white", **btn_style
        )
        self.reset_btn.pack(side=tk.RIGHT, padx=5)

    def _build_gantt_chart(self):
        self.gantt_chart = GanttChart(self.main_frame)
        self.gantt_chart.pack(fill=tk.X, padx=5, pady=2)
        self.gantt_chart.configure(height=150)

    def _build_bottom_area(self):
        bottom = tk.Frame(self.main_frame, bg="#2d2d30")
        bottom.pack(fill=tk.BOTH, expand=True, padx=5, pady=(2, 5))

        self.process_table = ProcessTable(bottom)
        self.process_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.stats_panel = StatsPanel(bottom)
        self.stats_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

    # ══════════════════════════════════════════════════════════════════
    #  EVENT HANDLERS
    # ══════════════════════════════════════════════════════════════════

    def _on_scheduler_change(self, event=None):
        if self.scheduler_var.get() == "Round Robin":
            self.quantum_frame.pack(side=tk.LEFT, padx=5)
        else:
            self.quantum_frame.pack_forget()

    def _setup_processes(self):
        if self.is_live_running:
            messagebox.showwarning("Warning", "Stop the simulation first!")
            return
        try:
            n = int(self.num_processes_entry.get().strip())
            if n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid positive number.")
            return

        sched = self.scheduler_var.get()
        needs_priority = "Priority" in sched
        self.process_counter = n
        self.input_panel.setup_inputs(n, needs_priority=needs_priority)
        self.main_canvas.yview_moveto(0)

    # ══════════════════════════════════════════════════════════════════
    #  TEST CASE LOADER
    # ══════════════════════════════════════════════════════════════════

    def _load_test_case(self, instant=False):
        """Load a built-in test case and optionally run it."""
        selected = self.test_var.get()
        tc = get_test_case(selected)

        if tc is None:
            messagebox.showwarning(
                "No Test Selected",
                "Please select a test case from the dropdown."
            )
            return

        # Stop any running simulation
        self._stop_simulation()
        self._reset_state()

        # Set scheduler type in combo
        sched_name = tc["scheduler"]
        self.scheduler_var.set(sched_name)
        self._on_scheduler_change()

        # Set quantum if needed
        if tc["quantum"] is not None:
            self.quantum_entry.delete(0, tk.END)
            self.quantum_entry.insert(0, str(tc["quantum"]))

        # Set up input panel
        processes = tc["processes"]
        needs_priority = "Priority" in sched_name
        self.process_counter = len(processes)

        self.num_processes_entry.delete(0, tk.END)
        self.num_processes_entry.insert(0, str(len(processes)))

        self.input_panel.setup_inputs(len(processes), needs_priority=needs_priority)

        # Fill in the values
        for i, (pid, arrival, burst, priority) in enumerate(processes):
            entry = self.input_panel.process_entries[i]
            # Arrival
            entry["arrival"].delete(0, tk.END)
            entry["arrival"].insert(0, str(arrival))
            # Burst
            entry["burst"].delete(0, tk.END)
            entry["burst"].insert(0, str(burst))
            # Priority
            if "priority" in entry:
                entry["priority"].delete(0, tk.END)
                entry["priority"].insert(0, str(priority))

        self.main_canvas.yview_moveto(0)

        # Show info toast
        self._show_toast(
            f"✅ Loaded: {tc['name']}",
            "#4CAF50", duration=2500
        )

        # Run after short delay so user sees the loaded inputs
        if instant:
            self.root.after(400, self._run_instant)
        else:
            self.root.after(400, self._start_live)

    def _show_test_info(self):
        """Show detailed info about the selected test case."""
        selected = self.test_var.get()
        tc = get_test_case(selected)

        if tc is None:
            messagebox.showwarning(
                "No Test Selected",
                "Please select a test case from the dropdown."
            )
            return

        # Build process table string
        proc_lines = []
        has_priority = "Priority" in tc["scheduler"]

        if has_priority:
            proc_lines.append(f"{'PID':<6} {'Arrival':<9} {'Burst':<8} {'Priority':<8}")
            proc_lines.append("─" * 35)
            for pid, arr, bur, pri in tc["processes"]:
                proc_lines.append(f"{pid:<6} {arr:<9} {bur:<8} {pri:<8}")
        else:
            proc_lines.append(f"{'PID':<6} {'Arrival':<9} {'Burst':<8}")
            proc_lines.append("─" * 26)
            for pid, arr, bur, pri in tc["processes"]:
                proc_lines.append(f"{pid:<6} {arr:<9} {bur:<8}")

        proc_table = "\n".join(proc_lines)

        quantum_str = ""
        if tc["quantum"] is not None:
            quantum_str = f"\nTime Quantum: {tc['quantum']}"

        info_text = (
            f"📝 {tc['name']}\n"
            f"{'═' * 45}\n\n"
            f"Algorithm: {tc['scheduler']}{quantum_str}\n\n"
            f"Description:\n{tc['description']}\n\n"
            f"Processes:\n{proc_table}\n\n"
            f"💡 Tip: Use 'Load & Run Live' to watch step-by-step,\n"
            f"   or 'Load & Run Instant' to see final results immediately.\n"
            f"   You can also add processes dynamically during live run!"
        )

        # Custom info window (nicer than messagebox)
        popup = tk.Toplevel(self.root)
        popup.title(f"Test Case Info — {tc['scheduler']}")
        popup.configure(bg="#2d2d30")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        # Size and center
        pw, ph = 520, 480
        px = self.root.winfo_x() + (self.root.winfo_width() - pw) // 2
        py = self.root.winfo_y() + (self.root.winfo_height() - ph) // 2
        popup.geometry(f"{pw}x{ph}+{px}+{py}")

        # Content
        text_widget = tk.Text(
            popup, bg="#1e1e1e", fg="#dcdcdc",
            font=("Consolas", 10), padx=16, pady=16,
            wrap=tk.WORD, relief=tk.FLAT, highlightthickness=0
        )
        text_widget.insert("1.0", info_text)
        text_widget.configure(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        btn_frame = tk.Frame(popup, bg="#2d2d30")
        btn_frame.pack(pady=(5, 10))

        tk.Button(
            btn_frame, text="Load & Run Live",
            command=lambda: [popup.destroy(), self._load_test_case(instant=False)],
            bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"),
            padx=14, pady=4, cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="Load & Run Instant",
            command=lambda: [popup.destroy(), self._load_test_case(instant=True)],
            bg="#FF9800", fg="white", font=("Segoe UI", 10, "bold"),
            padx=14, pady=4, cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="Close",
            command=popup.destroy,
            bg="#607D8B", fg="white", font=("Segoe UI", 10, "bold"),
            padx=14, pady=4, cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

    def _show_toast(self, message, color, duration=2000):
        """Show a temporary notification at the top of the window."""
        toast = tk.Label(
            self.main_frame, text=message,
            bg=color, fg="white",
            font=("Segoe UI", 11, "bold"),
            pady=8, padx=20
        )
        toast.pack(fill=tk.X, padx=5, pady=(0, 2), before=self.input_panel)
        self.root.after(duration, toast.destroy)

    # ══════════════════════════════════════════════════════════════════
    #  SCHEDULER CREATION (uses core/)
    # ══════════════════════════════════════════════════════════════════

    def _create_scheduler(self):
        sched_type = self.SCHEDULER_TYPES[self.scheduler_var.get()]
        self.sched_type_key = sched_type

        if sched_type == "fcfs":
            return FCFS()
        elif sched_type == "sjf_np":
            return SJFScheduler(preemptive=False)
        elif sched_type == "sjf_p":
            return SJFScheduler(preemptive=True)
        elif sched_type == "priority_np":
            return PriorityScheduler(preemptive=False)
        elif sched_type == "priority_p":
            return PriorityScheduler(preemptive=True)
        elif sched_type == "rr":
            try:
                quantum = int(self.quantum_entry.get().strip())
                if quantum <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Time quantum must be a positive integer.")
                return None
            return RoundRobinScheduler(quantum=quantum)

    def _load_processes(self):
        data = self.input_panel.get_process_data()
        if data is None:
            return False
        if not data:
            messagebox.showerror("Error", "No processes to simulate!")
            return False

        for pid, arrival, burst, priority in data:
            process = Process(pid, arrival, burst, priority)
            self.scheduler.add_process(process)
            self.gantt_chart.get_color(pid)

        return True

    # ══════════════════════════════════════════════════════════════════
    #  SIMULATION CONTROLS
    # ══════════════════════════════════════════════════════════════════

    def _start_live(self):
        if self.is_live_running:
            messagebox.showinfo("Info", "Simulation is already running!")
            return

        self.scheduler = self._create_scheduler()
        if self.scheduler is None:
            return
        if not self._load_processes():
            return

        self.gantt_chart.clear()
        self.process_table.clear()
        self.is_live_running = True
        self._set_buttons_running(True)
        self._update_all_displays()

        for p in self.scheduler.processes:
            self.gantt_chart.get_color(p.pid)

        self._tick_live()

    def _tick_live(self):
        if not self.is_live_running or self.is_paused:
            return
        if self.scheduler.is_done():
            self._on_simulation_complete()
            return

        self.scheduler.tick()
        self._update_all_displays()
        self.sim_timer = self.root.after(1000, self._tick_live)

    def _run_instant(self):
        if self.is_live_running:
            messagebox.showwarning("Warning", "Stop the live simulation first!")
            return

        self.scheduler = self._create_scheduler()
        if self.scheduler is None:
            return
        if not self._load_processes():
            return

        self.gantt_chart.clear()
        self.process_table.clear()

        for p in self.scheduler.processes:
            self.gantt_chart.get_color(p.pid)

        max_steps = 10000
        steps = 0
        while not self.scheduler.is_done() and steps < max_steps:
            self.scheduler.tick()
            steps += 1

        if steps >= max_steps:
            messagebox.showwarning("Warning", "Max steps reached. Check your input.")

        self._update_all_displays()
        self._update_stats(is_running=False, is_complete=True)

    def _stop_simulation(self):
        if self.sim_timer is not None:
            self.root.after_cancel(self.sim_timer)
            self.sim_timer = None
        self.is_live_running = False
        self.is_paused = False
        self._set_buttons_running(False)

    def _toggle_pause(self):
        if self.is_paused:
            self._resume_from_pause()
        else:
            self._pause_simulation()

    def _pause_simulation(self):
        self.is_paused = True
        self.pause_btn.config(text="▶  Resume", bg="#4CAF50")

    def _resume_from_pause(self):
        self.is_paused = False
        self.pause_btn.config(text="⏸  Pause", bg="#FF9800")
        self._tick_live()

    def _on_simulation_complete(self):
        if self.sim_timer is not None:
            self.root.after_cancel(self.sim_timer)
            self.sim_timer = None
        self.is_live_running = False
        self._set_buttons_running(False)
        self._update_all_displays()
        self._update_stats(is_running=False, is_complete=True)

        avg_wt = self.scheduler.average_waiting_time()
        avg_tat = self.scheduler.average_turnaround_time()
        messagebox.showinfo(
            "Simulation Complete",
            f"All processes completed!\n\n"
            f"Average Waiting Time: {avg_wt:.2f}\n"
            f"Average Turnaround Time: {avg_tat:.2f}"
        )

    # ══════════════════════════════════════════════════════════════════
    #  DYNAMIC PROCESS ADDITION
    # ══════════════════════════════════════════════════════════════════

    def _add_process_dynamic(self):
        if not self.scheduler:
            messagebox.showwarning("Warning", "Start a simulation first!")
            return
        if self.scheduler.is_done():
            messagebox.showinfo("Info", "Simulation already completed.")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Add New Process")
        popup.geometry("350x300")
        popup.configure(bg="#3c3c3c")
        popup.resizable(False, False)
        popup.grab_set()
        popup.transient(self.root)

        popup.update_idletasks()
        pw = popup.winfo_width()
        ph = popup.winfo_height()
        px = self.root.winfo_x() + (self.root.winfo_width() - pw) // 2
        py = self.root.winfo_y() + (self.root.winfo_height() - ph) // 2
        popup.geometry(f"+{px}+{py}")

        self.process_counter += 1
        pid = f"P{self.process_counter}"

        tk.Label(
            popup, text=f"Adding Process: {pid}",
            bg="#3c3c3c", fg="#61dafb",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(15, 10))

        form = tk.Frame(popup, bg="#3c3c3c")
        form.pack(pady=10)

        tk.Label(
            form, text="Arrival Time:", bg="#3c3c3c", fg="white",
            font=("Segoe UI", 11)
        ).grid(row=0, column=0, padx=10, pady=8, sticky=tk.E)
        arrival_entry = tk.Entry(form, width=10, font=("Segoe UI", 11), justify=tk.CENTER)
        arrival_entry.grid(row=0, column=1, padx=10, pady=8)
        arrival_entry.insert(0, str(self.scheduler.current_time))

        tk.Label(
            form, text="Burst Time:", bg="#3c3c3c", fg="white",
            font=("Segoe UI", 11)
        ).grid(row=1, column=0, padx=10, pady=8, sticky=tk.E)
        burst_entry = tk.Entry(form, width=10, font=("Segoe UI", 11), justify=tk.CENTER)
        burst_entry.grid(row=1, column=1, padx=10, pady=8)

        priority_entry = None
        if "Priority" in self.scheduler_var.get():
            tk.Label(
                form, text="Priority:", bg="#3c3c3c", fg="white",
                font=("Segoe UI", 11)
            ).grid(row=2, column=0, padx=10, pady=8, sticky=tk.E)
            priority_entry = tk.Entry(form, width=10, font=("Segoe UI", 11), justify=tk.CENTER)
            priority_entry.grid(row=2, column=1, padx=10, pady=8)
            priority_entry.insert(0, "0")

        def on_add():
            try:
                arrival = int(arrival_entry.get().strip())
                burst = int(burst_entry.get().strip())
                priority = 0
                if priority_entry:
                    priority = int(priority_entry.get().strip())
                if burst <= 0:
                    messagebox.showerror("Error", "Burst time must be positive!")
                    return
                if arrival < 0:
                    messagebox.showerror("Error", "Arrival time cannot be negative!")
                    return

                process = Process(pid, arrival, burst, priority)
                self.gantt_chart.get_color(pid)
                self.scheduler.add_process(process)
                self._update_all_displays()
                popup.destroy()

                self._show_toast(
                    f"➕ Added {pid} (arrival={arrival}, burst={burst})",
                    "#9C27B0", duration=2000
                )

            except ValueError:
                messagebox.showerror("Error", "Please enter valid integers!")

        btn_frame = tk.Frame(popup, bg="#3c3c3c")
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame, text="✓ Add", command=on_add,
            bg="#4CAF50", fg="white", font=("Segoe UI", 11, "bold"),
            padx=20, pady=5, cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="✗ Cancel", command=popup.destroy,
            bg="#f44336", fg="white", font=("Segoe UI", 11, "bold"),
            padx=20, pady=5, cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)

    # ══════════════════════════════════════════════════════════════════
    #  UI UPDATES
    # ══════════════════════════════════════════════════════════════════

    def _update_all_displays(self):
        if not self.scheduler:
            return

        self.gantt_chart.draw(self.scheduler.gantt_chart)

        show_priority = "Priority" in self.scheduler_var.get()
        self.process_table.update_table(
            self.scheduler.processes,
            self.scheduler.current_time,
            show_priority=show_priority
        )

        self._update_stats(
            is_running=self.is_live_running,
            is_complete=self.scheduler.is_done()
        )

    def _update_stats(self, is_running=False, is_complete=False):
        if not self.scheduler:
            return

        name = self.SCHEDULER_NAMES.get(self.sched_type_key, "Unknown")
        completed = [p for p in self.scheduler.processes if p.is_completed]

        self.stats_panel.update_stats(
            scheduler_name=name,
            current_time=self.scheduler.current_time,
            avg_wt=self.scheduler.average_waiting_time(),
            avg_tat=self.scheduler.average_turnaround_time(),
            completed_count=len(completed),
            total_count=len(self.scheduler.processes),
            is_running=is_running,
            is_complete=is_complete,
        )

    def _set_buttons_running(self, is_running):
        if is_running:
            self.start_btn.config(state=tk.DISABLED)
            self.instant_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.NORMAL)
            self.scheduler_combo.config(state=tk.DISABLED)
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.instant_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.DISABLED, text="⏸  Pause", bg="#FF9800")
            self.scheduler_combo.config(state="readonly")

    def _reset_state(self):
        """Reset internal state without clearing UI combo/entries."""
        if self.sim_timer is not None:
            self.root.after_cancel(self.sim_timer)
            self.sim_timer = None
        self.is_live_running = False
        self.scheduler = None
        self.process_counter = 0
        self.gantt_chart.clear()
        self.process_table.clear()
        self.stats_panel.clear()
        self._set_buttons_running(False)

    def _reset(self):
        self._reset_state()
        self.input_panel.clear()
        self.main_canvas.yview_moveto(0)
