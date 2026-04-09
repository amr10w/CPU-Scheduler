"""
Process Table Widget
====================
Live-updating table showing status of all processes.
Shows: PID, Arrival, Burst, Remaining, Priority, Wait, Turnaround, Status
"""

import tkinter as tk
from tkinter import ttk


class ProcessTable(tk.LabelFrame):
    """Table displaying real-time process information."""

    def __init__(self, parent):
        super().__init__(
            parent, text="  Process Status (Live)  ",
            font=("Segoe UI", 11, "bold"),
            bg="#2d2d30", fg="#dcdcdc",
            labelanchor="n"
        )

        # Column definitions
        self.columns = (
            "PID", "Arrival", "Burst", "Remaining",
            "Priority", "Wait", "Turnaround", "Status"
        )

        # Style the treeview for dark theme
        self._setup_style()

        # Create treeview widget
        self.tree = ttk.Treeview(
            self, columns=self.columns,
            show="headings", style="Custom.Treeview",
            height=8
        )

        # Configure columns
        col_widths = {
            "PID": 60, "Arrival": 70, "Burst": 60,
            "Remaining": 85, "Priority": 70, "Wait": 60,
            "Turnaround": 90, "Status": 110
        }
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(
                col, width=col_widths.get(col, 80),
                anchor=tk.CENTER, minwidth=50
            )

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)

    def _setup_style(self):
        """Configure the dark theme style for the treeview."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Custom.Treeview",
            background="#1e1e1e",
            foreground="#dcdcdc",
            fieldbackground="#1e1e1e",
            font=("Segoe UI", 10),
            rowheight=25
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#3c3c3c",
            foreground="#61dafb",
            font=("Segoe UI", 10, "bold")
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#264f78")]
        )

    def update_table(self, processes, current_time, show_priority=True):
        """
        Refresh the table with current process data.

        Args:
            processes: list of Process objects
            current_time: current simulation time
            show_priority: whether to display priority values
        """
        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not processes:
            return

        for p in processes:
            # Determine current status with emoji indicators
            if p.is_completed:
                status = "✅ Completed"
            elif p.remaining_time < p.burst_time and not p.is_completed:
                status = "🔄 Running"
            elif p.has_arrived(current_time):
                status = "⏳ Ready"
            else:
                status = "🕐 Not Arrived"

            # Show dash for unavailable data
            priority_val = p.priority if show_priority else "-"
            wait_val = p.waiting_time if p.is_completed else "-"
            tat_val = p.turnaround_time if p.is_completed else "-"

            self.tree.insert("", tk.END, values=(
                p.pid, p.arrival_time, p.burst_time,
                p.remaining_time, priority_val,
                wait_val, tat_val, status
            ))

    def clear(self):
        """Remove all rows from the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)