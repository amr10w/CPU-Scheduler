"""
Statistics Panel
================
Displays simulation metrics:
- Scheduler name
- Current time
- Average waiting time
- Average turnaround time
- Completion progress
- Running status
"""

import tkinter as tk


class StatsPanel(tk.LabelFrame):
    """Panel showing real-time simulation statistics."""

    def __init__(self, parent):
        super().__init__(
            parent, text="  Statistics  ",
            font=("Segoe UI", 11, "bold"),
            bg="#2d2d30", fg="#dcdcdc",
            labelanchor="n", padx=15, pady=15
        )

        # --- Scheduler Name ---
        self.scheduler_label = tk.Label(
            self, text="Scheduler: --",
            bg="#2d2d30", fg="#61dafb",
            font=("Segoe UI", 13, "bold")
        )
        self.scheduler_label.pack(pady=(5, 15))

        # --- Separator ---
        tk.Frame(self, bg="#555555", height=1).pack(fill=tk.X, pady=5)

        # --- Current Time ---
        self.time_label = tk.Label(
            self, text="⏱  Current Time: 0",
            bg="#2d2d30", fg="#FFEAA7",
            font=("Segoe UI", 14, "bold")
        )
        self.time_label.pack(pady=10)

        # --- Average Waiting Time ---
        self.avg_wt_label = tk.Label(
            self, text="Avg Waiting Time\n--",
            bg="#2d2d30", fg="#4ECDC4",
            font=("Segoe UI", 13, "bold")
        )
        self.avg_wt_label.pack(pady=10)

        # --- Average Turnaround Time ---
        self.avg_tat_label = tk.Label(
            self, text="Avg Turnaround Time\n--",
            bg="#2d2d30", fg="#FF6B6B",
            font=("Segoe UI", 13, "bold")
        )
        self.avg_tat_label.pack(pady=10)

        # --- Separator ---
        tk.Frame(self, bg="#555555", height=1).pack(fill=tk.X, pady=5)

        # --- Completion Counter ---
        self.completion_label = tk.Label(
            self, text="Completed: 0 / 0",
            bg="#2d2d30", fg="#82E0AA",
            font=("Segoe UI", 12)
        )
        self.completion_label.pack(pady=10)

        # --- Status Indicator ---
        self.status_label = tk.Label(
            self, text="● IDLE",
            bg="#2d2d30", fg="#888888",
            font=("Segoe UI", 12, "bold")
        )
        self.status_label.pack(pady=10)

    def update_stats(self, scheduler_name, current_time,
                     avg_wt, avg_tat,
                     completed_count, total_count,
                     is_running=False, is_complete=False):
        """
        Update all statistics displays.

        Args:
            scheduler_name: name of current algorithm
            current_time: simulation clock value
            avg_wt: average waiting time
            avg_tat: average turnaround time
            completed_count: number of completed processes
            total_count: total number of processes
            is_running: whether simulation is actively running
            is_complete: whether all processes finished
        """
        self.scheduler_label.config(text=f"Scheduler: {scheduler_name}")
        self.time_label.config(text=f"⏱  Current Time: {current_time}")
        self.avg_wt_label.config(text=f"Avg Waiting Time\n{avg_wt:.2f}")
        self.avg_tat_label.config(text=f"Avg Turnaround Time\n{avg_tat:.2f}")
        self.completion_label.config(
            text=f"Completed: {completed_count} / {total_count}"
        )

        # Update status indicator
        if is_complete:
            self.status_label.config(text="● COMPLETE", fg="#82E0AA")
        elif is_running:
            self.status_label.config(text="● RUNNING", fg="#4ECDC4")
        else:
            self.status_label.config(text="● IDLE", fg="#888888")

    def clear(self):
        """Reset all statistics to default."""
        self.scheduler_label.config(text="Scheduler: --")
        self.time_label.config(text="⏱  Current Time: 0")
        self.avg_wt_label.config(text="Avg Waiting Time\n--")
        self.avg_tat_label.config(text="Avg Turnaround Time\n--")
        self.completion_label.config(text="Completed: 0 / 0")
        self.status_label.config(text="● IDLE", fg="#888888")