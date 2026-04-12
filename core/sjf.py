from process import Process
from base_scheduler import BaseScheduler


class SJFScheduler(BaseScheduler):

    def __init__(self, preemptive=False):
        super().__init__()
        self.preemptive = preemptive
 

    # ------------------------------------------------------------------

   
    def _ready_queue(self):
        """Returns arrived, incomplete processes sorted by SJF criteria."""
        available = [
            p for p in self.processes
            if p.has_arrived(self.current_time) and not p.is_completed
        ]

        if self.preemptive:
            # SRTF: sort by remaining time
            return sorted(available, key=lambda p: (p.remaining_time, p.arrival_time, p.pid))
        else:
            # Non-preemptive: sort by burst time
            return sorted(available, key=lambda p: (p.burst_time, p.arrival_time, p.pid))

    # ------------------------------------------------------------------

    def tick(self):
        queue = self._ready_queue()

        if queue:
            top = queue[0]

            if self.preemptive:
                # SRTF: always pick shortest remaining time (can preempt)
                self.current_process = top
            elif self.current_process is None or self.current_process.is_completed:
                # Non-preemptive: only switch when CPU is free
                self.current_process = top
        else:
            self.current_process = None  # idle

        # Execute 1 unit
        if self.current_process:
            if self.current_process.start_time == -1:
                self.current_process.start_time = self.current_time

            finished = self.current_process.execute_one_unit()

            if finished:
                self.current_process.completion_time = self.current_time + 1
                self.current_process.calculate_times()
                self.completed_processes.append(self.current_process)

        # Record Gantt entry
        self.gantt_chart.append({
            "pid":  self.current_process.pid if self.current_process else "Idle",
            "time": self.current_time,
        })

        self.current_time += 1

        return {
            "time":    self.current_time - 1,
            "running": self.current_process.pid if self.current_process else None,
            "remaining_times": {
                p.pid: p.remaining_time for p in self.processes if not p.is_completed
            },
        }

   

    

    def reset(self):
        self._base_reset()

   