"""
Teller module for Bank Queue Simulation.

This module defines tellers with varying efficiency levels.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from bank_simulation.customer import Customer


@dataclass
class Teller:
    """
    Represents a bank teller with variable efficiency.
    
    Attributes:
        teller_id: Unique identifier for the teller
        efficiency: Efficiency factor (1.0 = normal, >1.0 = faster, <1.0 = slower)
        current_customer: Customer currently being served (None if idle)
        customers_served: List of customers served by this teller
        total_busy_time: Total time spent serving customers
        idle_since: Time when the teller became idle (None if busy)
    """
    teller_id: int
    efficiency: float = 1.0
    current_customer: Optional[Customer] = None
    customers_served: List[Customer] = field(default_factory=list)
    total_busy_time: float = 0.0
    idle_since: Optional[float] = 0.0
    
    def is_available(self) -> bool:
        """Check if the teller is available to serve a customer."""
        return self.current_customer is None
    
    def calculate_service_time(self, customer: Customer) -> float:
        """
        Calculate actual service time based on teller efficiency.
        
        Args:
            customer: The customer to be served.
            
        Returns:
            Actual service time adjusted for teller efficiency.
        """
        return customer.service_time_required / self.efficiency
    
    def start_service(self, customer: Customer, current_time: float) -> float:
        """
        Start serving a customer.
        
        Args:
            customer: The customer to serve.
            current_time: The current simulation time.
            
        Returns:
            The time when service will be completed.
        """
        if not self.is_available():
            raise ValueError(f"Teller {self.teller_id} is not available")
        
        self.current_customer = customer
        customer.service_start_time = current_time
        service_duration = self.calculate_service_time(customer)
        
        # Track idle time that just ended
        if self.idle_since is not None:
            self.idle_since = None
            
        return current_time + service_duration
    
    def complete_service(self, current_time: float) -> Customer:
        """
        Complete serving the current customer.
        
        Args:
            current_time: The current simulation time.
            
        Returns:
            The customer who was being served.
        """
        if self.current_customer is None:
            raise ValueError(f"Teller {self.teller_id} has no customer to complete")
        
        customer = self.current_customer
        customer.service_end_time = current_time
        
        # Update statistics
        service_time = current_time - customer.service_start_time
        self.total_busy_time += service_time
        self.customers_served.append(customer)
        
        # Mark teller as idle
        self.current_customer = None
        self.idle_since = current_time
        
        return customer
    
    def get_utilization(self, total_time: float) -> float:
        """
        Calculate teller utilization as percentage of time spent serving.
        
        Args:
            total_time: Total simulation time.
            
        Returns:
            Utilization percentage (0.0 to 1.0).
        """
        if total_time <= 0:
            return 0.0
        return min(1.0, self.total_busy_time / total_time)
