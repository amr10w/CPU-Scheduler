from core.process import Process
from core.base_scheduler import BaseScheduler

class FCFS(BaseScheduler):
    def __init__(self):
        super().__init__()
        self.ready_queue = []

    def tick(self):
        for p in self.processes:
            if p.arrival_time == self.current_time and p not in self.ready_queue and p != self.current_process:
                if not p.is_completed:
                    self.ready_queue.append(p)

        if self.current_process is None and not self.ready_queue:
            self.gantt_chart.append({"pid": "Idle", "time": self.current_time})
            self.current_time += 1
            return {"time": self.current_time - 1, "running": None, "remaining": {}}

        if self.current_process is None:
            self.current_process = self.ready_queue.pop(0)
            if self.current_process.start_time == -1:
                self.current_process.start_time = self.current_time

        finished = self.current_process.execute_one_unit()

        if finished:
            self.current_process.completion_time = self.current_time + 1
            self.current_process.calculate_times()
            self.current_process = None

        self.gantt_chart.append({
            "pid": self.current_process.pid if self.current_process else "Idle",
            "time": self.current_time,
        })
        self.current_time += 1

        return {
            "time": self.current_time - 1,
            "running": self.current_process.pid if self.current_process else None,
            "remaining": {p.pid: p.remaining_time for p in self.processes if not p.is_completed},
        }

    def reset(self):
        self._base_reset()
        self.ready_queue = []
