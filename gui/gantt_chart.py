"""
Gantt Chart Widget
==================
Draws a live, scrollable Gantt chart showing which process
runs at each time unit.
"""

import tkinter as tk


class GanttChart(tk.LabelFrame):
    """Live Gantt chart that draws the scheduling timeline."""

    # Color palette for different processes
    COLORS = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
        "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F",
        "#BB8FCE", "#85C1E9", "#F0B27A", "#82E0AA",
        "#F1948A", "#AED6F1", "#A3E4D7", "#FAD7A0",
    ]
    IDLE_COLOR = "#555555"

    def __init__(self, parent):
        super().__init__(
            parent, text="  Gantt Chart (Live Timeline)  ",
            font=("Segoe UI", 11, "bold"),
            bg="#1e1e1e", fg="#dcdcdc",
            labelanchor="n"
        )

        self.color_map = {}        # {pid: color_string}
        self.color_index = 0
        self.unit_width = 55       # Pixels per time unit
        self.bar_height = 45       # Height of each process block
        self.y_top = 25            # Top of the bar area
        self.x_offset = 30         # Left margin

        # Canvas with horizontal scrollbar
        self.canvas = tk.Canvas(
            self, bg="#1e1e1e", height=120, highlightthickness=0
        )
        self.scrollbar = tk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=self.canvas.xview
        )
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Show initial message
        self._draw_placeholder()

    def _draw_placeholder(self):
        """Show a placeholder message on the empty chart."""
        self.canvas.create_text(
            300, 60,
            text="Gantt chart will appear here when simulation starts...",
            fill="#888888", font=("Segoe UI", 11, "italic")
        )

    def get_color(self, pid):
        """Get or assign a color for a process."""
        if pid == "IDLE":
            return self.IDLE_COLOR
        if pid not in self.color_map:
            self.color_map[pid] = self.COLORS[self.color_index % len(self.COLORS)]
            self.color_index += 1
        return self.color_map[pid]

    def draw(self, timeline, merged=True):
        """
        Draw the Gantt chart from timeline data.

        Args:
            timeline: list of (pid, start_time, end_time) tuples
            merged: if True, merge consecutive same-process blocks
        """
        self.canvas.delete("all")

        if not timeline:
            self._draw_placeholder()
            return

        # Merge consecutive entries for cleaner display
        if merged:
            timeline = self._merge_timeline(timeline)

        y_bottom = self.y_top + self.bar_height

        for pid, start, end in timeline:
            x1 = self.x_offset + start * self.unit_width
            x2 = self.x_offset + end * self.unit_width
            color = self.get_color(pid)

            # Choose text color based on block type
            text_color = "black" if pid != "IDLE" else "#aaaaaa"
            display_text = pid if pid != "IDLE" else "idle"

            # Draw the colored block
            self.canvas.create_rectangle(
                x1, self.y_top, x2, y_bottom,
                fill=color, outline="#ffffff", width=1
            )

            # Process name centered in the block
            self.canvas.create_text(
                (x1 + x2) / 2, (self.y_top + y_bottom) / 2,
                text=display_text,
                fill=text_color, font=("Segoe UI", 9, "bold")
            )

            # Time label below the start of each block
            self.canvas.create_text(
                x1, y_bottom + 15,
                text=str(start),
                fill="#cccccc", font=("Segoe UI", 8)
            )

        # Draw the final end time
        if timeline:
            last_end = timeline[-1][2]
            x_last = self.x_offset + last_end * self.unit_width
            self.canvas.create_text(
                x_last, y_bottom + 15,
                text=str(last_end),
                fill="#cccccc", font=("Segoe UI", 8)
            )

        # Update scroll region and auto-scroll to latest
        total_width = self.x_offset + (timeline[-1][2] + 2) * self.unit_width
        self.canvas.configure(scrollregion=(0, 0, total_width, 120))
        self.canvas.xview_moveto(1.0)

    def _merge_timeline(self, timeline):
        """
        Merge consecutive timeline entries for the same process.
        Example: [(P1,0,1), (P1,1,2)] -> [(P1,0,2)]
        """
        if not timeline:
            return []

        merged = [list(timeline[0])]
        for i in range(1, len(timeline)):
            pid, start, end = timeline[i]
            prev = merged[-1]

            if pid == prev[0] and start == prev[2]:
                prev[2] = end  # Extend the existing block
            else:
                merged.append([pid, start, end])

        return [tuple(m) for m in merged]

    def clear(self):
        """Clear the Gantt chart and reset colors."""
        self.canvas.delete("all")
        self.color_map.clear()
        self.color_index = 0
        self._draw_placeholder()