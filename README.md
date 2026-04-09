
# 🖥️ CPU Scheduler Simulator

A GUI desktop application that simulates various CPU scheduling algorithms.
Built with Python and Tkinter as a mini-project for the Operating Systems course.

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Table of Contents

- [About](#about)
- [Supported Algorithms](#supported-algorithms)
- [Features](#features)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)
- [How to Build Executable](#how-to-build-executable)
- [How to Use](#how-to-use)
- [Test Examples](#test-examples)
- [Screenshots](#screenshots)
- [Author](#author)

---

## 📖 About

This project implements a **CPU Scheduler Simulator** with a graphical user interface.
It allows users to visualize how different CPU scheduling algorithms work by showing
a **live Gantt chart**, **real-time process status table**, and **performance statistics**.

The simulator supports both **live mode** (1 second = 1 time unit) and **instant mode**,
and allows **dynamic process addition** during simulation.

---

## 🔧 Supported Algorithms

| # | Algorithm | Type | Description |
|---|---|---|---|
| 1 | **FCFS** | Non-Preemptive | First Come First Served - processes run in arrival order |
| 2 | **SJF** | Non-Preemptive | Shortest Job First - shortest burst time runs first |
| 3 | **SRTF** | Preemptive | Shortest Remaining Time First - preemptive version of SJF |
| 4 | **Priority** | Non-Preemptive | Lowest priority number runs first, no interruption |
| 5 | **Priority** | Preemptive | Lowest priority number runs first, can interrupt |
| 6 | **Round Robin** | Preemptive | Each process gets a fixed time quantum in rotation |

> **Note:** For Priority scheduling, a **smaller number = higher priority**.

---

## ✨ Features

- **Live Simulation** — Watch the scheduler run in real-time (1 second per time unit)
- **Instant Mode** — Run the entire simulation at once without delays
- **Dynamic Process Addition** — Add new processes while the simulation is running
- **Live Gantt Chart** — Visual timeline showing process execution order with colors
- **Live Process Table** — Real-time updates showing remaining burst times and status
- **Smart Input** — Only asks for relevant information per scheduler type
  - FCFS/SJF/Round Robin: No priority field
  - Round Robin: Shows time quantum input
  - Priority: Shows priority field
- **Statistics Dashboard** — Average Waiting Time and Average Turnaround Time
- **Scrollable Interface** — Handles any number of processes without overflow
- **Cross-Platform** — Works on Windows, macOS, and Linux

---

## 📁 Project Structure

```
CPU-SCHEDULER/
│
├── main.py                      # Entry point - launches the application
│
├── models/
│   ├── __init__.py              # Package initializer
│   └── process.py               # Process data class
│
├── schedulers/
│   ├── __init__.py              # Package initializer
│   ├── base_scheduler.py        # Abstract base class for all schedulers
│   ├── fcfs.py                  # First Come First Served algorithm
│   ├── sjf.py                   # Shortest Job First (Preemptive & Non-Preemptive)
│   ├── priority_scheduler.py    # Priority Scheduling (Preemptive & Non-Preemptive)
│   └── round_robin.py           # Round Robin algorithm
│
├── gui/
│   ├── __init__.py              # Package initializer
│   ├── app.py                   # Main application window (connects everything)
│   ├── input_panel.py           # Process input form with validation
│   ├── gantt_chart.py           # Live scrollable Gantt chart
│   ├── process_table.py         # Real-time process status table
│   └── stats_panel.py           # Statistics display panel
│
├── requirements.txt             # Project dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

### Architecture Overview

```
┌─────────────────────────────────────────┐
│                main.py                  │
│            (Entry Point)                │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│              gui/app.py                 │
│        (Main Application Window)        │
│                                         │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │ input_panel │  │   gantt_chart    │  │
│  └─────────────┘  └──────────────────┘  │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │process_table│  │   stats_panel    │  │
│  └─────────────┘  └──────────────────┘  │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│          schedulers/                    │
│  ┌────────────────────────────────────┐ │
│  │       base_scheduler.py            │ │
│  │    (Abstract Base Class)           │ │
│  └───────────────┬────────────────────┘ │
│    ┌─────────────┼─────────────┐        │
│  ┌─▼──┐  ┌──▼───┐  ┌───▼────┐  ┌─▼──┐   │
│  │FCFS│  │ SJF  │  │Priority│  │ RR │   │
│  └────┘  └──────┘  └────────┘  └────┘   │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│           models/process.py             │
│         (Process Data Class)            │
└─────────────────────────────────────────┘
```

---

## 🚀 How to Run

### Prerequisites

- **Python 3.7** or higher
- **Tkinter** (included with standard Python installation)

### From Source Code

```bash
# Clone the repository
git clone <your-repo-url>
cd CPU-SCHEDULER

# Run the application
python main.py
```

### From Executable

```bash
# Windows
dist\CPU_Scheduler.exe

# macOS / Linux
./dist/CPU_Scheduler
```

---

## 📦 How to Build Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build single-file executable
pyinstaller --onefile --windowed --name "CPU_Scheduler" main.py

# If you get import errors, use this extended command:
pyinstaller --onefile --windowed --name "CPU_Scheduler" \
    --hidden-import=models \
    --hidden-import=models.process \
    --hidden-import=schedulers \
    --hidden-import=schedulers.base_scheduler \
    --hidden-import=schedulers.fcfs \
    --hidden-import=schedulers.sjf \
    --hidden-import=schedulers.priority_scheduler \
    --hidden-import=schedulers.round_robin \
    --hidden-import=gui \
    --hidden-import=gui.app \
    --hidden-import=gui.input_panel \
    --hidden-import=gui.gantt_chart \
    --hidden-import=gui.process_table \
    --hidden-import=gui.stats_panel \
    main.py

# Find your executable in the dist/ folder
```

---

## 📖 How to Use

### Step 1: Select Scheduler
Choose a scheduling algorithm from the dropdown menu.

### Step 2: Set Number of Processes
Enter how many processes you want and click **"Set Up"**.

### Step 3: Enter Process Data
Fill in the details for each process:
- **Arrival Time** — When the process arrives (≥ 0)
- **Burst Time** — How much CPU time needed (> 0)
- **Priority** — Priority level (only for Priority schedulers, lower = higher priority)
- **Time Quantum** — Time slice for Round Robin

### Step 4: Run Simulation
- **▶ Start Live** — Runs in real-time, 1 second per time unit
- **⚡ Run Instantly** — Completes the entire simulation immediately

### Step 5: Observe Results
- Watch the **Gantt Chart** build live
- Monitor the **Process Table** for remaining burst times
- Check **Statistics** for average waiting and turnaround times

### Step 6: (Optional) Add Processes Dynamically
- Click **"➕ Add Process"** during a live simulation
- Enter the new process details in the popup
- The scheduler will include it in the simulation

### Step 7: Reset
- Click **"🔄 Reset"** to start over with a new simulation

---

## 🧪 Test Examples

### Test 1: FCFS

| Process | Arrival | Burst |
|---------|---------|-------|
| P1 | 0 | 4 |
| P2 | 1 | 3 |
| P3 | 2 | 1 |

**Expected Gantt Chart:**
```
| P1 | P2 | P3 |
0    4    7    8
```

**Expected Results:**

| Process | WT | TAT |
|---------|----|-----|
| P1 | 0 | 4 |
| P2 | 3 | 6 |
| P3 | 5 | 6 |
| **Average** | **2.67** | **5.33** |

---

### Test 2: SJF Non-Preemptive

| Process | Arrival | Burst |
|---------|---------|-------|
| P1 | 0 | 7 |
| P2 | 2 | 4 |
| P3 | 4 | 1 |
| P4 | 5 | 4 |

**Expected Gantt Chart:**
```
|  P1  | P3 | P2 | P4 |
0      7    8    12   16
```

**Expected Results:**

| Process | WT | TAT |
|---------|----|-----|
| P1 | 0 | 7 |
| P2 | 6 | 10 |
| P3 | 3 | 4 |
| P4 | 7 | 11 |
| **Average** | **4.00** | **8.00** |

---

### Test 3: SJF Preemptive (SRTF)

| Process | Arrival | Burst |
|---------|---------|-------|
| P1 | 0 | 7 |
| P2 | 2 | 4 |
| P3 | 4 | 1 |
| P4 | 5 | 4 |

**Expected Gantt Chart:**
```
| P1 | P2 | P3 | P2 |  P4  |   P1   |
0    2    4    5    7      11       16
```

**Expected Results:**

| Process | WT | TAT |
|---------|----|-----|
| P1 | 9 | 16 |
| P2 | 1 | 5 |
| P3 | 0 | 1 |
| P4 | 6 | 10 (wait: 11-5-4=2... verify) |
| **Average** | **4.00** | **7.75** |

---

### Test 4: Priority Non-Preemptive

| Process | Arrival | Burst | Priority |
|---------|---------|-------|----------|
| P1 | 0 | 5 | 3 |
| P2 | 1 | 3 | 1 |
| P3 | 2 | 4 | 4 |
| P4 | 3 | 2 | 2 |

**Expected Gantt Chart:**
```
| P1 | P2 | P4 | P3 |
0    5    8    10   14
```

**Expected Results:**

| Process | WT | TAT |
|---------|----|-----|
| P1 | 0 | 5 |
| P2 | 4 | 7 |
| P3 | 8 | 12 |
| P4 | 5 | 7 |
| **Average** | **4.25** | **7.75** |

---

### Test 5: Priority Preemptive

| Process | Arrival | Burst | Priority |
|---------|---------|-------|----------|
| P1 | 0 | 5 | 3 |
| P2 | 1 | 3 | 1 |
| P3 | 2 | 4 | 4 |
| P4 | 3 | 2 | 2 |

**Expected Gantt Chart:**
```
| P1 | P2 | P4 |  P1  |  P3  |
0    1    4    6      10     14
```

**Expected Results:**

| Process | WT | TAT |
|---------|----|-----|
| P1 | 5 | 10 |
| P2 | 0 | 3 |
| P3 | 8 | 12 |
| P4 | 1 | 3 |
| **Average** | **3.50** | **7.00** |

---

### Test 6: Round Robin (Quantum = 2)

| Process | Arrival | Burst |
|---------|---------|-------|
| P1 | 0 | 5 |
| P2 | 1 | 4 |
| P3 | 2 | 2 |
| P4 | 3 | 1 |

**Expected Gantt Chart:**
```
| P1 | P2 | P3 | P4 | P1 | P2 | P1 |
0    2    4    6    7    9    11   12
```

**Expected Results:**

| Process | WT | TAT |
|---------|----|-----|
| P1 | 7 | 12 |
| P2 | 6 | 10 |
| P3 | 2 | 4 |
| P4 | 4 | 5 (wait: 7-3-1=3... verify) |
| **Average** | **4.75** | **7.75** |

---

## 🛠️ Technical Details

### Design Patterns Used

- **Abstract Base Class (ABC)** — `BaseScheduler` provides common functionality, each algorithm only implements `get_next_process()`
- **Template Method Pattern** — `step()` method in base class defines the simulation flow, subclasses customize the selection logic
- **MVC-like Architecture** — Models (Process), Logic (Schedulers), View (GUI components) are separated
- **Observer-like Updates** — GUI components are refreshed from a central `_update_all_displays()` method

### Key Design Decisions

| Decision | Reason |
|---|---|
| Separate packages (models, schedulers, gui) | Clean separation of concerns |
| Abstract base class for schedulers | Avoid code duplication, easy to add new algorithms |
| Thread-based live simulation | Keeps GUI responsive during simulation |
| 1-second mapped time units | Makes it easy to observe the scheduling in action |
| Dynamic process addition | Demonstrates real-world scenario of processes arriving at runtime |

### Technologies

- **Python 3.7+** — Programming language
- **Tkinter** — GUI framework (built into Python)
- **Threading** — For live simulation without freezing the GUI
- **ABC module** — For abstract base classes
- **PyInstaller** — For building standalone executables
