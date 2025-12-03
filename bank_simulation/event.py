"""
Event module for Bank Queue Simulation.

This module defines the discrete event system components including
event types, events, and the priority-based event queue.
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, Optional
import heapq


class EventType(Enum):
    """
    Types of events in the bank queue simulation.
    """
    CUSTOMER_ARRIVAL = auto()      # A new customer arrives at the bank
    SERVICE_START = auto()         # A teller starts serving a customer
    SERVICE_COMPLETE = auto()      # A teller finishes serving a customer
    CUSTOMER_ABANDON = auto()      # A customer abandons the queue
    BANK_OPEN = auto()             # The bank opens
    BANK_CLOSE = auto()            # The bank closes


@dataclass(order=True)
class Event:
    """
    Represents a discrete event in the simulation.
    
    Events are ordered by time, then by a sequence number for deterministic ordering
    of simultaneous events.
    
    Attributes:
        time: The simulation time when the event occurs
        sequence: Sequence number for ordering simultaneous events
        event_type: The type of event
        data: Additional event-specific data
    """
    time: float
    sequence: int = field(compare=True)
    event_type: EventType = field(compare=False)
    data: Any = field(default=None, compare=False)


class EventQueue:
    """
    Priority queue for managing simulation events.
    
    Events are processed in chronological order, with ties broken by sequence number.
    """
    
    def __init__(self):
        """Initialize an empty event queue."""
        self._heap: list[Event] = []
        self._sequence: int = 0
    
    def schedule(self, time: float, event_type: EventType, data: Any = None) -> Event:
        """
        Schedule a new event.
        
        Args:
            time: The simulation time when the event should occur.
            event_type: The type of event.
            data: Optional event-specific data.
            
        Returns:
            The scheduled event.
        """
        event = Event(time=time, sequence=self._sequence, event_type=event_type, data=data)
        self._sequence += 1
        heapq.heappush(self._heap, event)
        return event
    
    def pop(self) -> Optional[Event]:
        """
        Remove and return the next event to process.
        
        Returns:
            The next event, or None if the queue is empty.
        """
        if self._heap:
            return heapq.heappop(self._heap)
        return None
    
    def peek(self) -> Optional[Event]:
        """
        Return the next event without removing it.
        
        Returns:
            The next event, or None if the queue is empty.
        """
        if self._heap:
            return self._heap[0]
        return None
    
    def is_empty(self) -> bool:
        """Check if the event queue is empty."""
        return len(self._heap) == 0
    
    def __len__(self) -> int:
        """Return the number of events in the queue."""
        return len(self._heap)
