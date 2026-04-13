import tkinter as tk
from tkinter import ttk


class ProcessTable(ttk.LabelFrame):
    """Real-time process status table."""

    def __init__(self, parent):
        super().__init__(parent, text="Process Table", padding=10)

        columns = [
            "pid",
            "arrival",
            "burst",
            "remaining",
            "priority",
            "start",
            "completion",
            "waiting",
            "turnaround",
        ]

        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, anchor="center", width=90)

        self.tree.column("pid", width=60)
        self.tree.column("arrival", width=70)
        self.tree.column("burst", width=70)
        self.tree.column("remaining", width=80)
        self.tree.column("priority", width=70)
        self.tree.column("start", width=70)
        self.tree.column("completion", width=80)
        self.tree.column("waiting", width=80)
        self.tree.column("turnaround", width=90)

        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def update(self, processes):
        self.tree.delete(*self.tree.get_children())
        for process in processes:
            remaining = process.remaining_time if not process.is_completed else 0
            self.tree.insert(
                "",
                "end",
                values=(
                    process.pid,
                    process.arrival_time,
                    process.burst_time,
                    remaining,
                    process.priority,
                    process.start_time if process.start_time != -1 else "-",
                    process.completion_time if process.completion_time else "-",
                    process.waiting_time if process.waiting_time else "-",
                    process.turnaround_time if process.turnaround_time else "-",
                ),
            )
