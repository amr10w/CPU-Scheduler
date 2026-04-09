"""
Base Scheduler
==============
Abstract base class that all scheduling algorithms inherit from.
Contains common logic so we don't repeat code in every scheduler.
"""

from abc import ABC, abstractmethod


class BaseScheduler(ABC):
    """
    Abstract base class for all CPU scheduling algorithms.

    Every scheduler must implement:
        get_next_process() - decides which process runs next

    Common functionality provided:
        - add_process()     : add a process to the system
        - step()            : execute one time unit
        - is_complete()     : check if all processes are done
        - get_avg_waiting_time()     : calculate average WT
        - get_avg_turnaround_time()  : calculate average TAT
        - get_merged_timeline()      : merge consecutive same-process blocks
    """

    def __init__(self, name):
        self.name = name                # Display name of the algorithm
        self.processes = []             # All processes in the system
        self.current_time = 0           # Current simulation clock
        self.timeline = []              # [(pid, start, end), ...] for Gantt chart
        self.completed = []             # List of completed processes
        self.current_running = None     # Currently running process (or None)

    def add_process(self, process):
        """
        Add a process to the scheduler.
        Can be called before or during simulation (dynamic addition).
        """
        self.processes.append(process)

    def get_ready_queue(self):
        """
        Get all processes that have arrived and are NOT completed.
        This is the pool of processes available to run.
        """
        return [
            p for p in self.processes
            if p.has_arrived(self.current_time) and not p.is_completed
        ]

    def has_pending_processes(self):
        """Check if there are any processes that haven't finished yet."""
        return any(not p.is_completed for p in self.processes)

    @abstractmethod
    def get_next_process(self):
        """
        Select the next process to run.
        
        MUST be implemented by each scheduling algorithm.
        
        Returns:
            Process object - the process to run next
            None           - CPU should be idle (no ready process)
        """
        pass

    def step(self):
        """
        Execute ONE time unit of simulation.

        This is the heart of the simulator. Each call:
            1. Checks if simulation is done
            2. Asks the algorithm which process to run (get_next_process)
            3. Executes that process for 1 time unit
            4. Updates the timeline and process statistics

        Returns:
            Process object - the process that ran this time unit
            None          - CPU was idle this time unit
            "DONE"        - all processes have completed
        """
        # --- Check if all processes are done ---
        if not self.has_pending_processes():
            return "DONE"

        # --- Ask the algorithm: who runs next? ---
        next_process = self.get_next_process()

        if next_process is None:
            # No process is ready - CPU is idle
            self.timeline.append(("IDLE", self.current_time, self.current_time + 1))
            self.current_time += 1
            self.current_running = None
            return None

        # --- Record first time this process gets the CPU ---
        if next_process.start_time == -1:
            next_process.start_time = self.current_time

        self.current_running = next_process

        # --- Execute for 1 time unit ---
        just_finished = next_process.execute_one_unit()

        # --- Record in timeline for Gantt chart ---
        self.timeline.append(
            (next_process.pid, self.current_time, self.current_time + 1)
        )

        # --- Advance the clock ---
        self.current_time += 1

        # --- Handle process completion ---
        if just_finished:
            next_process.completion_time = self.current_time
            next_process.calculate_times()
            self.completed.append(next_process)
            self.current_running = None

        return next_process

    def is_complete(self):
        """Check if ALL processes have finished execution."""
        return (
            len(self.processes) > 0
            and all(p.is_completed for p in self.processes)
        )

    def get_avg_waiting_time(self):
        """
        Calculate average waiting time across all COMPLETED processes.
        Returns 0.0 if no processes have completed yet.
        """
        if not self.completed:
            return 0.0
        total = sum(p.waiting_time for p in self.completed)
        return total / len(self.completed)

    def get_avg_turnaround_time(self):
        """
        Calculate average turnaround time across all COMPLETED processes.
        Returns 0.0 if no processes have completed yet.
        """
        if not self.completed:
            return 0.0
        total = sum(p.turnaround_time for p in self.completed)
        return total / len(self.completed)

    def get_merged_timeline(self):
        """
        Merge consecutive timeline entries for the same process.

        Example:
            [(P1,0,1), (P1,1,2), (P2,2,3)] --> [(P1,0,2), (P2,2,3)]

        This makes the Gantt chart cleaner and easier to read.
        """
        if not self.timeline:
            return []

        merged = [list(self.timeline[0])]

        for i in range(1, len(self.timeline)):
            pid, start, end = self.timeline[i]
            prev_pid, prev_start, prev_end = merged[-1]

            if pid == prev_pid and start == prev_end:
                # Same process, consecutive time - extend the block
                merged[-1][2] = end
            else:
                # Different process or gap - new block
                merged.append([pid, start, end])

        return [tuple(m) for m in merged]