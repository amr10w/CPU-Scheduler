"""
FCFS (First Come First Served) Scheduler
=========================================
The simplest scheduling algorithm.
Processes are executed in the order they arrive.
Non-preemptive: once a process starts, it runs until completion.
"""

from schedulers.base_scheduler import BaseScheduler


class FCFSScheduler(BaseScheduler):

    def __init__(self):
        super().__init__("FCFS")

    def get_next_process(self):
        """
        FCFS Logic:
            1. If a process is currently running, let it finish (non-preemptive)
            2. Otherwise, pick the process that arrived earliest
            3. Tie-breaker: lower PID goes first
        """
        ready = self.get_ready_queue()

        if not ready:
            return None

        # Non-preemptive: let current process finish
        if self.current_running and not self.current_running.is_completed:
            return self.current_running

        # Pick the process that arrived first
        ready.sort(key=lambda p: (p.arrival_time, p.pid))
        return ready[0]