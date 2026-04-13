import tkinter as tk
from tkinter import ttk, messagebox

from core.engine import Engine
from core.fcfs import FCFS
from core.priority import PriorityScheduler
from core.roundroubin import RoundRobinScheduler
from core.sjf import SJFScheduler
from .gantt_chart import GanttChart
from .input_panel import InputPanel
from .process_table import ProcessTable
from .stats_panel import StatsPanel


class SchedulerApp(tk.Tk):
    """Main application window that connects the GUI to the scheduler engine."""

    def __init__(self):
        super().__init__()
        self.title("CPU Scheduler Simulator")
        self.geometry("1000x700")
        self.minsize(900, 600)

        self.engine = Engine()
        self.scheduler = None
        self.after_id = None

        self.scheduler_type = tk.StringVar(value="FCFS")
        self.quantum = tk.IntVar(value=4)

        self._build_layout()
        self._refresh_input_panel_visibility()

    def _build_layout(self):
        top_frame = ttk.Frame(self, padding=10)
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="Scheduler:").grid(row=0, column=0, padx=4, pady=4, sticky="w")
        scheduler_menu = ttk.Combobox(
            top_frame,
            textvariable=self.scheduler_type,
            values=["FCFS", "SJF", "SRTF", "Priority", "Priority Preemptive", "Round Robin"],
            state="readonly",
            width=22,
        )
        scheduler_menu.grid(row=0, column=1, padx=4, pady=4, sticky="w")
        scheduler_menu.bind("<<ComboboxSelected>>", self._scheduler_changed)


        self.quantum_label = ttk.Label(top_frame, text="Quantum:")
        self.quantum_entry = ttk.Entry(top_frame, textvariable=self.quantum, width=6)
        self.quantum_label.grid(row=0, column=2, padx=16, pady=4, sticky="w")
        self.quantum_entry.grid(row=0, column=3, padx=4, pady=4, sticky="w")

        self.run_button = ttk.Button(top_frame, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(row=0, column=4, padx=12, pady=4)

        self.reset_button = ttk.Button(top_frame, text="Reset Simulation", command=self.reset_simulation)
        self.reset_button.grid(row=0, column=5, padx=4, pady=4)

        self.clear_table_button = ttk.Button(top_frame, text="Clear Process Table", command=self.clear_process_table)
        self.clear_table_button.grid(row=0, column=6, padx=4, pady=4)

        top_frame.columnconfigure(6, weight=1)

        main_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        main_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 10))

        self.input_panel = InputPanel(left_frame, self.add_process)
        self.input_panel.pack(fill="x", pady=(0, 10))

        self.stats_panel = StatsPanel(left_frame)
        self.stats_panel.pack(fill="x")

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        self.gantt_chart = GanttChart(right_frame)
        self.gantt_chart.pack(fill="both", expand=True, pady=(0, 10))

        self.process_table = ProcessTable(right_frame)
        self.process_table.pack(fill="both", expand=True)

    def add_process(self, pid, arrival, burst, priority):
        try:
            self.engine.add_process(pid, arrival, burst, priority)
            self.process_table.update(self.engine.processes)
            self.stats_panel.update({"avg_waiting": 0.0, "avg_turnaround": 0.0, "gantt": []})
        except Exception as exc:
            messagebox.showerror("Error", f"Unable to add process: {exc}")

    def run_simulation(self):
        if not self.engine.processes:
            messagebox.showwarning("No Processes", "Please add at least one process before running the simulation.")
            return

        self.scheduler = self._build_scheduler()
        try:
            self.engine.set_scheduler(self.scheduler)
            self.engine.start()
        except AssertionError as exc:
            messagebox.showerror("Scheduler Error", str(exc))
            return

        self.run_button.config(state="disabled")
        self.clear_table_button.config(state="disabled")
        self.input_panel.set_enabled(False)
        self._tick_loop()

    def reset_simulation(self):
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

        if self.scheduler:
            self.engine.reset()
            self.scheduler = None

        self.run_button.config(state="normal")
        self.clear_table_button.config(state="normal")
        self.input_panel.set_enabled(True)
        self.process_table.update(self.engine.processes)
        self.stats_panel.update({"avg_waiting": 0.0, "avg_turnaround": 0.0, "gantt": []})
        self.gantt_chart.draw([])

    def _scheduler_changed(self, event=None):
        self._refresh_input_panel_visibility()

    def _refresh_input_panel_visibility(self):
        scheduler = self.scheduler_type.get()
        self.input_panel.set_priority_visible(scheduler.startswith("Priority"))
        show_quantum = scheduler == "Round Robin"
        if show_quantum:
            self.quantum_label.grid()
            self.quantum_entry.grid()
        else:
            self.quantum_label.grid_remove()
            self.quantum_entry.grid_remove()

    def _tick_loop(self):
        result = self.engine.step()
        self._update_live_views()

        if self.engine.is_done() or result is None:
            self._finish_simulation()
            return

        self.after_id = self.after(250, self._tick_loop)

    def _update_live_views(self):
        self.process_table.update(self.engine.processes)
        gantt_data = self.scheduler.gantt_chart if self.scheduler else []
        self.gantt_chart.draw(gantt_data)
        self.stats_panel.update({
            "avg_waiting": self.scheduler.average_waiting_time() if self.scheduler else 0.0,
            "avg_turnaround": self.scheduler.average_turnaround_time() if self.scheduler else 0.0,
            "gantt": gantt_data,
        })

    def _finish_simulation(self):
        self.run_button.config(state="normal")
        self.input_panel.set_enabled(True)
        self.after_id = None

    def _build_scheduler(self):
        selection = self.scheduler_type.get()
        if selection == "FCFS":
            return FCFS()
        if selection == "SJF":
            return SJFScheduler(preemptive=False)
        if selection == "SRTF":
            return SJFScheduler(preemptive=True)
        if selection == "Priority":
            return PriorityScheduler(preemptive=False)
        if selection == "Priority Preemptive":
            return PriorityScheduler(preemptive=True)
        if selection == "Round Robin":
            quantum = max(1, self.quantum.get())
            return RoundRobinScheduler(quantum=quantum)
        return FCFS()

    def clear_process_table(self):
        self.engine.processes.clear()
        self.process_table.update(self.engine.processes)
        self.stats_panel.update({"avg_waiting": 0.0, "avg_turnaround": 0.0, "gantt": []})
        self.gantt_chart.draw([])
        self.run_button.config(state="normal")
        self.input_panel.set_enabled(True)
        self.scheduler = None


if __name__ == "__main__":
    app = SchedulerApp()
    app.mainloop()
