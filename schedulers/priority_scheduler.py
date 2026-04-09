"""
Priority Scheduler
==================
Selects the process with the highest priority.
Convention: LOWER priority number = HIGHER priority.

Two modes:
    - Non-Preemptive: running process continues until done
    - Preemptive: higher priority process can interrupt current one
"""

from schedulers.base_scheduler import BaseScheduler


class PriorityScheduler(BaseScheduler):

    def __init__(self, preemptive=False):
        name = "Priority (Preemptive)" if preemptive else "Priority (Non-Preemptive)"
        super().__init__(name)
        self.preemptive = preemptive

    def get_next_process(self):
        """
        Priority Logic:

        Non-Preemptive:
            1. If a process is running, let it finish
            2. Otherwise, pick process with lowest priority number
            3. Tie-breaker: earlier arrival time

        Preemptive:
            1. Always pick process with lowest priority number
            2. This may preempt the current process
            3. Tie-breaker: earlier arrival time
        """
        ready = self.get_ready_queue()

        if not ready:
            return None

        if self.preemptive:
            # Always pick highest priority (lowest number)
            ready.sort(key=lambda p: (p.priority, p.arrival_time))
            return ready[0]
        else:
            # Non-preemptive: let current process finish
            if self.current_running and not self.current_running.is_completed:
                return self.current_running

            # Pick highest priority (lowest number)
            ready.sort(key=lambda p: (p.priority, p.arrival_time))
            return ready[0]