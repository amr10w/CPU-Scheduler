from process import Process

class FCFS:
    def __init__(self):
        self.ready_queue = []
        self.current_process = None
        self.completed_processes = []
        self.current_time = 0

    def add_process(self, pid, arrival_time, burst_time):
        p = Process(pid, arrival_time, burst_time)
        self.ready_queue.append(p)

    def tick(self, processes_in_list):
        # 1. Arrival Logic: Check if anyone new just arrived
        for p in processes_in_list:
            if p.arrival_time == self.current_time and p not in self.ready_queue and p != self.current_process:
                if not p.is_completed:
                    self.ready_queue.append(p)

        # 2. Idle Logic: If nothing is running and no one is waiting
        if self.current_process is None and not self.ready_queue:
            self.current_time += 1
            return

        # 3. Selection Logic: If CPU is free, grab the next process
        if self.current_process is None:
            self.current_process = self.ready_queue.pop(0)
            if self.current_process.start_time == -1:
                self.current_process.start_time = self.current_time

        # 4. Execution Logic: Run for 1 unit
        finished = self.current_process.execute_one_unit()

        # 5. Completion Logic
        if finished:
            self.current_process.completion_time = self.current_time + 1
            self.current_process.calculate_times()
            self.completed_processes.append(self.current_process)
            self.current_process = None

        self.current_time += 1