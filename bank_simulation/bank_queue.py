"""
Bank Queue module for Bank Queue Simulation.

This module implements the priority-based queue where customers wait for service.
"""

import heapq
from typing import Optional, List
from bank_simulation.customer import Customer, CustomerPriority


class BankQueue:
    """
    Priority-based queue for bank customers.
    
    Customers are ordered by:
    1. Priority level (VIP > ELDERLY > APPOINTMENT > REGULAR)
    2. Arrival time (FIFO within same priority)
    
    Attributes:
        max_size: Maximum queue capacity (None for unlimited)
    """
    
    def __init__(self, max_size: Optional[int] = None):
        """
        Initialize the bank queue.
        
        Args:
            max_size: Optional maximum queue size.
        """
        self._heap: List[Customer] = []
        self.max_size = max_size
        self._total_customers_entered: int = 0
        self._total_customers_abandoned: int = 0
    
    def add_customer(self, customer: Customer) -> bool:
        """
        Add a customer to the queue.
        
        Args:
            customer: The customer to add.
            
        Returns:
            True if customer was added, False if queue is full.
        """
        if self.max_size is not None and len(self._heap) >= self.max_size:
            return False
        
        heapq.heappush(self._heap, customer)
        self._total_customers_entered += 1
        return True
    
    def get_next_customer(self) -> Optional[Customer]:
        """
        Remove and return the next customer to be served.
        
        Returns:
            The highest priority customer, or None if queue is empty.
        """
        if self._heap:
            return heapq.heappop(self._heap)
        return None
    
    def peek(self) -> Optional[Customer]:
        """
        Return the next customer without removing them.
        
        Returns:
            The highest priority customer, or None if queue is empty.
        """
        if self._heap:
            return self._heap[0]
        return None
    
    def remove_customer(self, customer: Customer) -> bool:
        """
        Remove a specific customer from the queue (e.g., for abandonment).
        
        Args:
            customer: The customer to remove.
            
        Returns:
            True if customer was found and removed.
        """
        try:
            self._heap.remove(customer)
            heapq.heapify(self._heap)
            return True
        except ValueError:
            return False
    
    def process_abandonments(self, current_time: float) -> List[Customer]:
        """
        Check and remove customers who have exceeded their patience.
        
        Args:
            current_time: The current simulation time.
            
        Returns:
            List of customers who abandoned the queue.
        """
        abandoned_customers = []
        remaining_customers = []
        
        for customer in self._heap:
            if customer.should_abandon(current_time):
                customer.abandoned = True
                abandoned_customers.append(customer)
                self._total_customers_abandoned += 1
            else:
                remaining_customers.append(customer)
        
        self._heap = remaining_customers
        heapq.heapify(self._heap)
        
        return abandoned_customers
    
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self._heap) == 0
    
    def is_full(self) -> bool:
        """Check if the queue is at capacity."""
        if self.max_size is None:
            return False
        return len(self._heap) >= self.max_size
    
    def get_queue_length(self) -> int:
        """Return the current queue length."""
        return len(self._heap)
    
    def get_customers_by_priority(self) -> dict:
        """
        Get count of customers in queue by priority level.
        
        Returns:
            Dictionary mapping priority levels to customer counts.
        """
        counts = {priority: 0 for priority in CustomerPriority}
        for customer in self._heap:
            counts[customer.priority] += 1
        return counts
    
    def get_abandonment_rate(self) -> float:
        """
        Calculate the abandonment rate.
        
        Returns:
            Proportion of customers who abandoned (0.0 to 1.0).
        """
        if self._total_customers_entered == 0:
            return 0.0
        return self._total_customers_abandoned / self._total_customers_entered
    
    def __len__(self) -> int:
        """Return the number of customers in the queue."""
        return len(self._heap)
