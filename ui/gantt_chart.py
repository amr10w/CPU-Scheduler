"""
Gantt Chart - Live scrollable timeline.
"""

import tkinter as tk


class GanttChart(tk.LabelFrame):

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

        self.color_map = {}
        self.color_index = 0
        self.unit_width = 55
        self.bar_height = 45
        self.y_top = 25
        self.x_offset = 30

        self.canvas = tk.Canvas(
            self, bg="#1e1e1e", height=120, highlightthickness=0
        )
        self.scrollbar = tk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=self.canvas.xview
        )
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._draw_placeholder()

    def _draw_placeholder(self):
        self.canvas.create_text(
            300, 60,
            text="Gantt chart will appear here when simulation starts...",
            fill="#888888", font=("Segoe UI", 11, "italic")
        )

    def get_color(self, pid):
        if pid == "Idle":
            return self.IDLE_COLOR
        if pid not in self.color_map:
            self.color_map[pid] = self.COLORS[self.color_index % len(self.COLORS)]
            self.color_index += 1
        return self.color_map[pid]

    def draw(self, gantt_data):
        self.canvas.delete("all")
        if not gantt_data:
            self._draw_placeholder()
            return

        # Convert from [{pid, time}, ...] to [(pid, start, end), ...]
        timeline = self._convert_gantt(gantt_data)
        if not timeline:
            self._draw_placeholder()
            return

        # Merge consecutive
        timeline = self._merge_timeline(timeline)

        y_bottom = self.y_top + self.bar_height

        for pid, start, end in timeline:
            x1 = self.x_offset + start * self.unit_width
            x2 = self.x_offset + end * self.unit_width
            color = self.get_color(pid)

            text_color = "black" if pid != "Idle" else "#aaaaaa"
            display_text = pid if pid != "Idle" else "idle"

            self.canvas.create_rectangle(
                x1, self.y_top, x2, y_bottom,
                fill=color, outline="#ffffff", width=1
            )
            self.canvas.create_text(
                (x1 + x2) / 2, (self.y_top + y_bottom) / 2,
                text=display_text,
                fill=text_color, font=("Segoe UI", 9, "bold")
            )
            self.canvas.create_text(
                x1, y_bottom + 15,
                text=str(start),
                fill="#cccccc", font=("Segoe UI", 8)
            )

        if timeline:
            last_end = timeline[-1][2]
            x_last = self.x_offset + last_end * self.unit_width
            self.canvas.create_text(
                x_last, y_bottom + 15,
                text=str(last_end),
                fill="#cccccc", font=("Segoe UI", 8)
            )

            total_width = self.x_offset + (last_end + 2) * self.unit_width
            self.canvas.configure(scrollregion=(0, 0, total_width, 120))
            self.canvas.xview_moveto(1.0)

    def _convert_gantt(self, gantt_data):
        """Convert [{pid, time}, ...] to [(pid, start, end), ...]"""
        if not gantt_data:
            return []
        result = []
        for entry in gantt_data:
            pid = entry.get("pid", "Idle")
            t = entry.get("time", 0)
            result.append((pid, t, t + 1))
        return result

    def _merge_timeline(self, timeline):
        if not timeline:
            return []
        merged = [list(timeline[0])]
        for i in range(1, len(timeline)):
            pid, start, end = timeline[i]
            prev = merged[-1]
            if pid == prev[0] and start == prev[2]:
                prev[2] = end
            else:
                merged.append([pid, start, end])
        return [tuple(m) for m in merged]

    def clear(self):
        self.canvas.delete("all")
        self.color_map.clear()
        self.color_index = 0
        self._draw_placeholder()
