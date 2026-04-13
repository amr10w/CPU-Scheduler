<div align="center">

# ⚡ CPU Scheduler Simulator

### A Real-Time Desktop Application for Visualizing CPU Scheduling Algorithms

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FF6F00?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3/library/tkinter.html)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![OS](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue?style=for-the-badge)]()

<br>

*An interactive GUI application that simulates and visualizes six major CPU scheduling algorithms with live Gantt charts, real-time process tracking, and dynamic process injection.*

<br>

---

</div>

## 📋 Table of Contents

- [Features](#-features)
- [Supported Algorithms](#-supported-algorithms)
- [Screenshots](#-screenshots)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Built-in Test Cases](#-built-in-test-cases)
- [Architecture](#-architecture)
- [How It Works](#-how-it-works)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Simulation
- **Live Simulation** — 1 time unit mapped to 1 real second, watch scheduling happen in real-time
- **Instant Execution** — Run the entire simulation at once and view final results immediately
- **Dynamic Process Addition** — Add new processes on-the-fly while the simulation is running
- **Stop & Resume** — Full control over the simulation lifecycle

### Visualization
- **Live Gantt Chart** — Scrollable, color-coded timeline drawn progressively as the simulation runs
- **Process Status Table** — Real-time updates showing remaining burst, waiting time, turnaround time, and status indicators (🕐 Not Arrived → ⏳ Ready → 🔄 Running → ✅ Completed)
- **Statistics Panel** — Live metrics including current time, average waiting time, average turnaround time, completion progress, and running status

### User Experience
- **Smart Input Forms** — Only shows relevant fields per algorithm (e.g., Priority field hidden for FCFS/SJF/RR)
- **Built-in Test Cases** — Pre-configured scenarios for each algorithm with descriptions explaining key behaviors
- **Input Validation** — Comprehensive error checking with clear error messages
- **Scrollable Interface** — Handles any number of processes without layout overflow
- **Cross-Platform** — Works on Windows, macOS, and Linux

---

## 🔧 Supported Algorithms

| # | Algorithm | Type | Key Behavior |
|---|-----------|------|--------------|
| 1 | **FCFS** | Non-Preemptive | First Come, First Served — processes execute in arrival order |
| 2 | **SJF** | Non-Preemptive | Shortest Job First — picks shortest burst when CPU is free |
| 3 | **SRTF** | Preemptive | Shortest Remaining Time First — preempts if a shorter job arrives |
| 4 | **Priority** | Non-Preemptive | Highest priority (lowest number) runs when CPU is free |
| 5 | **Priority** | Preemptive | Preempts running process if higher priority arrives |
| 6 | **Round Robin** | Preemptive | Time-sliced with configurable quantum — fair CPU sharing |

---

## 📸 Screenshots

> *Run the application to see the live interface. Key sections include:*

```
┌─────────────────────────────────────────────────────────────┐
│  Scheduler: [FCFS ▼]   Quantum: [2]   Processes: [5] [Set]  │
│  📝 Load Test Case:[Round Robin ▼] [Run Live] [Run Instant]│
├─────────────────────────────────────────────────────────────┤
│  Process Input                                              │
│  PID    Arrival Time    Burst Time    Priority              │
│  P1     0               8             -                     │
│  P2     1               4             -                     │
│  ...                                                        │
├─────────────────────────────────────────────────────────────┤
│  [▶ Start Live] [⚡ Run Instantly] [⏹ Stop] [➕ Add] [🔄] │
├─────────────────────────────────────────────────────────────┤
│  Gantt Chart (Live Timeline)                                │
│  ┃ P1 ┃ P1 ┃ P2 ┃ P3 ┃ P2 ┃ P1 ┃ P4 ┃ ──────────►           │
│  0    3    6    9   12   14   17   20                       │
├──────────────────────────────────┬──────────────────────────┤
│  Process Status (Live)           │  Statistics              │
│  PID Arr Bur Rem  Stat           │  Scheduler: Round Robin  │
│  P1  0   8   3   🔄 Running     │  ⏱ Current Time: 17      │
│  P2  1   4   0   ✅ Completed   │  Avg WT: 8.50             │
│  P3  2   6   2   ⏳ Ready       │  Avg TAT: 13.25           │
│  P4  5   3   3   🕐 Not Arrived │  Completed: 2 / 4         │
│                                  │  ● RUNNING               │
└──────────────────────────────────┴──────────────────────────┘
```

---

## 📂 Project Structure

```
CPU-Scheduler/
├── core/                       # Scheduling engine (backend)
│   ├── __init__.py             # Package exports
│   ├── process.py              # Process data model
│   ├── base_scheduler.py       # Abstract base class for all algorithms
│   ├── engine.py               # Simulation engine (drives schedulers)
│   ├── fcfs.py                 # First Come First Served
│   ├── sjf.py                  # Shortest Job First (preemptive & non-preemptive)
│   ├── priority.py             # Priority Scheduling (preemptive & non-preemptive)
│   └── roundroubin.py          # Round Robin with configurable quantum
│
├── ui/                         # GUI components (frontend)
│   ├── __init__.py             # Package marker
│   ├── app.py                  # Main application window & controller
│   ├── input_panel.py          # Dynamic process input form
│   ├── process_table.py        # Live process status table
│   ├── stats_panel.py          # Real-time statistics display
│   ├── gantt_chart.py          # Live scrollable Gantt chart
│   └── test_cases.py           # Built-in test scenarios
│
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.9+** — [Download here](https://www.python.org/downloads/)
- **Tkinter** — Usually included with Python

### Steps

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/CPU-Scheduler.git
cd CPU-Scheduler
```

**2. (Optional) Create a virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Verify Tkinter is available**

```bash
python -c "import tkinter; print('Tkinter OK')"
```

> If Tkinter is missing:
> ```bash
> # Ubuntu/Debian
> sudo apt-get install python3-tk
>
> # Fedora
> sudo dnf install python3-tkinter
>
> # macOS (Homebrew)
> brew install python-tk
> ```

**5. Run the application**

```bash
python main.py
```

---

## 📖 Usage

### Quick Start (Using Built-in Test Cases)

1. Launch the app with `python main.py`
2. In the **Load Test Case** dropdown, select an algorithm (e.g., `Round Robin`)
3. Click **ℹ Info** to read what the test demonstrates
4. Click **Load & Run Live** to watch it step-by-step, or **Load & Run Instant** for immediate results

### Manual Setup

1. **Select a scheduler** from the dropdown (e.g., `Priority (Preemptive)`)
2. **Enter the number of processes** and click **Set Up**
3. **Fill in process details** — Arrival Time, Burst Time, and Priority (if applicable)
4. Click **▶ Start Live** for real-time simulation or **⚡ Run Instantly** for immediate results
5. **Watch the Gantt chart** build in real-time and the process table update live

### Adding Processes Dynamically

1. While a **live simulation is running**, click **➕ Add Process**
2. A popup appears with Arrival Time pre-filled to the current simulation time
3. Enter Burst Time (and Priority if applicable), then click **✓ Add**
4. The new process is immediately injected into the running scheduler

### Controls

| Button | Action |
|--------|--------|
| **▶ Start Live** | Begin tick-by-tick simulation (1 sec = 1 time unit) |
| **⚡ Run Instantly** | Execute entire simulation at once |
| **⏹ Stop** | Halt the live simulation |
| **➕ Add Process** | Dynamically add a process during simulation |
| **🔄 Reset** | Clear everything and start fresh |

---

## 🧪 Built-in Test Cases

Each test case is carefully designed to showcase specific algorithm behaviors:

| Algorithm | Test Name | What It Demonstrates |
|-----------|-----------|----------------------|
| **FCFS** | Convoy Effect | Short jobs stuck behind a long job (P1 burst=8) |
| **SJF (NP)** | Shortest Job First | CPU picks shortest burst when free, not by arrival |
| **SJF (P)** | SRTF Preemption | Running process preempted by shorter new arrival |
| **Priority (NP)** | Priority Selection | Lower number = higher priority, non-preemptive |
| **Priority (P)** | Priority Preemption | Higher priority arrival preempts current process |
| **Round Robin** | Fair Sharing (q=3) | Time slicing, multiple rounds for long jobs |

### Example: FCFS Test Case

```
Processes:
PID    Arrival    Burst
P1     0          8       ← Long job arrives first
P2     1          2       ← Short job waits behind P1
P3     2          3
P4     3          1       ← Very short, still waits
P5     4          4

Result: P2, P3, P4 all wait 7+ units due to convoy effect
```

---

## 🏗 Architecture

### Design Pattern

The application follows a clean **MVC-like separation**:

```
┌──────────────────────────────────────────────────┐
│                    UI Layer                      │
│  app.py (Controller)                             │
│  ├── input_panel.py    (View - Input)            │
│  ├── process_table.py  (View - Status)           │
│  ├── gantt_chart.py    (View - Timeline)         │
│  ├── stats_panel.py    (View - Metrics)          │
│  └── test_cases.py     (Data - Presets)          │
├──────────────────────────────────────────────────┤
│                   Core Layer                     │
│  engine.py (Simulation Driver)                   │
│  ├── base_scheduler.py (Abstract Interface)      │
│  ├── fcfs.py           (Algorithm)               │
│  ├── sjf.py            (Algorithm)               │
│  ├── priority.py       (Algorithm)               │
│  ├── roundroubin.py    (Algorithm)               │
│  └── process.py        (Data Model)              │
└──────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **`tkinter.after()` instead of threading** | Thread-safe GUI updates, no race conditions |
| **Tick-based simulation** | Each `tick()` advances exactly 1 time unit — clean, testable |
| **Abstract base class** | All schedulers implement `tick()` and `reset()` — easy to extend |
| **Gantt as `[{pid, time}]`** | Simple format, UI merges consecutive entries for display |
| **Separate core/ui packages** | Core logic is testable without GUI, UI is swappable |

---

## ⚙ How It Works

### Simulation Loop

```
1. User clicks "Start Live"
2. App creates a Scheduler and loads processes
3. Every 1 second, root.after() calls tick():
   a. Check for new arrivals at current_time
   b. Select next process based on algorithm rules
   c. Execute 1 time unit (decrement remaining_time)
   d. Record Gantt chart entry
   e. Check for completion
   f. Update all GUI components
4. Repeat until all processes are completed
```

### Process Lifecycle

```
  Created → Not Arrived → Ready → Running → Completed
              (waiting)    (in     (on CPU)   (done)
                          queue)
```

### Gantt Chart Format

```python
# Internal format (one entry per time unit):
[{"pid": "P1", "time": 0}, {"pid": "P1", "time": 1}, {"pid": "P2", "time": 2}]

# UI merges consecutive same-PID entries for display:
[(P1, 0, 2), (P2, 2, 3)]  →  |  P1  |P2|
                               0     2  3
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Commit** your changes: `git commit -m "Add my feature"`
4. **Push** to the branch: `git push origin feature/my-feature`
5. **Open** a Pull Request

### Ideas for Contributions

- [ ] Add **Multilevel Queue** scheduling
- [ ] Add **Multilevel Feedback Queue** scheduling
- [ ] Export results to **CSV/PDF**
- [ ] Add **dark/light theme toggle**
- [ ] Add **speed control slider** for live simulation
- [ ] Add **process arrival animation**
- [ ] Package as standalone **.exe** with PyInstaller

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.


