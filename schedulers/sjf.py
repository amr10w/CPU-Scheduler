"""
SJF (Shortest Job First) Scheduler
====================================
Selects the process with the shortest burst/remaining time.

Two modes:
    - Non-Preemptive: once started, the process runs to completion
    - Preemptive (SRTF): a new process with shorter remaining time
      can preempt the currently running process
"""

from schedulers.base_scheduler import BaseScheduler


class SJFScheduler(BaseScheduler):

    def __init__(self, preemptive=False):
        name = "SJF (Preemptive - SRTF)" if preemptive else "SJF (Non-Preemptive)"
        super().__init__(name)
        self.preemptive = preemptive

    def get_next_process(self):
        """
        SJF Logic:

        Non-Preemptive:
            1. If a process is running, let it finish
            2. Otherwise, pick process with shortest BURST TIME
            3. Tie-breaker: earlier arrival time

        Preemptive (SRTF):
            1. Always pick process with shortest REMAINING TIME
            2. This may preempt the current process
            3. Tie-breaker: earlier arrival time
        """
        ready = self.get_ready_queue()

        if not ready:
            return None

        if self.preemptive:
            # SRTF: always pick shortest remaining time
            ready.sort(key=lambda p: (p.remaining_time, p.arrival_time))
            return ready[0]
        else:
            # Non-preemptive: let current process finish
            if self.current_running and not self.current_running.is_completed:
                return self.current_running

            # Pick shortest burst time
            ready.sort(key=lambda p: (p.burst_time, p.arrival_time))
            return ready[0]