import tkinter as tk
from tkinter import ttk


class StatsPanel(ttk.LabelFrame):
    """Statistics display panel."""

    def __init__(self, parent):
        super().__init__(parent, text="Statistics", padding=10)
        self.avg_wait_label = ttk.Label(self, text="Average Waiting Time: -")
        self.avg_turn_label = ttk.Label(self, text="Average Turnaround Time: -")
        self.gantt_label = ttk.Label(self, text="Gantt Length: -")

        self.avg_wait_label.grid(row=0, column=0, sticky="w", pady=4)
        self.avg_turn_label.grid(row=1, column=0, sticky="w", pady=4)
        self.gantt_label.grid(row=2, column=0, sticky="w", pady=4)

    def update(self, stats):
        self.avg_wait_label.config(text=f"Average Waiting Time: {stats.get('avg_waiting', 0):.2f}")
        self.avg_turn_label.config(text=f"Average Turnaround Time: {stats.get('avg_turnaround', 0):.2f}")
        self.gantt_label.config(text=f"Gantt Length: {len(stats.get('gantt', []))}")
