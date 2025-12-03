"""
Unit tests for Customer and CustomerPriority classes.
"""

import unittest
from bank_simulation.customer import Customer, CustomerPriority


class TestCustomerPriority(unittest.TestCase):
    """Tests for CustomerPriority enum."""
    
    def test_priority_ordering(self):
        """Test that priority values are ordered correctly."""
        self.assertLess(CustomerPriority.VIP, CustomerPriority.ELDERLY)
        self.assertLess(CustomerPriority.ELDERLY, CustomerPriority.APPOINTMENT)
        self.assertLess(CustomerPriority.APPOINTMENT, CustomerPriority.REGULAR)
    
    def test_priority_values(self):
        """Test that priority values are integers."""
        self.assertEqual(CustomerPriority.VIP, 1)
        self.assertEqual(CustomerPriority.ELDERLY, 2)
        self.assertEqual(CustomerPriority.APPOINTMENT, 3)
        self.assertEqual(CustomerPriority.REGULAR, 4)


class TestCustomer(unittest.TestCase):
    """Tests for Customer class."""
    
    def test_customer_creation(self):
        """Test basic customer creation."""
        customer = Customer(customer_id=1, arrival_time=10.0)
        
        self.assertEqual(customer.customer_id, 1)
        self.assertEqual(customer.arrival_time, 10.0)
        self.assertEqual(customer.priority, CustomerPriority.REGULAR)
        self.assertFalse(customer.abandoned)
        self.assertIsNone(customer.service_start_time)
        self.assertIsNone(customer.service_end_time)
    
    def test_customer_with_priority(self):
        """Test customer creation with custom priority."""
        customer = Customer(
            customer_id=1,
            arrival_time=10.0,
            priority=CustomerPriority.VIP
        )
        
        self.assertEqual(customer.priority, CustomerPriority.VIP)
    
    def test_get_wait_time_not_served(self):
        """Test wait time calculation for unserved customer."""
        customer = Customer(customer_id=1, arrival_time=10.0)
        self.assertIsNone(customer.get_wait_time())
    
    def test_get_wait_time_served(self):
        """Test wait time calculation for served customer."""
        customer = Customer(customer_id=1, arrival_time=10.0)
        customer.service_start_time = 15.0
        
        self.assertEqual(customer.get_wait_time(), 5.0)
    
    def test_get_total_time(self):
        """Test total time calculation."""
        customer = Customer(customer_id=1, arrival_time=10.0)
        customer.service_start_time = 15.0
        customer.service_end_time = 20.0
        
        self.assertEqual(customer.get_total_time(), 10.0)
    
    def test_get_total_time_not_complete(self):
        """Test total time for incomplete service."""
        customer = Customer(customer_id=1, arrival_time=10.0)
        customer.service_start_time = 15.0
        
        self.assertIsNone(customer.get_total_time())
    
    def test_should_abandon_within_patience(self):
        """Test abandonment check within patience limit."""
        customer = Customer(customer_id=1, arrival_time=10.0, patience=20.0)
        
        self.assertFalse(customer.should_abandon(current_time=25.0))
    
    def test_should_abandon_exceeded_patience(self):
        """Test abandonment check when patience exceeded."""
        customer = Customer(customer_id=1, arrival_time=10.0, patience=10.0)
        
        self.assertTrue(customer.should_abandon(current_time=25.0))
    
    def test_should_abandon_when_being_served(self):
        """Test that customer doesn't abandon when being served."""
        customer = Customer(customer_id=1, arrival_time=10.0, patience=5.0)
        customer.service_start_time = 12.0
        
        self.assertFalse(customer.should_abandon(current_time=20.0))
    
    def test_customer_comparison_by_priority(self):
        """Test customer comparison prioritizes by priority level."""
        vip = Customer(customer_id=1, arrival_time=20.0, priority=CustomerPriority.VIP)
        regular = Customer(customer_id=2, arrival_time=10.0, priority=CustomerPriority.REGULAR)
        
        self.assertLess(vip, regular)  # VIP comes first despite later arrival
    
    def test_customer_comparison_same_priority(self):
        """Test customer comparison uses FIFO for same priority."""
        customer1 = Customer(customer_id=1, arrival_time=10.0)
        customer2 = Customer(customer_id=2, arrival_time=20.0)
        
        self.assertLess(customer1, customer2)  # Earlier arrival comes first


if __name__ == '__main__':
    unittest.main()
