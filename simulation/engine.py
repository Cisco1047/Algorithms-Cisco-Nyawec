"""
This module implements the core simulation engine for a discrete-event simulation.
"""
import heapq


class Event:
    def __init__(self, time, action):
        self.time = time
        self.action = action

    def __lt__(self, other):
        return self.time < other.time


class EventQueue:
    def __init__(self):
        self._heap = []

    def push(self, event):
        heapq.heappush(self._heap, event)

    def pop(self):
        return heapq.heappop(self._heap)

    def empty(self):
        return len(self._heap) == 0


class SimulationEngine:
    def __init__(self):
        self.current_time = 0
        self.events = EventQueue()

    def schedule(self, time, action):
        ev = Event(time, action)
        self.events.push(ev)

    def run(self, until_time=float('inf')):
        while not self.events.empty():
            event = self.events.pop()
            if event.time > until_time:
                break

            self.current_time = event.time
            event.action(self)
