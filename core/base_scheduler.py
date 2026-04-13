from abc import ABC, abstractmethod
from .process import Process

class BaseScheduler(ABC):
    """
    Abstract base class for all CPU scheduling algorithms.
    The Engine calls tick() every time unit and reads gantt_chart for the GUI.
    """
    def __init__(self):
        self.processes = []
        self.current_time=0
        self.current_process= None
        self.gantt_chart = []   # [{"pid": "P1", "time": 0}, ...]
        
    def add_process(self,process):
        self.processes.append(process)
        
    @abstractmethod
    def tick(self):
        """
        Advance the scheduler by 1 time unit.
        Must return:
          {"time": int, "running": str | None, "remaining": {pid: int}}
        """
        
    @abstractmethod
    def reset(self):
        """Reset everything to the initial state."""
        
    # ── Shared statistics (same formula for all algorithms) ──────────────
    def average_waiting_time(self):
        done = [p for p in self.processes if p.is_completed]
        return sum(p.waiting_time for p in done) / len(done) if done else 0.0

    def average_turnaround_time(self):
        done = [p for p in self.processes if p.is_completed]
        return sum(p.turnaround_time for p in done) / len(done) if done else 0.0

    def is_done(self):
        return all(p.is_completed for p in self.processes)
    
    # ── Shared reset helper ───────────────────────────────────────────────

    def _base_reset(self):
        for p in self.processes:
            p.reset()
        self.current_time = 0
        self.current_process = None
        self.gantt_chart = []