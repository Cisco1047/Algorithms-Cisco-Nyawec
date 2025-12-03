"""
Bank module for Bank Queue Simulation.

This module defines the Bank class that orchestrates customers, tellers, and the queue.
"""

from typing import List, Optional
from bank_simulation.customer import Customer
from bank_simulation.teller import Teller
from bank_simulation.bank_queue import BankQueue


class Bank:
    """
    Represents a bank with tellers and a customer queue.
    
    The bank coordinates customer arrivals, queue management, and teller assignments.
    
    Attributes:
        tellers: List of tellers serving customers
        queue: The customer waiting queue
        is_open: Whether the bank is currently open for business
    """
    
    def __init__(
        self,
        tellers: List[Teller],
        queue: Optional[BankQueue] = None
    ):
        """
        Initialize the bank.
        
        Args:
            tellers: List of tellers to staff the bank.
            queue: Optional custom queue (creates default if not provided).
        """
        self.tellers = tellers
        self.queue = queue if queue is not None else BankQueue()
        self.is_open = False
        self._total_customers_arrived = 0
        self._customers_turned_away = 0
    
    def open_bank(self, current_time: float):
        """Open the bank for business."""
        self.is_open = True
        for teller in self.tellers:
            teller.idle_since = current_time
    
    def close_bank(self):
        """Close the bank (no new customers accepted)."""
        self.is_open = False
    
    def customer_arrives(self, customer: Customer) -> bool:
        """
        Process a customer arrival.
        
        Args:
            customer: The arriving customer.
            
        Returns:
            True if customer joined the queue, False if turned away.
        """
        self._total_customers_arrived += 1
        
        if not self.is_open:
            self._customers_turned_away += 1
            return False
        
        if not self.queue.add_customer(customer):
            self._customers_turned_away += 1
            return False
        
        return True
    
    def get_available_teller(self) -> Optional[Teller]:
        """
        Find an available teller.
        
        Returns the teller who has been idle the longest to balance workload.
        
        Returns:
            An available teller, or None if all are busy.
        """
        available_tellers = [t for t in self.tellers if t.is_available()]
        
        if not available_tellers:
            return None
        
        # Return teller idle longest (for workload balancing)
        return min(
            available_tellers,
            key=lambda t: t.idle_since if t.idle_since is not None else float('inf')
        )
    
    def try_assign_customer_to_teller(self, current_time: float) -> Optional[tuple]:
        """
        Try to assign a waiting customer to an available teller.
        
        Args:
            current_time: The current simulation time.
            
        Returns:
            Tuple of (teller, customer, service_end_time) if assignment made,
            None if no assignment possible.
        """
        teller = self.get_available_teller()
        if teller is None:
            return None
        
        customer = self.queue.get_next_customer()
        if customer is None:
            return None
        
        service_end_time = teller.start_service(customer, current_time)
        return (teller, customer, service_end_time)
    
    def complete_service(self, teller: Teller, current_time: float) -> Customer:
        """
        Complete service for a teller's current customer.
        
        Args:
            teller: The teller completing service.
            current_time: The current simulation time.
            
        Returns:
            The customer who was served.
        """
        return teller.complete_service(current_time)
    
    def process_abandonments(self, current_time: float) -> List[Customer]:
        """
        Process customers who have abandoned the queue.
        
        Args:
            current_time: The current simulation time.
            
        Returns:
            List of customers who abandoned.
        """
        return self.queue.process_abandonments(current_time)
    
    def get_queue_length(self) -> int:
        """Get the current queue length."""
        return self.queue.get_queue_length()
    
    def has_waiting_customers(self) -> bool:
        """Check if there are customers waiting in the queue."""
        return not self.queue.is_empty()
    
    def has_customers_being_served(self) -> bool:
        """Check if any teller is currently serving a customer."""
        return any(not t.is_available() for t in self.tellers)
    
    def get_total_customers_arrived(self) -> int:
        """Get total number of customers who arrived."""
        return self._total_customers_arrived
    
    def get_customers_turned_away(self) -> int:
        """Get number of customers turned away (bank closed or queue full)."""
        return self._customers_turned_away
