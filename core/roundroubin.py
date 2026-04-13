from collections import deque
from core.process import Process
from core.base_scheduler import BaseScheduler

class RoundRobinScheduler(BaseScheduler):
    def __init__(self, quantum=5):
        super().__init__()
        self.quantum = quantum
        self.ready_queue = deque()
        self.time_in_quantum = 0

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
            self.current_process = self.ready_queue.popleft()
            self.time_in_quantum = 0
            if self.current_process.start_time == -1:
                self.current_process.start_time = self.current_time

        finished = self.current_process.execute_one_unit()
        self.time_in_quantum += 1

        if finished:
            self.current_process.completion_time = self.current_time + 1
            self.current_process.calculate_times()
            self.current_process = None
        elif self.time_in_quantum >= self.quantum:
            for p in self.processes:
                if p.arrival_time == self.current_time + 1 \
                   and p not in self.ready_queue and not p.is_completed:
                    self.ready_queue.append(p)
            self.ready_queue.append(self.current_process)
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
        self.ready_queue = deque()
        self.time_in_quantum = 0
