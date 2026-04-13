from .process import Process
from .base_scheduler import BaseScheduler


class Engine:
    """
    Owns the process list and drives any scheduler tick-by-tick.

    The GUI:
      1. Creates an Engine
      2. Adds processes via add_process()
      3. Sets a scheduler via set_scheduler()
      4. Calls start()
      5. Calls step() every 1 second from a GUI timer
      6. Uses pause() / resume() / toggle_pause() for the pause button
    """

    def __init__(self):
        self.processes: list[Process] = []
        self.scheduler: BaseScheduler | None = None
        self.is_running: bool = False

    # ── Setup ──────────────────────────────────────────────────────────────

    def add_process(
        self,
        pid: str,
        arrival_time: int,
        burst_time: int,
        priority: int = 0,
    ) -> Process:
        """Create and store a process. Returns the Process object."""
        p = Process(pid, arrival_time, burst_time, priority)
        self.processes.append(p)
        return p

    def set_scheduler(self, scheduler: BaseScheduler) -> None:
        """
        Attach a scheduler and hand it the current process list.
        Call this AFTER all add_process() calls and BEFORE start().
        """
        self.scheduler = scheduler
        for p in self.processes:
            self.scheduler.add_process(p)

    # ── Simulation controls ────────────────────────────────────────────────

    def start(self) -> None:
        """Begin the simulation. Must call set_scheduler() first."""
        assert self.scheduler is not None, "Call set_scheduler() before start()"
        assert self.processes,             "Add at least one process before start()"
        self.is_running = True

    def step(self) -> dict | None:
        """
        Advance the simulation by exactly 1 time unit.
        Call this from your GUI timer every second.

        Returns:
            dict  — tick result while simulation is running and not paused:
                    {
                        "time":      int,         # current time unit
                        "running":   str | None,  # pid of running process or None (idle)
                        "remaining": {pid: int},  # remaining burst for incomplete processes
                    }
            None  — when paused OR when simulation is finished.
                    Check is_done() to tell the two apart.
        """
        # Paused or not started — do nothing this tick
        if not self.is_running:
            return None

        # Finished — stop automatically
        if self.scheduler.is_done():
            self.is_running = False
            return None

        return self.scheduler.tick()

    def pause(self) -> None:
        """Pause the simulation. State is fully preserved."""
        self.is_running = False

    def resume(self) -> None:
        """Resume from exactly where it was paused."""
        assert self.scheduler is not None, "Call set_scheduler() before resume()"
        if not self.scheduler.is_done():
            self.is_running = True

    def toggle_pause(self) -> None:
        """
        Single method for a Pause/Resume button.
        Pauses if running, resumes if paused.
        """
        if self.is_running:
            self.pause()
        else:
            self.resume()

    def run_all(self) -> None:
        """
        Run the entire simulation instantly (no GUI timer needed).
        Useful for testing or showing final results immediately.
        """
        assert self.scheduler is not None, "Call set_scheduler() before run_all()"
        self.start()
        while not self.scheduler.is_done():
            self.scheduler.tick()
        self.is_running = False

    def reset(self) -> None:
        """
        Reset the simulation to its initial state.
        After reset, call start() again to run.
        """
        self.is_running = False
        if self.scheduler:
            self.scheduler.reset()

    # ── State queries ──────────────────────────────────────────────────────

    @property
    def is_paused(self) -> bool:
        """True if the simulation was started but is currently paused."""
        return (
            not self.is_running
            and self.scheduler is not None
            and not self.scheduler.is_done()
            and self.scheduler.current_time > 0   # has started
        )

    def is_done(self) -> bool:
        """True if every process has completed."""
        return self.scheduler is not None and self.scheduler.is_done()

    # ── Results (read after is_done() is True) ─────────────────────────────

    def get_stats(self) -> dict:
        """
        Returns average waiting and turnaround times, plus the Gantt chart.
        Call after the simulation finishes.
        """
        assert self.scheduler is not None
        return {
            "avg_waiting":    self.scheduler.average_waiting_time(),
            "avg_turnaround": self.scheduler.average_turnaround_time(),
            "gantt":          self.scheduler.gantt_chart,
        }

    def get_process_table(self) -> list[dict]:
        """
        Returns per-process results for the results table in the GUI.
        Only includes all processes.
        """
        return [
            {
                "pid":        p.pid,
                "arrival":    p.arrival_time,
                "burst":      p.burst_time,
                "priority":   p.priority,
                "completion": p.completion_time,
                "waiting":    p.waiting_time,
                "turnaround": p.turnaround_time,
            }
            for p in self.processes
     
        ]