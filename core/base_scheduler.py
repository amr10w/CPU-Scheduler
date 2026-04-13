from abc import ABC, abstractmethod
from core.process import Process

class BaseScheduler(ABC):
    def __init__(self):
        self.processes = []
        self.current_time = 0
        self.current_process = None
        self.gantt_chart = []

    def add_process(self, process):
        self.processes.append(process)

    @abstractmethod
    def tick(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    def average_waiting_time(self):
        done = [p for p in self.processes if p.is_completed]
        return sum(p.waiting_time for p in done) / len(done) if done else 0.0

    def average_turnaround_time(self):
        done = [p for p in self.processes if p.is_completed]
        return sum(p.turnaround_time for p in done) / len(done) if done else 0.0

    def is_done(self):
        return all(p.is_completed for p in self.processes)

    def _base_reset(self):
        for p in self.processes:
            p.reset()
        self.current_time = 0
        self.current_process = None
        self.gantt_chart = []
