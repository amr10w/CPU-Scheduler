"""
CPU Scheduler Simulator
=======================
A GUI desktop application that simulates CPU scheduling algorithms.

Supported Algorithms:
    1. FCFS (First Come First Served)
    2. SJF - Preemptive (SRTF) & Non-Preemptive
    3. Priority Scheduling - Preemptive & Non-Preemptive
    4. Round Robin (with configurable time quantum)

Features:
    - Live simulation (1 second = 1 time unit)
    - Instant execution mode
    - Dynamic process addition during simulation
    - Live Gantt chart timeline
    - Live process status table with remaining burst times
    - Average waiting time and turnaround time statistics

Author: [Your Name]
Course: [Your Course Name]
Date: [Date]
"""

import tkinter as tk
from gui.app import CPUSchedulerApp


def main():
    """Initialize and run the CPU Scheduler application."""
    root = tk.Tk()

    # Create the application
    app = CPUSchedulerApp(root)

    # Center the window on screen
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"+{x}+{y}")

    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()