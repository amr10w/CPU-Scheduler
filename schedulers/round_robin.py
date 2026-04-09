"""
Round Robin Scheduler
=====================
Each process gets a fixed time slice (quantum).
After the quantum expires, the process goes to the back of the ready queue.
This is inherently preemptive.

Key behaviors:
    - Processes are served in FIFO order
    - New arrivals join the queue BEFORE the preempted process
    - If a process finishes before its quantum expires, CPU moves to next immediately
"""

from collections import deque
from schedulers.base_scheduler import BaseScheduler


class RoundRobinScheduler(BaseScheduler):

    def __init__(self, quantum=2):
        super().__init__(f"Round Robin (Q={quantum})")
        self.quantum = quantum
        self.ready_queue = deque()      # FIFO queue of ready processes
        self.quantum_remaining = 0      # Time left in current quantum
        self.arrived_pids = set()       # Track which processes entered the queue

    def _enqueue_new_arrivals(self):
        """
        Check for processes that have just arrived and add them to the queue.
        Maintains FCFS order among processes arriving at the same time.
        """
        new_arrivals = [
            p for p in self.processes
            if p.has_arrived(self.current_time)
            and p.pid not in self.arrived_pids
            and not p.is_completed
        ]
        # Sort by arrival time, then PID for deterministic ordering
        new_arrivals.sort(key=lambda p: (p.arrival_time, p.pid))

        for p in new_arrivals:
            self.ready_queue.append(p)
            self.arrived_pids.add(p.pid)

    def get_next_process(self):
        """
        Round Robin Logic:
            1. Check for new arrivals and add them to queue
            2. If current process still has quantum remaining, continue it
            3. If quantum expired, put current process back in queue
            4. Pick next process from front of queue
            5. Reset quantum counter
        """
        # Add newly arrived processes
        self._enqueue_new_arrivals()

        # Check if current process should continue
        if self.current_running and not self.current_running.is_completed:
            if self.quantum_remaining > 0:
                # Still has quantum time - continue running
                return self.current_running
            else:
                # Quantum expired!
                # First: add any new arrivals (they go BEFORE preempted process)
                self._enqueue_new_arrivals()
                # Then: put the preempted process at the back of queue
                self.ready_queue.append(self.current_running)
                self.current_running = None

        # Pick next process from queue
        if not self.ready_queue:
            if self.has_pending_processes():
                return None  # CPU idle - waiting for arrivals
            return None

        next_process = self.ready_queue.popleft()
        self.quantum_remaining = self.quantum  # Reset quantum
        return next_process

    def step(self):
        """
        Override step() to handle quantum countdown.
        
        The base class step() doesn't know about quantum,
        so we add the quantum countdown logic here.
        """
        # Check if all done
        if not self.has_pending_processes():
            return "DONE"

        # Get next process (handles quantum logic)
        next_process = self.get_next_process()

        if next_process is None:
            # CPU idle
            self.timeline.append(("IDLE", self.current_time, self.current_time + 1))
            self.current_time += 1
            self.current_running = None
            return None

        # Record first CPU access
        if next_process.start_time == -1:
            next_process.start_time = self.current_time

        self.current_running = next_process

        # Execute for 1 time unit
        just_finished = next_process.execute_one_unit()
        self.quantum_remaining -= 1  # Count down the quantum

        # Record in timeline
        self.timeline.append(
            (next_process.pid, self.current_time, self.current_time + 1)
        )

        # Advance clock
        self.current_time += 1

        # Handle completion
        if just_finished:
            next_process.completion_time = self.current_time
            next_process.calculate_times()
            self.completed.append(next_process)
            self.current_running = None
            self.quantum_remaining = 0  # Reset quantum

        return next_process

    def add_process(self, process):
        """
        Override to support dynamic process addition.
        The process will be detected by _enqueue_new_arrivals() on next step.
        """
        self.processes.append(process)