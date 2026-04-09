"""
Process Model
=============
Represents a single process in the CPU scheduler.
This is the core data structure used by all scheduling algorithms.
"""


class Process:
    """
    Represents a single process in the CPU scheduler.

    Attributes:
        pid (str): Process identifier (e.g., "P1")
        arrival_time (int): Time when process arrives in ready queue
        burst_time (int): Total CPU time needed
        priority (int): Priority level (lower number = higher priority)
        remaining_time (int): CPU time still needed
        start_time (int): Time when process first gets CPU (-1 if not started)
        completion_time (int): Time when process finishes
        waiting_time (int): Total time spent waiting
        turnaround_time (int): Total time from arrival to completion
        is_completed (bool): Whether the process has finished execution
    """

    def __init__(self, pid, arrival_time, burst_time, priority=0):
        # --- Given by user ---
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority

        # --- Updated during simulation ---
        self.remaining_time = burst_time
        self.start_time = -1            # -1 means "not started yet"
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.is_completed = False

    def execute_one_unit(self):
        """
        Simulate executing this process for 1 time unit.

        Returns:
            True if the process just finished, False otherwise.
        """
        self.remaining_time -= 1
        if self.remaining_time == 0:
            self.is_completed = True
            return True
        return False

    def calculate_times(self):
        """
        Calculate waiting time and turnaround time.
        Call this after the process completes.

        Formulas:
            turnaround_time = completion_time - arrival_time
            waiting_time = turnaround_time - burst_time
        """
        self.turnaround_time = self.completion_time - self.arrival_time
        self.waiting_time = self.turnaround_time - self.burst_time

    def has_arrived(self, current_time):
        """Check if this process has arrived by the given time."""
        return self.arrival_time <= current_time

    def reset(self):
        """Reset process to initial state (useful for re-running simulation)."""
        self.remaining_time = self.burst_time
        self.start_time = -1
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.is_completed = False

    def __repr__(self):
        """String representation for debugging."""
        return (f"Process({self.pid}, arrival={self.arrival_time}, "
                f"burst={self.burst_time}, remaining={self.remaining_time}, "
                f"priority={self.priority})")