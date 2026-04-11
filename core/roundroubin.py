from collections import deque
from process import Process

class RoundRobinScheduler:
    def __init__(self, quantum):
        self.quantum = quantum
        self.ready_queue = deque()
        self.time_in_quantum = 0
        self.completed_processes = []
        self.current_process = None

    def add_process(self,process):
        self.ready_queue.append(process)

    def add_process(self,  pid, arrival_time, burst_time):
        p = Process(pid,arrival_time,burst_time)
        self.ready_queue.append(p)

    def tick(self, current_time, processes_in_list):
        """
        Called by the Engine every 1 second.
        current_time: The master clock from the Engine.
        processes_in_list: List of all Process objects created in the GUI.
        """

        # 1. Arrival Logic: Check if anyone new just arrived
        for p in processes_in_list:
            # If process arrives now and isn't already in the queue or running
            if p.arrival_time == current_time and p not in self.ready_queue and p != self.current_process:
                if not p.is_completed:
                    self.ready_queue.append(p)

        # 2. Idle Logic: If nothing is running and no one is waiting
        if self.current_process is None and not self.ready_queue:
            return  # Engine will call tick again at current_time + 1

        # 3. Selection Logic: If CPU is free, grab the next process
        if self.current_process is None:
            self.current_process = self.ready_queue.popleft()
            self.time_in_quantum = 0
            if self.current_process.start_time == -1:
                self.current_process.start_time = current_time

        # 4. Execution Logic: Run for 1 unit
        finished = self.current_process.execute_one_unit()
        self.time_in_quantum += 1

        self._print_state(self.current_process, processes_in_list, current_time)
        # 5. Preemption/Completion Logic
        if finished:
            self.current_process.completion_time = current_time + 1  # Ends at end of this unit
            self.current_process.calculate_times()
            self.completed_processes.append(self.current_process)
            self.current_process = None
        elif self.time_in_quantum >= self.quantum:
            # Time slice is over - check for mid-tick arrivals before re-queueing
            for p in processes_in_list:
                if p.arrival_time == (current_time + 1) and p not in self.ready_queue:
                    self.ready_queue.append(p)

            self.ready_queue.append(self.current_process)
            self.current_process = None



    def _print_state(self, running_process, all_processes,current_time):
        remaining = {p.pid: p.remaining_time for p in all_processes if not p.is_completed}
        print(f"T={current_time:<6} | {running_process.pid:<8} | {remaining}")

    def _print_summary(self):
        print("\n" + "=" * 60)
        print(f"{'PID':<6} {'Arrival':<10} {'Burst':<8} {'Completion':<12} {'Waiting':<10} {'Turnaround'}")
        print("-" * 60)
        for p in self.completed_processes:
            print(f"{p.pid:<6} {p.arrival_time:<10} {p.burst_time:<8} {p.completion_time:<12} {p.waiting_time:<10} {p.turnaround_time}")

        avg_wt  = sum(p.waiting_time    for p in self.completed_processes) / len(self.completed_processes)
        avg_tat = sum(p.turnaround_time for p in self.completed_processes) / len(self.completed_processes)
        print("-" * 60)
        print(f"Average Waiting Time    : {avg_wt:.2f}")
        print(f"Average Turnaround Time : {avg_tat:.2f}")


