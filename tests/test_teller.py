"""
Unit tests for Teller class.
"""

import unittest
from bank_simulation.customer import Customer, CustomerPriority
from bank_simulation.teller import Teller


class TestTeller(unittest.TestCase):
    """Tests for Teller class."""
    
    def test_teller_creation(self):
        """Test basic teller creation."""
        teller = Teller(teller_id=0)
        
        self.assertEqual(teller.teller_id, 0)
        self.assertEqual(teller.efficiency, 1.0)
        self.assertTrue(teller.is_available())
        self.assertEqual(len(teller.customers_served), 0)
    
    def test_teller_with_custom_efficiency(self):
        """Test teller creation with custom efficiency."""
        teller = Teller(teller_id=1, efficiency=1.5)
        
        self.assertEqual(teller.efficiency, 1.5)
    
    def test_is_available(self):
        """Test availability check."""
        teller = Teller(teller_id=0)
        
        self.assertTrue(teller.is_available())
        
        teller.current_customer = Customer(customer_id=1, arrival_time=0.0)
        self.assertFalse(teller.is_available())
    
    def test_calculate_service_time_normal_efficiency(self):
        """Test service time calculation with normal efficiency."""
        teller = Teller(teller_id=0, efficiency=1.0)
        customer = Customer(customer_id=1, arrival_time=0.0, service_time_required=10.0)
        
        service_time = teller.calculate_service_time(customer)
        self.assertEqual(service_time, 10.0)
    
    def test_calculate_service_time_high_efficiency(self):
        """Test service time calculation with high efficiency."""
        teller = Teller(teller_id=0, efficiency=2.0)
        customer = Customer(customer_id=1, arrival_time=0.0, service_time_required=10.0)
        
        service_time = teller.calculate_service_time(customer)
        self.assertEqual(service_time, 5.0)
    
    def test_calculate_service_time_low_efficiency(self):
        """Test service time calculation with low efficiency."""
        teller = Teller(teller_id=0, efficiency=0.5)
        customer = Customer(customer_id=1, arrival_time=0.0, service_time_required=10.0)
        
        service_time = teller.calculate_service_time(customer)
        self.assertEqual(service_time, 20.0)
    
    def test_start_service(self):
        """Test starting service for a customer."""
        teller = Teller(teller_id=0, efficiency=1.0)
        customer = Customer(customer_id=1, arrival_time=0.0, service_time_required=10.0)
        
        end_time = teller.start_service(customer, current_time=5.0)
        
        self.assertEqual(end_time, 15.0)
        self.assertEqual(customer.service_start_time, 5.0)
        self.assertEqual(teller.current_customer, customer)
        self.assertFalse(teller.is_available())
    
    def test_start_service_when_busy(self):
        """Test that starting service when busy raises error."""
        teller = Teller(teller_id=0)
        customer1 = Customer(customer_id=1, arrival_time=0.0)
        customer2 = Customer(customer_id=2, arrival_time=1.0)
        
        teller.start_service(customer1, current_time=5.0)
        
        with self.assertRaises(ValueError):
            teller.start_service(customer2, current_time=6.0)
    
    def test_complete_service(self):
        """Test completing service for a customer."""
        teller = Teller(teller_id=0)
        customer = Customer(customer_id=1, arrival_time=0.0, service_time_required=10.0)
        
        teller.start_service(customer, current_time=5.0)
        completed_customer = teller.complete_service(current_time=15.0)
        
        self.assertEqual(completed_customer, customer)
        self.assertEqual(customer.service_end_time, 15.0)
        self.assertTrue(teller.is_available())
        self.assertIn(customer, teller.customers_served)
        self.assertEqual(teller.total_busy_time, 10.0)
    
    def test_complete_service_when_idle(self):
        """Test that completing service when idle raises error."""
        teller = Teller(teller_id=0)
        
        with self.assertRaises(ValueError):
            teller.complete_service(current_time=10.0)
    
    def test_get_utilization(self):
        """Test utilization calculation."""
        teller = Teller(teller_id=0)
        teller.total_busy_time = 30.0
        
        utilization = teller.get_utilization(total_time=100.0)
        self.assertEqual(utilization, 0.3)
    
    def test_get_utilization_zero_time(self):
        """Test utilization with zero total time."""
        teller = Teller(teller_id=0)
        
        utilization = teller.get_utilization(total_time=0.0)
        self.assertEqual(utilization, 0.0)
    
    def test_get_utilization_capped(self):
        """Test that utilization is capped at 1.0."""
        teller = Teller(teller_id=0)
        teller.total_busy_time = 150.0
        
        utilization = teller.get_utilization(total_time=100.0)
        self.assertEqual(utilization, 1.0)


if __name__ == '__main__':
    unittest.main()
