from process import Process


class SJFScheduler:

    def __init__(self, preemptive=False):
        self.preemptive = preemptive
        self.processes = []
        self.current_time = 0
        self.current_process = None
        self.completed_processes = []
        self.gantt_chart = []

    # ------------------------------------------------------------------

    def add_process(self, process):
        self.processes.append(process)

    def _ready_queue(self):
        """Returns arrived, incomplete processes sorted by SJF criteria."""
        available = [
            p for p in self.processes
            if p.has_arrived(self.current_time) and not p.is_completed
        ]

        if self.preemptive:
            # SRTF: sort by remaining time
            return sorted(available, key=lambda p: (p.remaining_time, p.arrival_time, p.pid))
        else:
            # Non-preemptive: sort by burst time
            return sorted(available, key=lambda p: (p.burst_time, p.arrival_time, p.pid))

    # ------------------------------------------------------------------

    def tick(self):
        queue = self._ready_queue()

        if queue:
            top = queue[0]

            if self.preemptive:
                # SRTF: always pick shortest remaining time (can preempt)
                self.current_process = top
            elif self.current_process is None or self.current_process.is_completed:
                # Non-preemptive: only switch when CPU is free
                self.current_process = top
        else:
            self.current_process = None  # idle

        # Execute 1 unit
        if self.current_process:
            if self.current_process.start_time == -1:
                self.current_process.start_time = self.current_time

            finished = self.current_process.execute_one_unit()

            if finished:
                self.current_process.completion_time = self.current_time + 1
                self.current_process.calculate_times()
                self.completed_processes.append(self.current_process)

        # Record Gantt entry
        self.gantt_chart.append({
            "pid":  self.current_process.pid if self.current_process else "Idle",
            "time": self.current_time,
        })

        self.current_time += 1

        return {
            "time":    self.current_time - 1,
            "running": self.current_process.pid if self.current_process else None,
            "remaining_times": {
                p.pid: p.remaining_time for p in self.processes if not p.is_completed
            },
        }

    # ------------------------------------------------------------------

    def run_all(self):
        while any(not p.is_completed for p in self.processes):
            if not self._ready_queue() and self.current_process is None:
                self.current_time += 1
                continue
            self.tick()

    # ------------------------------------------------------------------

    def average_waiting_time(self):
        done = [p for p in self.processes if p.is_completed]
        return sum(p.waiting_time for p in done) / len(done) if done else 0.0

    def average_turnaround_time(self):
        done = [p for p in self.processes if p.is_completed]
        return sum(p.turnaround_time for p in done) / len(done) if done else 0.0

    # ------------------------------------------------------------------

    def reset(self):
        for p in self.processes:
            p.reset()
        self.current_time = 0
        self.current_process = None
        self.completed_processes = []
        self.gantt_chart = []

    # ------------------------------------------------------------------

    def _print_summary(self):
        print("\n" + "=" * 60)
        name = "SJF (Preemptive - SRTF)" if self.preemptive else "SJF (Non-Preemptive)"
        print(f"  Scheduler: {name}")
        print("=" * 60)
        print(f"{'PID':<6} {'Arrival':<10} {'Burst':<8} {'Completion':<12} "
              f"{'Waiting':<10} {'Turnaround'}")
        print("-" * 60)
        for p in sorted(self.completed_processes, key=lambda x: x.pid):
            print(f"{p.pid:<6} {p.arrival_time:<10} {p.burst_time:<8} "
                  f"{p.completion_time:<12} {p.waiting_time:<10} {p.turnaround_time}")
        print("-" * 60)
        print(f"  Avg Waiting Time:    {self.average_waiting_time():.2f}")
        print(f"  Avg Turnaround Time: {self.average_turnaround_time():.2f}")
        print("=" * 60)