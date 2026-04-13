from core.process import Process
from core.base_scheduler import BaseScheduler


class Engine:
    def __init__(self):
        self.processes: list[Process] = []
        self.scheduler: BaseScheduler | None = None
        self.is_running: bool = False

    def add_process(self, pid, arrival_time, burst_time, priority=0):
        p = Process(pid, arrival_time, burst_time, priority)
        self.processes.append(p)
        return p

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler
        for p in self.processes:
            self.scheduler.add_process(p)

    def start(self):
        assert self.scheduler is not None, "Call set_scheduler() before start()"
        assert self.processes, "Add at least one process before start()"
        self.is_running = True

    def step(self):
        if not self.is_running:
            return None
        if self.scheduler.is_done():
            self.is_running = False
            return None
        return self.scheduler.tick()

    def pause(self):
        self.is_running = False

    def resume(self):
        assert self.scheduler is not None
        if not self.scheduler.is_done():
            self.is_running = True

    def toggle_pause(self):
        if self.is_running:
            self.pause()
        else:
            self.resume()

    def run_all(self):
        assert self.scheduler is not None
        self.start()
        while not self.scheduler.is_done():
            self.scheduler.tick()
        self.is_running = False

    def reset(self):
        self.is_running = False
        if self.scheduler:
            self.scheduler.reset()

    @property
    def is_paused(self):
        return (
            not self.is_running
            and self.scheduler is not None
            and not self.scheduler.is_done()
            and self.scheduler.current_time > 0
        )

    def is_done(self):
        return self.scheduler is not None and self.scheduler.is_done()

    def get_stats(self):
        assert self.scheduler is not None
        return {
            "avg_waiting": self.scheduler.average_waiting_time(),
            "avg_turnaround": self.scheduler.average_turnaround_time(),
            "gantt": self.scheduler.gantt_chart,
        }

    def get_process_table(self):
        return [
            {
                "pid": p.pid,
                "arrival": p.arrival_time,
                "burst": p.burst_time,
                "priority": p.priority,
                "completion": p.completion_time,
                "waiting": p.waiting_time,
                "turnaround": p.turnaround_time,
            }
            for p in self.processes
        ]
