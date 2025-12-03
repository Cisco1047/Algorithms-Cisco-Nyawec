"""
Customer module for Bank Queue Simulation.

This module defines customer types and priority levels for the bank queue simulation.
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Optional


class CustomerPriority(IntEnum):
    """
    Customer priority levels for queue ordering.
    
    Lower values indicate higher priority:
    - VIP (1): Highest priority customers
    - ELDERLY (2): Senior citizens with priority service
    - APPOINTMENT (3): Customers with scheduled appointments
    - REGULAR (4): Standard FIFO customers
    """
    VIP = 1
    ELDERLY = 2
    APPOINTMENT = 3
    REGULAR = 4


@dataclass
class Customer:
    """
    Represents a customer in the bank queue system.
    
    Attributes:
        customer_id: Unique identifier for the customer
        arrival_time: Time when the customer arrived at the bank
        priority: Priority level of the customer
        service_time_required: Estimated time needed to serve this customer
        patience: Maximum time the customer is willing to wait before abandoning
        service_start_time: Time when service began (None if not yet served)
        service_end_time: Time when service completed (None if not yet completed)
        abandoned: Whether the customer abandoned the queue
    """
    customer_id: int
    arrival_time: float
    priority: CustomerPriority = CustomerPriority.REGULAR
    service_time_required: float = 5.0
    patience: float = float('inf')
    service_start_time: Optional[float] = None
    service_end_time: Optional[float] = None
    abandoned: bool = False
    
    def get_wait_time(self) -> Optional[float]:
        """
        Calculate the time the customer waited before being served.
        
        Returns:
            Wait time in simulation time units, or None if not yet served.
        """
        if self.service_start_time is not None:
            return self.service_start_time - self.arrival_time
        return None
    
    def get_total_time(self) -> Optional[float]:
        """
        Calculate the total time the customer spent in the bank.
        
        Returns:
            Total time from arrival to service completion, or None if not completed.
        """
        if self.service_end_time is not None:
            return self.service_end_time - self.arrival_time
        return None
    
    def should_abandon(self, current_time: float) -> bool:
        """
        Check if the customer should abandon the queue based on their patience.
        
        Args:
            current_time: The current simulation time.
            
        Returns:
            True if the customer's wait time exceeds their patience.
        """
        if self.service_start_time is not None:
            return False  # Already being served
        wait_time = current_time - self.arrival_time
        return wait_time > self.patience
    
    def __lt__(self, other: 'Customer') -> bool:
        """
        Compare customers for priority queue ordering.
        
        Priority is determined first by priority level (lower is higher priority),
        then by arrival time (earlier arrivals first - FIFO within same priority).
        """
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.arrival_time < other.arrival_time
