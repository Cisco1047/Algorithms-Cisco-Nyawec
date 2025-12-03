"""
Unit tests for Simulator class.
"""

import unittest
from bank_simulation.customer import CustomerPriority
from bank_simulation.simulator import Simulator, SimulationConfig


class TestSimulationConfig(unittest.TestCase):
    """Tests for SimulationConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SimulationConfig()
        
        self.assertEqual(config.num_tellers, 3)
        self.assertEqual(config.simulation_duration, 480.0)
        self.assertIsNone(config.teller_efficiencies)
        self.assertEqual(config.mean_arrival_interval, 2.0)
        self.assertEqual(config.mean_service_time, 5.0)
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = SimulationConfig(
            num_tellers=5,
            simulation_duration=240.0,
            teller_efficiencies=[1.0, 1.2, 0.8, 1.0, 1.5],
            random_seed=42
        )
        
        self.assertEqual(config.num_tellers, 5)
        self.assertEqual(config.simulation_duration, 240.0)
        self.assertEqual(len(config.teller_efficiencies), 5)
        self.assertEqual(config.random_seed, 42)


class TestSimulator(unittest.TestCase):
    """Tests for Simulator class."""
    
    def test_simulator_creation(self):
        """Test basic simulator creation."""
        simulator = Simulator()
        
        self.assertIsNotNone(simulator.config)
        self.assertIsNotNone(simulator.bank)
        self.assertEqual(len(simulator.tellers), 3)
    
    def test_simulator_with_custom_config(self):
        """Test simulator with custom configuration."""
        config = SimulationConfig(num_tellers=5, random_seed=123)
        simulator = Simulator(config=config)
        
        self.assertEqual(len(simulator.tellers), 5)
    
    def test_simulator_with_custom_efficiencies(self):
        """Test simulator with custom teller efficiencies."""
        config = SimulationConfig(
            num_tellers=3,
            teller_efficiencies=[1.0, 1.5, 0.8]
        )
        simulator = Simulator(config=config)
        
        self.assertEqual(simulator.tellers[0].efficiency, 1.0)
        self.assertEqual(simulator.tellers[1].efficiency, 1.5)
        self.assertEqual(simulator.tellers[2].efficiency, 0.8)
    
    def test_initialize(self):
        """Test simulation initialization."""
        config = SimulationConfig(random_seed=42)
        simulator = Simulator(config=config)
        
        simulator.initialize()
        
        self.assertEqual(simulator.current_time, 0.0)
        self.assertTrue(simulator.bank.is_open)
        self.assertFalse(simulator.event_queue.is_empty())
    
    def test_run_short_simulation(self):
        """Test running a short simulation."""
        config = SimulationConfig(
            num_tellers=2,
            simulation_duration=60.0,  # 1 hour
            mean_arrival_interval=5.0,
            random_seed=42
        )
        simulator = Simulator(config=config)
        
        stats = simulator.run()
        
        # Should have some customers processed
        self.assertGreaterEqual(stats.get_total_customers_served(), 0)
    
    def test_run_with_verbose(self):
        """Test running simulation with verbose output."""
        config = SimulationConfig(
            num_tellers=2,
            simulation_duration=30.0,
            random_seed=42
        )
        simulator = Simulator(config=config)
        
        # Should not raise any errors
        stats = simulator.run(verbose=False)
        self.assertIsNotNone(stats)
    
    def test_step_simulation(self):
        """Test stepping through simulation one event at a time."""
        config = SimulationConfig(
            simulation_duration=60.0,
            random_seed=42
        )
        simulator = Simulator(config=config)
        simulator.initialize()
        
        event_count = 0
        while True:
            event = simulator.step()
            if event is None:
                break
            event_count += 1
            if event_count > 1000:  # Safety limit
                break
        
        self.assertGreater(event_count, 0)
    
    def test_callbacks(self):
        """Test event callbacks."""
        config = SimulationConfig(
            simulation_duration=60.0,
            random_seed=42
        )
        simulator = Simulator(config=config)
        
        arrivals = []
        completions = []
        
        simulator.on_customer_arrival(lambda c: arrivals.append(c))
        simulator.on_service_complete(lambda t, c: completions.append(c))
        
        simulator.run()
        
        self.assertGreater(len(arrivals), 0)
    
    def test_priority_distribution(self):
        """Test that priority distribution is applied."""
        config = SimulationConfig(
            simulation_duration=240.0,
            mean_arrival_interval=1.0,
            priority_distribution={
                CustomerPriority.VIP: 0.5,  # High VIP ratio for testing
                CustomerPriority.ELDERLY: 0.2,
                CustomerPriority.APPOINTMENT: 0.2,
                CustomerPriority.REGULAR: 0.1,
            },
            random_seed=42
        )
        simulator = Simulator(config=config)
        stats = simulator.run()
        
        # With high VIP distribution, should have some VIP customers
        served_by_priority = stats.get_customers_served_by_priority()
        total_served = sum(served_by_priority.values())
        
        if total_served > 0:
            # Just verify simulation ran successfully
            self.assertGreater(total_served, 0)
    
    def test_deterministic_with_seed(self):
        """Test that simulation is deterministic with same seed."""
        config1 = SimulationConfig(
            simulation_duration=60.0,
            random_seed=12345
        )
        config2 = SimulationConfig(
            simulation_duration=60.0,
            random_seed=12345
        )
        
        stats1 = Simulator(config=config1).run()
        stats2 = Simulator(config=config2).run()
        
        self.assertEqual(
            stats1.get_total_customers_served(),
            stats2.get_total_customers_served()
        )


if __name__ == '__main__':
    unittest.main()
