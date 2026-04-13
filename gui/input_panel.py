import tkinter as tk
from tkinter import ttk, messagebox


class InputPanel(ttk.LabelFrame):
    """Process input form with validation."""

    def __init__(self, parent, add_process_callback):
        super().__init__(parent, text="Add Process", padding=10)
        self.add_process_callback = add_process_callback

        ttk.Label(self, text="Process ID:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.pid_entry = ttk.Entry(self)
        self.pid_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(self, text="Arrival Time:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.arrival_entry = ttk.Entry(self)
        self.arrival_entry.grid(row=1, column=1, sticky="ew", padx=4, pady=4)

        ttk.Label(self, text="Burst Time:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        self.burst_entry = ttk.Entry(self)
        self.burst_entry.grid(row=2, column=1, sticky="ew", padx=4, pady=4)

        self.priority_label = ttk.Label(self, text="Priority (lower = higher):")
        self.priority_label.grid(row=3, column=0, sticky="w", padx=4, pady=4)
        self.priority_entry = ttk.Entry(self)
        self.priority_entry.grid(row=3, column=1, sticky="ew", padx=4, pady=4)
        self.priority_widgets = [self.priority_label, self.priority_entry]

        self.add_button = ttk.Button(self, text="Add Process", command=self.add_process)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.status_label = ttk.Label(self, text="", foreground="red")
        self.status_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=4)

        self.columnconfigure(1, weight=1)
        self.priority_visible = False
        self.set_priority_visible(False)

    def add_process(self):
        try:
            pid = self.pid_entry.get().strip()
            if not pid:
                raise ValueError("Process ID cannot be empty")

            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            if self.priority_visible:
                raw_priority = self.priority_entry.get().strip()
                if raw_priority == "":
                    raise ValueError("Priority cannot be empty for priority scheduling")
                priority = int(raw_priority)
            else:
                priority = 0

            if arrival < 0:
                raise ValueError("Arrival time must be 0 or greater")
            if burst <= 0:
                raise ValueError("Burst time must be greater than 0")

            self.add_process_callback(pid, arrival, burst, priority)
            self.status_label.config(text="Process added successfully", foreground="green")
            self._clear_fields()
        except ValueError as exc:
            messagebox.showerror("Input Error", str(exc))
            self.status_label.config(text=str(exc), foreground="red")

    def set_priority_visible(self, visible):
        self.priority_visible = visible
        if visible:
            self.priority_label.grid()
            self.priority_entry.grid()
        else:
            self.priority_label.grid_remove()
            self.priority_entry.grid_remove()

    def set_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        for widget in [
            self.pid_entry,
            self.arrival_entry,
            self.burst_entry,
            self.priority_entry,
            self.add_button,
        ]:
            widget.config(state=state)

    def _clear_fields(self):
        self.pid_entry.delete(0, tk.END)
        self.arrival_entry.delete(0, tk.END)
        self.burst_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)
