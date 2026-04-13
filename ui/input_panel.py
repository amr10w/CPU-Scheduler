"""
Input Panel - Process input form.
Dynamically shows/hides fields based on scheduler type.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class InputPanel(tk.LabelFrame):

    def __init__(self, parent):
        super().__init__(
            parent, text="  Process Input  ",
            font=("Segoe UI", 11, "bold"),
            bg="#2d2d30", fg="#dcdcdc",
            labelanchor="n", padx=10, pady=10
        )
        self.process_entries = []
        self._build_empty_state()

    def _build_empty_state(self):
        self.placeholder = tk.Label(
            self,
            text="← Select a scheduler and set number of processes to begin",
            bg="#2d2d30", fg="#888888",
            font=("Segoe UI", 10, "italic")
        )
        self.placeholder.pack(pady=20)

    def setup_inputs(self, num_processes, needs_priority=False):
        for widget in self.winfo_children():
            widget.destroy()
        self.process_entries.clear()

        if num_processes == 0:
            self._build_empty_state()
            return

        canvas = tk.Canvas(self, bg="#2d2d30", highlightthickness=0, height=150)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#2d2d30")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        headers = ["PID", "Arrival Time", "Burst Time"]
        if needs_priority:
            headers.append("Priority")

        header_frame = tk.Frame(scroll_frame, bg="#2d2d30")
        header_frame.pack(fill=tk.X, pady=(0, 5))

        col_widths = [8, 12, 12, 12]
        for i, header in enumerate(headers):
            tk.Label(
                header_frame, text=header,
                bg="#2d2d30", fg="#61dafb",
                font=("Segoe UI", 10, "bold"),
                width=col_widths[i]
            ).grid(row=0, column=i, padx=5)

        for i in range(num_processes):
            row_frame = tk.Frame(scroll_frame, bg="#2d2d30")
            row_frame.pack(fill=tk.X, pady=1)

            entry_dict = {}
            pid = f"P{i + 1}"
            entry_dict["pid"] = pid

            tk.Label(
                row_frame, text=pid,
                bg="#2d2d30", fg="#ffa500",
                font=("Segoe UI", 10, "bold"),
                width=col_widths[0]
            ).grid(row=0, column=0, padx=5)

            arrival = tk.Entry(
                row_frame, width=col_widths[1],
                font=("Segoe UI", 10), justify=tk.CENTER
            )
            arrival.grid(row=0, column=1, padx=5)
            arrival.insert(0, "0")
            entry_dict["arrival"] = arrival

            burst = tk.Entry(
                row_frame, width=col_widths[2],
                font=("Segoe UI", 10), justify=tk.CENTER
            )
            burst.grid(row=0, column=2, padx=5)
            entry_dict["burst"] = burst

            if needs_priority:
                priority = tk.Entry(
                    row_frame, width=col_widths[3],
                    font=("Segoe UI", 10), justify=tk.CENTER
                )
                priority.grid(row=0, column=3, padx=5)
                priority.insert(0, "0")
                entry_dict["priority"] = priority

            self.process_entries.append(entry_dict)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def get_process_data(self):
        data = []
        for entry in self.process_entries:
            pid = entry["pid"]
            try:
                arrival = int(entry["arrival"].get().strip())
                if arrival < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Input Error",
                    f"{pid}: Arrival time must be a non-negative integer.")
                return None
            try:
                burst = int(entry["burst"].get().strip())
                if burst <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Input Error",
                    f"{pid}: Burst time must be a positive integer.")
                return None
            priority = 0
            if "priority" in entry:
                try:
                    priority = int(entry["priority"].get().strip())
                    if priority < 0:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Input Error",
                        f"{pid}: Priority must be a non-negative integer.")
                    return None
            data.append((pid, arrival, burst, priority))
        return data

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.process_entries.clear()
        self._build_empty_state()
