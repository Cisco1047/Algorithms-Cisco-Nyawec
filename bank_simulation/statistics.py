"""
Statistics module for Bank Queue Simulation.

This module provides comprehensive statistics tracking for the simulation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from bank_simulation.customer import Customer, CustomerPriority
from bank_simulation.teller import Teller


@dataclass
class SimulationStatistics:
    """
    Tracks and computes statistics for the bank queue simulation.
    
    Collects data on:
    - Customer wait times
    - Service times
    - Teller utilization
    - Abandonment rates
    - Queue lengths over time
    """
    
    served_customers: List[Customer] = field(default_factory=list)
    abandoned_customers: List[Customer] = field(default_factory=list)
    queue_length_samples: List[tuple] = field(default_factory=list)  # (time, length)
    
    def record_served_customer(self, customer: Customer):
        """Record a customer who completed service."""
        self.served_customers.append(customer)
    
    def record_abandoned_customer(self, customer: Customer):
        """Record a customer who abandoned the queue."""
        self.abandoned_customers.append(customer)
    
    def record_queue_length(self, time: float, length: int):
        """Record queue length at a specific time."""
        self.queue_length_samples.append((time, length))
    
    # Wait time statistics
    
    def get_average_wait_time(self) -> float:
        """Calculate average wait time across all served customers."""
        wait_times = [c.get_wait_time() for c in self.served_customers if c.get_wait_time() is not None]
        return sum(wait_times) / len(wait_times) if wait_times else 0.0
    
    def get_max_wait_time(self) -> float:
        """Get the maximum wait time experienced by any customer."""
        wait_times = [c.get_wait_time() for c in self.served_customers if c.get_wait_time() is not None]
        return max(wait_times) if wait_times else 0.0
    
    def get_min_wait_time(self) -> float:
        """Get the minimum wait time experienced by any customer."""
        wait_times = [c.get_wait_time() for c in self.served_customers if c.get_wait_time() is not None]
        return min(wait_times) if wait_times else 0.0
    
    def get_wait_time_by_priority(self) -> Dict[CustomerPriority, float]:
        """Calculate average wait time for each priority level."""
        wait_times_by_priority: Dict[CustomerPriority, List[float]] = {
            priority: [] for priority in CustomerPriority
        }
        
        for customer in self.served_customers:
            wait_time = customer.get_wait_time()
            if wait_time is not None:
                wait_times_by_priority[customer.priority].append(wait_time)
        
        return {
            priority: (sum(times) / len(times) if times else 0.0)
            for priority, times in wait_times_by_priority.items()
        }
    
    # Service time statistics
    
    def get_average_service_time(self) -> float:
        """Calculate average service time across all served customers."""
        service_times = [
            c.service_end_time - c.service_start_time
            for c in self.served_customers
            if c.service_start_time is not None and c.service_end_time is not None
        ]
        return sum(service_times) / len(service_times) if service_times else 0.0
    
    def get_average_total_time(self) -> float:
        """Calculate average total time (wait + service) for served customers."""
        total_times = [c.get_total_time() for c in self.served_customers if c.get_total_time() is not None]
        return sum(total_times) / len(total_times) if total_times else 0.0
    
    # Customer statistics
    
    def get_total_customers_served(self) -> int:
        """Get total number of customers who completed service."""
        return len(self.served_customers)
    
    def get_total_customers_abandoned(self) -> int:
        """Get total number of customers who abandoned."""
        return len(self.abandoned_customers)
    
    def get_abandonment_rate(self) -> float:
        """Calculate the abandonment rate."""
        total = len(self.served_customers) + len(self.abandoned_customers)
        return len(self.abandoned_customers) / total if total > 0 else 0.0
    
    def get_customers_served_by_priority(self) -> Dict[CustomerPriority, int]:
        """Get count of served customers by priority level."""
        counts = {priority: 0 for priority in CustomerPriority}
        for customer in self.served_customers:
            counts[customer.priority] += 1
        return counts
    
    # Queue statistics
    
    def get_average_queue_length(self) -> float:
        """Calculate time-weighted average queue length."""
        if not self.queue_length_samples:
            return 0.0
        
        # Time-weighted average
        total_weighted_length = 0.0
        total_time = 0.0
        
        for i in range(len(self.queue_length_samples) - 1):
            time1, length = self.queue_length_samples[i]
            time2, _ = self.queue_length_samples[i + 1]
            duration = time2 - time1
            total_weighted_length += length * duration
            total_time += duration
        
        return total_weighted_length / total_time if total_time > 0 else 0.0
    
    def get_max_queue_length(self) -> int:
        """Get the maximum queue length observed."""
        if not self.queue_length_samples:
            return 0
        return max(length for _, length in self.queue_length_samples)
    
    # Teller statistics
    
    def get_teller_utilizations(self, tellers: List[Teller], total_time: float) -> Dict[int, float]:
        """Calculate utilization for each teller."""
        return {
            teller.teller_id: teller.get_utilization(total_time)
            for teller in tellers
        }
    
    def get_average_teller_utilization(self, tellers: List[Teller], total_time: float) -> float:
        """Calculate average utilization across all tellers."""
        utilizations = [teller.get_utilization(total_time) for teller in tellers]
        return sum(utilizations) / len(utilizations) if utilizations else 0.0
    
    def get_customers_per_teller(self, tellers: List[Teller]) -> Dict[int, int]:
        """Get count of customers served by each teller."""
        return {
            teller.teller_id: len(teller.customers_served)
            for teller in tellers
        }
    
    # Summary report
    
    def generate_report(self, tellers: List[Teller], total_time: float) -> str:
        """
        Generate a comprehensive statistics report.
        
        Args:
            tellers: List of tellers in the simulation.
            total_time: Total simulation time.
            
        Returns:
            Formatted report string.
        """
        lines = [
            "=" * 60,
            "BANK QUEUE SIMULATION - STATISTICS REPORT",
            "=" * 60,
            "",
            "CUSTOMER STATISTICS",
            "-" * 40,
            f"  Total customers served:     {self.get_total_customers_served()}",
            f"  Total customers abandoned:  {self.get_total_customers_abandoned()}",
            f"  Abandonment rate:           {self.get_abandonment_rate():.2%}",
            "",
            "  Customers served by priority:",
        ]
        
        for priority, count in self.get_customers_served_by_priority().items():
            lines.append(f"    {priority.name}: {count}")
        
        lines.extend([
            "",
            "WAIT TIME STATISTICS",
            "-" * 40,
            f"  Average wait time:  {self.get_average_wait_time():.2f} time units",
            f"  Maximum wait time:  {self.get_max_wait_time():.2f} time units",
            f"  Minimum wait time:  {self.get_min_wait_time():.2f} time units",
            "",
            "  Average wait time by priority:",
        ])
        
        for priority, avg_wait in self.get_wait_time_by_priority().items():
            lines.append(f"    {priority.name}: {avg_wait:.2f} time units")
        
        lines.extend([
            "",
            "SERVICE STATISTICS",
            "-" * 40,
            f"  Average service time:    {self.get_average_service_time():.2f} time units",
            f"  Average total time:      {self.get_average_total_time():.2f} time units",
            "",
            "QUEUE STATISTICS",
            "-" * 40,
            f"  Average queue length:  {self.get_average_queue_length():.2f}",
            f"  Maximum queue length:  {self.get_max_queue_length()}",
            "",
            "TELLER STATISTICS",
            "-" * 40,
            f"  Number of tellers:           {len(tellers)}",
            f"  Average teller utilization:  {self.get_average_teller_utilization(tellers, total_time):.2%}",
            "",
            "  Individual teller statistics:",
        ])
        
        utilizations = self.get_teller_utilizations(tellers, total_time)
        customers_per_teller = self.get_customers_per_teller(tellers)
        
        for teller in tellers:
            lines.append(
                f"    Teller {teller.teller_id} (efficiency {teller.efficiency:.1f}x): "
                f"utilization {utilizations[teller.teller_id]:.2%}, "
                f"{customers_per_teller[teller.teller_id]} customers served"
            )
        
        lines.extend([
            "",
            "=" * 60,
        ])
        
        return "\n".join(lines)
