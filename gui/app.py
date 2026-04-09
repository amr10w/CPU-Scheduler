"""
Main Application
================
The central GUI class that connects all components together.
Now with a scrollable main frame to handle long content.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import platform

from models.process import Process
from schedulers.fcfs import FCFSScheduler
from schedulers.sjf import SJFScheduler
from schedulers.priority_scheduler import PriorityScheduler
from schedulers.round_robin import RoundRobinScheduler
from gui.input_panel import InputPanel
from gui.gantt_chart import GanttChart
from gui.process_table import ProcessTable
from gui.stats_panel import StatsPanel


class CPUSchedulerApp:
    """Main application with scrollable interface."""

    SCHEDULER_TYPES = {
        "FCFS": "fcfs",
        "SJF (Non-Preemptive)": "sjf_np",
        "SJF (Preemptive)": "sjf_p",
        "Priority (Non-Preemptive)": "priority_np",
        "Priority (Preemptive)": "priority_p",
        "Round Robin": "rr",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduler Simulator")
        self.root.geometry("1300x850")
        self.root.minsize(1100, 700)
        self.root.configure(bg="#2d2d30")

        # --- Application State ---
        self.scheduler = None
        self.is_live_running = False
        self.simulation_thread = None
        self.process_counter = 0
        self.stop_event = threading.Event()

        # --- Build scrollable container FIRST ---
        self._build_scrollable_container()

        # --- Then build all GUI sections inside it ---
        self._build_control_bar()
        self._build_input_area()
        self._build_button_bar()
        self._build_gantt_chart()
        self._build_bottom_area()

    # ==============================================
    #       SCROLLABLE CONTAINER SETUP
    # ==============================================

    def _build_scrollable_container(self):
        """
        Create a scrollable main frame.
        Everything else is packed inside self.main_frame.
        """
        # --- Outer container that fills the entire window ---
        self.outer_frame = tk.Frame(self.root, bg="#2d2d30")
        self.outer_frame.pack(fill=tk.BOTH, expand=True)

        # --- Canvas (this is what actually scrolls) ---
        self.main_canvas = tk.Canvas(
            self.outer_frame, bg="#2d2d30", highlightthickness=0
        )

        # --- Vertical scrollbar ---
        self.v_scrollbar = ttk.Scrollbar(
            self.outer_frame, orient=tk.VERTICAL,
            command=self.main_canvas.yview
        )

        # --- The frame inside the canvas where all content goes ---
        self.main_frame = tk.Frame(self.main_canvas, bg="#2d2d30")

        # When the main_frame changes size, update the scroll region
        self.main_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )

        # Place the main_frame inside the canvas
        self.canvas_window = self.main_canvas.create_window(
            (0, 0), window=self.main_frame, anchor="nw"
        )

        # Connect scrollbar to canvas
        self.main_canvas.configure(yscrollcommand=self.v_scrollbar.set)

        # Pack scrollbar and canvas
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Make the inner frame resize with the canvas ---
        self.main_canvas.bind("<Configure>", self._on_canvas_configure)

        # --- Enable mouse wheel scrolling ---
        self._bind_mousewheel()

    def _on_canvas_configure(self, event):
        """
        When the canvas is resized, make the inner frame match its width.
        This ensures content stretches to fill the window.
        """
        canvas_width = event.width
        self.main_canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _bind_mousewheel(self):
        """
        Bind mouse wheel scrolling.
        Handles Windows, Mac, and Linux differently.
        """
        system = platform.system()

        if system == "Windows":
            # Windows uses MouseWheel event
            self.main_canvas.bind_all(
                "<MouseWheel>",
                lambda e: self.main_canvas.yview_scroll(
                    int(-1 * (e.delta / 120)), "units"
                )
            )
        elif system == "Darwin":
            # Mac uses MouseWheel but with different delta
            self.main_canvas.bind_all(
                "<MouseWheel>",
                lambda e: self.main_canvas.yview_scroll(
                    int(-1 * e.delta), "units"
                )
            )
        else:
            # Linux uses Button-4 and Button-5
            self.main_canvas.bind_all(
                "<Button-4>",
                lambda e: self.main_canvas.yview_scroll(-1, "units")
            )
            self.main_canvas.bind_all(
                "<Button-5>",
                lambda e: self.main_canvas.yview_scroll(1, "units")
            )

    def _unbind_mousewheel(self):
        """Unbind mouse wheel events (called on cleanup)."""
        system = platform.system()
        if system in ("Windows", "Darwin"):
            self.main_canvas.unbind_all("<MouseWheel>")
        else:
            self.main_canvas.unbind_all("<Button-4>")
            self.main_canvas.unbind_all("<Button-5>")

    # ==============================================
    #           GUI CONSTRUCTION METHODS
    # ==============================================

    def _build_control_bar(self):
        """Top bar: scheduler type + quantum + process count."""
        frame = tk.Frame(self.main_frame, bg="#3c3c3c", padx=10, pady=8)
        frame.pack(fill=tk.X, padx=5, pady=(5, 2))

        # Scheduler selection
        tk.Label(
            frame, text="Scheduler:", bg="#3c3c3c", fg="white",
            font=("Segoe UI", 11)
        ).pack(side=tk.LEFT, padx=(5, 3))

        self.scheduler_var = tk.StringVar(value="FCFS")
        self.scheduler_combo = ttk.Combobox(
            frame, textvariable=self.scheduler_var,
            values=list(self.SCHEDULER_TYPES.keys()),
            state="readonly", width=25, font=("Segoe UI", 10)
        )
        self.scheduler_combo.pack(side=tk.LEFT, padx=5)
        self.scheduler_combo.bind("<<ComboboxSelected>>", self._on_scheduler_change)

        # Quantum input (hidden by default)
        self.quantum_frame = tk.Frame(frame, bg="#3c3c3c")
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

        # Number of processes
        tk.Label(
            frame, text="Number of Processes:", bg="#3c3c3c",
            fg="white", font=("Segoe UI", 11)
        ).pack(side=tk.LEFT, padx=(30, 3))

        self.num_processes_entry = tk.Entry(
            frame, width=5, font=("Segoe UI", 10), justify=tk.CENTER
        )
        self.num_processes_entry.pack(side=tk.LEFT, padx=3)

        tk.Button(
            frame, text="Set Up", command=self._setup_processes,
            bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"),
            padx=12, pady=2, cursor="hand2"
        ).pack(side=tk.LEFT, padx=10)

    def _build_input_area(self):
        """Process input panel."""
        self.input_panel = InputPanel(self.main_frame)
        self.input_panel.pack(fill=tk.X, padx=5, pady=2)

    def _build_button_bar(self):
        """Simulation control buttons."""
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
            command=self._start_live_simulation,
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
        """Gantt chart display."""
        self.gantt_chart = GanttChart(self.main_frame)
        self.gantt_chart.pack(fill=tk.X, padx=5, pady=2)
        # Set a minimum height so it's always visible
        self.gantt_chart.configure(height=150)

    def _build_bottom_area(self):
        """Process table (left) + Statistics (right)."""
        bottom = tk.Frame(self.main_frame, bg="#2d2d30")
        bottom.pack(fill=tk.X, padx=5, pady=(2, 5))

        self.process_table = ProcessTable(bottom)
        self.process_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.stats_panel = StatsPanel(bottom)
        self.stats_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

    # ==============================================
    #           EVENT HANDLERS
    # ==============================================

    def _on_scheduler_change(self, event=None):
        """Show/hide quantum field based on scheduler selection."""
        if self.scheduler_var.get() == "Round Robin":
            self.quantum_frame.pack(side=tk.LEFT, padx=5)
        else:
            self.quantum_frame.pack_forget()

    def _setup_processes(self):
        """Create process input fields when user clicks 'Set Up'."""
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

        # Scroll to top after setting up inputs
        self.main_canvas.yview_moveto(0)

    # ==============================================
    #           SCHEDULER CREATION
    # ==============================================

    def _create_scheduler(self):
        """Instantiate the selected scheduling algorithm."""
        sched_type = self.SCHEDULER_TYPES[self.scheduler_var.get()]

        if sched_type == "fcfs":
            return FCFSScheduler()
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
        """Read processes from input panel and add to scheduler."""
        data = self.input_panel.get_process_data()
        if data is None:
            return False

        for pid, arrival, burst, priority in data:
            process = Process(pid, arrival, burst, priority)
            self.scheduler.add_process(process)
            self.gantt_chart.get_color(pid)

        return True

    # ==============================================
    #           SIMULATION CONTROLS
    # ==============================================

    def _start_live_simulation(self):
        """Start live simulation (1 second = 1 time unit)."""
        if self.is_live_running:
            messagebox.showinfo("Info", "Simulation is already running!")
            return

        self.scheduler = self._create_scheduler()
        if self.scheduler is None:
            return
        if not self._load_processes():
            return
        if not self.scheduler.processes:
            messagebox.showerror("Error", "No processes to simulate!")
            return

        self.gantt_chart.clear()
        self.process_table.clear()
        self.stop_event.clear()
        self.is_live_running = True
        self._set_buttons_running(True)
        self._update_all_displays()

        self.simulation_thread = threading.Thread(
            target=self._live_simulation_worker, daemon=True
        )
        self.simulation_thread.start()

    def _live_simulation_worker(self):
        """Background thread: runs one step per second."""
        while not self.stop_event.is_set():
            if self.scheduler.is_complete():
                break

            result = self.scheduler.step()
            if result == "DONE":
                break

            self.root.after(0, self._update_all_displays)

            for _ in range(10):
                if self.stop_event.is_set():
                    break
                time.sleep(0.1)

        self.root.after(0, self._on_simulation_complete)

    def _run_instant(self):
        """Run simulation instantly without delays."""
        if self.is_live_running:
            messagebox.showwarning("Warning", "Stop the live simulation first!")
            return

        self.scheduler = self._create_scheduler()
        if self.scheduler is None:
            return
        if not self._load_processes():
            return
        if not self.scheduler.processes:
            messagebox.showerror("Error", "No processes to simulate!")
            return

        self.gantt_chart.clear()
        self.process_table.clear()

        max_steps = 10000
        steps = 0
        while not self.scheduler.is_complete() and steps < max_steps:
            result = self.scheduler.step()
            if result == "DONE":
                break
            steps += 1

        if steps >= max_steps:
            messagebox.showwarning("Warning", "Max steps reached. Check your input.")

        self._update_all_displays()
        self.stats_panel.update_stats(
            self.scheduler.name, self.scheduler.current_time,
            self.scheduler.get_avg_waiting_time(),
            self.scheduler.get_avg_turnaround_time(),
            len(self.scheduler.completed), len(self.scheduler.processes),
            is_running=False, is_complete=True
        )

    def _stop_simulation(self):
        """Stop the live simulation."""
        self.stop_event.set()
        self.is_live_running = False
        self._set_buttons_running(False)

    def _on_simulation_complete(self):
        """Called when simulation finishes."""
        self.is_live_running = False
        self._set_buttons_running(False)
        self._update_all_displays()

        if self.scheduler and self.scheduler.is_complete():
            avg_wt = self.scheduler.get_avg_waiting_time()
            avg_tat = self.scheduler.get_avg_turnaround_time()
            messagebox.showinfo(
                "Simulation Complete",
                f"All processes completed!\n\n"
                f"Average Waiting Time: {avg_wt:.2f}\n"
                f"Average Turnaround Time: {avg_tat:.2f}"
            )

    # ==============================================
    #           DYNAMIC PROCESS ADDITION
    # ==============================================

    def _add_process_dynamic(self):
        """Open a popup to add a new process during simulation."""
        if not self.scheduler:
            messagebox.showwarning("Warning", "Start a simulation first!")
            return
        if self.scheduler.is_complete():
            messagebox.showinfo("Info", "Simulation already completed.")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Add New Process")
        popup.geometry("350x300")
        popup.configure(bg="#3c3c3c")
        popup.resizable(False, False)
        popup.grab_set()
        popup.transient(self.root)

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
                self.root.after(0, self._update_all_displays)
                popup.destroy()

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

    # ==============================================
    #           UI UPDATE METHODS
    # ==============================================

    def _update_all_displays(self):
        """Refresh all GUI components with current state."""
        if not self.scheduler:
            return

        self.gantt_chart.draw(self.scheduler.timeline, merged=True)

        show_priority = "Priority" in self.scheduler_var.get()
        self.process_table.update_table(
            self.scheduler.processes,
            self.scheduler.current_time,
            show_priority=show_priority
        )

        self.stats_panel.update_stats(
            scheduler_name=self.scheduler.name,
            current_time=self.scheduler.current_time,
            avg_wt=self.scheduler.get_avg_waiting_time(),
            avg_tat=self.scheduler.get_avg_turnaround_time(),
            completed_count=len(self.scheduler.completed),
            total_count=len(self.scheduler.processes),
            is_running=self.is_live_running,
            is_complete=self.scheduler.is_complete()
        )

    def _set_buttons_running(self, is_running):
        """Toggle button states based on simulation state."""
        if is_running:
            self.start_btn.config(state=tk.DISABLED)
            self.instant_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.scheduler_combo.config(state=tk.DISABLED)
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.instant_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.scheduler_combo.config(state="readonly")

    def _reset(self):
        """Reset everything to initial state."""
        if self.is_live_running:
            self.stop_event.set()
            self.is_live_running = False

        self.scheduler = None
        self.process_counter = 0

        self.input_panel.clear()
        self.gantt_chart.clear()
        self.process_table.clear()
        self.stats_panel.clear()
        self._set_buttons_running(False)

        # Scroll back to top
        self.main_canvas.yview_moveto(0)