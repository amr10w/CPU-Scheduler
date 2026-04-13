"""
Built-in Test Cases
===================
Pre-configured test scenarios for each scheduling algorithm.
Each test case demonstrates key features of that algorithm.
"""


TEST_CASES = {
    "FCFS": {
        "name": "FCFS — Basic Convoy Effect",
        "description": (
            "Shows FCFS serving processes in arrival order.\n"
            "P1 has a long burst causing P2, P3 to wait (convoy effect).\n"
            "Notice: shorter jobs wait behind the long one."
        ),
        "scheduler": "FCFS",
        "quantum": None,
        "processes": [
            # (pid, arrival, burst, priority)
            ("P1", 0, 8, 0),
            ("P2", 1, 2, 0),
            ("P3", 2, 3, 0),
            ("P4", 3, 1, 0),
            ("P5", 4, 4, 0),
        ],
    },

    "SJF (Non-Preemptive)": {
        "name": "SJF Non-Preemptive — Shortest Job First",
        "description": (
            "CPU picks the shortest burst when it becomes free.\n"
            "P1 runs first (arrives at 0). After P1 finishes, P4 (burst=1)\n"
            "runs before P2 (burst=6) even though P2 arrived earlier.\n"
            "Shows how SJF minimizes average waiting time."
        ),
        "scheduler": "SJF (Non-Preemptive)",
        "quantum": None,
        "processes": [
            ("P1", 0, 3, 0),
            ("P2", 1, 6, 0),
            ("P3", 2, 2, 0),
            ("P4", 3, 1, 0),
            ("P5", 5, 4, 0),
        ],
    },

    "SJF (Preemptive)": {
        "name": "SJF Preemptive (SRTF) — Shortest Remaining Time",
        "description": (
            "Running process gets preempted if a new arrival has\n"
            "shorter remaining time.\n"
            "P1 starts, but P3 (burst=1) arrives at t=2 and preempts.\n"
            "Watch the Gantt chart for context switches."
        ),
        "scheduler": "SJF (Preemptive)",
        "quantum": None,
        "processes": [
            ("P1", 0, 7, 0),
            ("P2", 1, 4, 0),
            ("P3", 2, 1, 0),
            ("P4", 3, 3, 0),
            ("P5", 6, 2, 0),
        ],
    },

    "Priority (Non-Preemptive)": {
        "name": "Priority Non-Preemptive — Highest Priority First",
        "description": (
            "Lower priority number = higher priority.\n"
            "P1 runs first (only one at t=0). When P1 finishes,\n"
            "P4 (priority=1) runs before P2 (priority=3) and P3 (priority=5).\n"
            "Shows priority-based selection without preemption."
        ),
        "scheduler": "Priority (Non-Preemptive)",
        "quantum": None,
        "processes": [
            ("P1", 0, 4, 2),
            ("P2", 1, 3, 3),
            ("P3", 2, 5, 5),
            ("P4", 3, 2, 1),
            ("P5", 4, 6, 4),
        ],
    },

    "Priority (Preemptive)": {
        "name": "Priority Preemptive — Preempts on Higher Priority",
        "description": (
            "Running process is preempted when a higher-priority\n"
            "process arrives.\n"
            "P1 (priority=4) starts, but P2 (priority=2) preempts at t=1.\n"
            "Then P4 (priority=1) preempts P2 at t=3.\n"
            "Watch the Gantt chart for frequent switches."
        ),
        "scheduler": "Priority (Preemptive)",
        "quantum": None,
        "processes": [
            ("P1", 0, 5, 4),
            ("P2", 1, 4, 2),
            ("P3", 2, 3, 5),
            ("P4", 3, 2, 1),
            ("P5", 5, 3, 3),
        ],
    },

    "Round Robin": {
        "name": "Round Robin — Time Quantum = 3",
        "description": (
            "Each process runs for at most 3 time units, then\n"
            "goes to the back of the queue.\n"
            "P1 (burst=10) runs 3 units, then P2 gets a turn, etc.\n"
            "Shows fair CPU sharing and how longer jobs take multiple rounds.\n"
            "Try adding a process dynamically during the simulation!"
        ),
        "scheduler": "Round Robin",
        "quantum": 3,
        "processes": [
            ("P1", 0, 10, 0),
            ("P2", 1, 4, 0),
            ("P3", 2, 6, 0),
            ("P4", 3, 3, 0),
            ("P5", 5, 7, 0),
        ],
    },
}


def get_test_case(scheduler_name):
    """Get test case for a scheduler. Returns dict or None."""
    return TEST_CASES.get(scheduler_name, None)


def get_all_test_names():
    """Return list of (scheduler_name, test_case_name) tuples."""
    return [(k, v["name"]) for k, v in TEST_CASES.items()]
