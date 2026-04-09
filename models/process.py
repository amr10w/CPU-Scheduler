class Process:
    def __init__(self, name, arrival_time, burst_time):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.finish_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0



def calc_turnaround_time(processes):
    for p in processes:
        p.turnaround_time=p.finish_time - p.arrival_time


def calc_waiting_time(processes):
    for p in processes:
        p.waiting_time=p.turnaround_time - p.burst_time


