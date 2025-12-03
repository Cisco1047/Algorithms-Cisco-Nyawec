"""
Simulator module for Bank Queue Simulation.

This module implements the discrete event simulation engine that drives the simulation.
"""

import random
from typing import Optional, Callable
from dataclasses import dataclass, field

from bank_simulation.customer import Customer, CustomerPriority
from bank_simulation.teller import Teller
from bank_simulation.bank_queue import BankQueue
from bank_simulation.bank import Bank
from bank_simulation.event import Event, EventType, EventQueue
from bank_simulation.statistics import SimulationStatistics


@dataclass
class SimulationConfig:
    """
    Configuration for the bank queue simulation.
    
    Attributes:
        num_tellers: Number of tellers in the bank
        teller_efficiencies: Efficiency of each teller (None for all 1.0)
        simulation_duration: Total simulation time
        mean_arrival_interval: Average time between customer arrivals
        mean_service_time: Average service time per customer
        service_time_variance: Variance in service time
        priority_distribution: Probability distribution for customer priorities
        mean_patience: Average customer patience (waiting tolerance)
        patience_variance: Variance in patience
        queue_capacity: Maximum queue size (None for unlimited)
        random_seed: Random seed for reproducibility
    """
    num_tellers: int = 3
    teller_efficiencies: Optional[list] = None
    simulation_duration: float = 480.0  # 8-hour day in minutes
    mean_arrival_interval: float = 2.0
    mean_service_time: float = 5.0
    service_time_variance: float = 2.0
    priority_distribution: dict = field(default_factory=lambda: {
        CustomerPriority.VIP: 0.05,
        CustomerPriority.ELDERLY: 0.15,
        CustomerPriority.APPOINTMENT: 0.10,
        CustomerPriority.REGULAR: 0.70,
    })
    mean_patience: float = 15.0
    patience_variance: float = 5.0
    queue_capacity: Optional[int] = None
    random_seed: Optional[int] = None


class Simulator:
    """
    Discrete Event Simulation engine for the bank queue.
    
    Implements the core simulation loop that processes events in chronological order.
    """
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        """
        Initialize the simulator.
        
        Args:
            config: Simulation configuration (uses defaults if not provided).
        """
        self.config = config if config is not None else SimulationConfig()
        self.event_queue = EventQueue()
        self.current_time = 0.0
        self.statistics = SimulationStatistics()
        self._customer_id_counter = 0
        
        # Set random seed for reproducibility
        if self.config.random_seed is not None:
            random.seed(self.config.random_seed)
        
        # Create tellers
        efficiencies = self.config.teller_efficiencies or [1.0] * self.config.num_tellers
        self.tellers = [
            Teller(teller_id=i, efficiency=efficiencies[i])
            for i in range(self.config.num_tellers)
        ]
        
        # Create bank
        queue = BankQueue(max_size=self.config.queue_capacity)
        self.bank = Bank(tellers=self.tellers, queue=queue)
        
        # Callbacks for custom event handling
        self._on_customer_arrival: Optional[Callable] = None
        self._on_service_complete: Optional[Callable] = None
        self._on_customer_abandon: Optional[Callable] = None
    
    def _generate_customer_id(self) -> int:
        """Generate a unique customer ID."""
        self._customer_id_counter += 1
        return self._customer_id_counter
    
    def _generate_priority(self) -> CustomerPriority:
        """Generate a random customer priority based on distribution."""
        r = random.random()
        cumulative = 0.0
        for priority, prob in self.config.priority_distribution.items():
            cumulative += prob
            if r < cumulative:
                return priority
        return CustomerPriority.REGULAR
    
    def _generate_service_time(self) -> float:
        """Generate random service time."""
        return max(1.0, random.gauss(
            self.config.mean_service_time,
            self.config.service_time_variance
        ))
    
    def _generate_patience(self) -> float:
        """Generate random patience level."""
        return max(1.0, random.gauss(
            self.config.mean_patience,
            self.config.patience_variance
        ))
    
    def _generate_arrival_interval(self) -> float:
        """Generate random inter-arrival time (exponential distribution)."""
        return random.expovariate(1.0 / self.config.mean_arrival_interval)
    
    def _schedule_next_arrival(self):
        """Schedule the next customer arrival."""
        next_arrival_time = self.current_time + self._generate_arrival_interval()
        if next_arrival_time < self.config.simulation_duration:
            self.event_queue.schedule(
                time=next_arrival_time,
                event_type=EventType.CUSTOMER_ARRIVAL
            )
    
    def _create_customer(self) -> Customer:
        """Create a new customer with random attributes."""
        return Customer(
            customer_id=self._generate_customer_id(),
            arrival_time=self.current_time,
            priority=self._generate_priority(),
            service_time_required=self._generate_service_time(),
            patience=self._generate_patience()
        )
    
    def _handle_customer_arrival(self, event: Event):
        """Handle a customer arrival event."""
        customer = self._create_customer()
        
        # Try to add customer to queue
        if self.bank.customer_arrives(customer):
            # Record queue length
            self.statistics.record_queue_length(
                self.current_time,
                self.bank.get_queue_length()
            )
            
            # Try to assign to available teller
            self._try_start_service()
        
        if self._on_customer_arrival:
            self._on_customer_arrival(customer)
        
        # Schedule next arrival
        self._schedule_next_arrival()
    
    def _try_start_service(self):
        """Try to start service for waiting customers."""
        while True:
            assignment = self.bank.try_assign_customer_to_teller(self.current_time)
            if assignment is None:
                break
            
            teller, customer, service_end_time = assignment
            
            # Schedule service completion
            self.event_queue.schedule(
                time=service_end_time,
                event_type=EventType.SERVICE_COMPLETE,
                data={'teller_id': teller.teller_id}
            )
            
            # Update queue length statistics
            self.statistics.record_queue_length(
                self.current_time,
                self.bank.get_queue_length()
            )
    
    def _handle_service_complete(self, event: Event):
        """Handle a service completion event."""
        teller_id = event.data['teller_id']
        teller = self.tellers[teller_id]
        
        # Complete service for current customer
        customer = self.bank.complete_service(teller, self.current_time)
        self.statistics.record_served_customer(customer)
        
        if self._on_service_complete:
            self._on_service_complete(teller, customer)
        
        # Try to serve next customer
        self._try_start_service()
    
    def _handle_abandonment_check(self):
        """Check for and process customer abandonments."""
        abandoned = self.bank.process_abandonments(self.current_time)
        for customer in abandoned:
            self.statistics.record_abandoned_customer(customer)
            if self._on_customer_abandon:
                self._on_customer_abandon(customer)
        
        if abandoned:
            self.statistics.record_queue_length(
                self.current_time,
                self.bank.get_queue_length()
            )
    
    def initialize(self):
        """Initialize the simulation."""
        self.current_time = 0.0
        self.event_queue = EventQueue()
        self.statistics = SimulationStatistics()
        self._customer_id_counter = 0
        
        # Open the bank
        self.bank.open_bank(self.current_time)
        
        # Schedule first customer arrival
        self._schedule_next_arrival()
        
        # Schedule bank closing
        self.event_queue.schedule(
            time=self.config.simulation_duration,
            event_type=EventType.BANK_CLOSE
        )
    
    def run(self, verbose: bool = False) -> SimulationStatistics:
        """
        Run the complete simulation.
        
        Args:
            verbose: Whether to print progress information.
            
        Returns:
            Simulation statistics.
        """
        self.initialize()
        
        if verbose:
            print(f"Starting simulation with {self.config.num_tellers} tellers")
            print(f"Simulation duration: {self.config.simulation_duration} time units")
            print()
        
        # Main simulation loop
        while not self.event_queue.is_empty():
            event = self.event_queue.pop()
            self.current_time = event.time
            
            # Check for abandonments periodically
            self._handle_abandonment_check()
            
            if event.event_type == EventType.CUSTOMER_ARRIVAL:
                self._handle_customer_arrival(event)
                
            elif event.event_type == EventType.SERVICE_COMPLETE:
                self._handle_service_complete(event)
                
            elif event.event_type == EventType.BANK_CLOSE:
                self.bank.close_bank()
                if verbose:
                    print(f"Bank closed at time {self.current_time}")
                # Continue processing remaining customers
        
        # Final queue length recording
        self.statistics.record_queue_length(
            self.current_time,
            self.bank.get_queue_length()
        )
        
        if verbose:
            print()
            print(self.statistics.generate_report(self.tellers, self.current_time))
        
        return self.statistics
    
    def step(self) -> Optional[Event]:
        """
        Execute a single simulation step (process one event).
        
        Returns:
            The processed event, or None if simulation is complete.
        """
        if self.event_queue.is_empty():
            return None
        
        event = self.event_queue.pop()
        self.current_time = event.time
        
        self._handle_abandonment_check()
        
        if event.event_type == EventType.CUSTOMER_ARRIVAL:
            self._handle_customer_arrival(event)
        elif event.event_type == EventType.SERVICE_COMPLETE:
            self._handle_service_complete(event)
        elif event.event_type == EventType.BANK_CLOSE:
            self.bank.close_bank()
        
        return event
    
    def on_customer_arrival(self, callback: Callable):
        """Register a callback for customer arrival events."""
        self._on_customer_arrival = callback
    
    def on_service_complete(self, callback: Callable):
        """Register a callback for service completion events."""
        self._on_service_complete = callback
    
    def on_customer_abandon(self, callback: Callable):
        """Register a callback for customer abandonment events."""
        self._on_customer_abandon = callback
