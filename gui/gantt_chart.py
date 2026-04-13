import tkinter as tk
from tkinter import ttk


COLORS = [
    "#5DA5A4",
    "#9B5DE5",
    "#F15BB5",
    "#FE5F55",
    "#00BBF9",
    "#FEE440",
    "#3FC1C9",
    "#F7B32B",
    "#FF9F1C",
]


class GanttChart(ttk.LabelFrame):
    """Live scrollable Gantt chart."""

    def __init__(self, parent):
        super().__init__(parent, text="Gantt Chart", padding=10)
        self.canvas = tk.Canvas(self, height=120, background="#ffffff")
        self.h_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.h_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._colors = {}

    def draw(self, gantt_data):
        self.canvas.delete("all")

        if not gantt_data:
            return

        x = 0
        width = 80
        for entry in gantt_data:
            pid = entry.get("pid", "Idle")
            color = self._color_for(pid)
            self.canvas.create_rectangle(x, 20, x + width, 80, fill=color, outline="#333333")
            self.canvas.create_text(x + width / 2, 50, text=pid, fill="#ffffff")
            self.canvas.create_text(x + 5, 90, anchor="w", text=str(entry.get("time", "")), fill="#333333", font=(None, 8))
            x += width

        self.canvas.create_text(x - width / 2, 5, text=f"Time {gantt_data[-1].get('time', 0) + 1}", fill="#333333", font=(None, 9, "bold"))
        self.canvas.configure(scrollregion=(0, 0, max(x, self.winfo_width()), 120))

    def _color_for(self, pid):
        if pid not in self._colors:
            index = len(self._colors) % len(COLORS)
            self._colors[pid] = COLORS[index]
        return self._colors[pid]
