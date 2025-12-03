"""
Unit tests for BankQueue class.
"""

import unittest
from bank_simulation.customer import Customer, CustomerPriority
from bank_simulation.bank_queue import BankQueue


class TestBankQueue(unittest.TestCase):
    """Tests for BankQueue class."""
    
    def test_empty_queue(self):
        """Test empty queue behavior."""
        queue = BankQueue()
        
        self.assertTrue(queue.is_empty())
        self.assertFalse(queue.is_full())
        self.assertEqual(queue.get_queue_length(), 0)
        self.assertIsNone(queue.get_next_customer())
        self.assertIsNone(queue.peek())
    
    def test_add_customer(self):
        """Test adding a customer to the queue."""
        queue = BankQueue()
        customer = Customer(customer_id=1, arrival_time=10.0)
        
        result = queue.add_customer(customer)
        
        self.assertTrue(result)
        self.assertEqual(queue.get_queue_length(), 1)
        self.assertFalse(queue.is_empty())
    
    def test_add_customer_to_full_queue(self):
        """Test adding a customer when queue is full."""
        queue = BankQueue(max_size=2)
        
        queue.add_customer(Customer(customer_id=1, arrival_time=0.0))
        queue.add_customer(Customer(customer_id=2, arrival_time=1.0))
        
        self.assertTrue(queue.is_full())
        
        result = queue.add_customer(Customer(customer_id=3, arrival_time=2.0))
        self.assertFalse(result)
        self.assertEqual(queue.get_queue_length(), 2)
    
    def test_get_next_customer(self):
        """Test getting the next customer from queue."""
        queue = BankQueue()
        customer = Customer(customer_id=1, arrival_time=10.0)
        
        queue.add_customer(customer)
        next_customer = queue.get_next_customer()
        
        self.assertEqual(next_customer, customer)
        self.assertTrue(queue.is_empty())
    
    def test_peek(self):
        """Test peeking at the next customer."""
        queue = BankQueue()
        customer = Customer(customer_id=1, arrival_time=10.0)
        
        queue.add_customer(customer)
        peeked = queue.peek()
        
        self.assertEqual(peeked, customer)
        self.assertFalse(queue.is_empty())  # Customer still in queue
    
    def test_priority_ordering(self):
        """Test that customers are returned by priority."""
        queue = BankQueue()
        
        regular = Customer(customer_id=1, arrival_time=0.0, priority=CustomerPriority.REGULAR)
        vip = Customer(customer_id=2, arrival_time=5.0, priority=CustomerPriority.VIP)
        elderly = Customer(customer_id=3, arrival_time=2.0, priority=CustomerPriority.ELDERLY)
        
        queue.add_customer(regular)
        queue.add_customer(vip)
        queue.add_customer(elderly)
        
        # Should return in priority order: VIP, ELDERLY, REGULAR
        self.assertEqual(queue.get_next_customer().priority, CustomerPriority.VIP)
        self.assertEqual(queue.get_next_customer().priority, CustomerPriority.ELDERLY)
        self.assertEqual(queue.get_next_customer().priority, CustomerPriority.REGULAR)
    
    def test_fifo_within_same_priority(self):
        """Test FIFO ordering within same priority level."""
        queue = BankQueue()
        
        customer1 = Customer(customer_id=1, arrival_time=10.0)
        customer2 = Customer(customer_id=2, arrival_time=20.0)
        customer3 = Customer(customer_id=3, arrival_time=15.0)
        
        queue.add_customer(customer2)
        queue.add_customer(customer1)
        queue.add_customer(customer3)
        
        # Should return in arrival order
        self.assertEqual(queue.get_next_customer().customer_id, 1)
        self.assertEqual(queue.get_next_customer().customer_id, 3)
        self.assertEqual(queue.get_next_customer().customer_id, 2)
    
    def test_remove_customer(self):
        """Test removing a specific customer from queue."""
        queue = BankQueue()
        
        customer1 = Customer(customer_id=1, arrival_time=0.0)
        customer2 = Customer(customer_id=2, arrival_time=1.0)
        
        queue.add_customer(customer1)
        queue.add_customer(customer2)
        
        result = queue.remove_customer(customer1)
        
        self.assertTrue(result)
        self.assertEqual(queue.get_queue_length(), 1)
        self.assertEqual(queue.get_next_customer(), customer2)
    
    def test_remove_nonexistent_customer(self):
        """Test removing a customer not in queue."""
        queue = BankQueue()
        customer = Customer(customer_id=1, arrival_time=0.0)
        
        result = queue.remove_customer(customer)
        
        self.assertFalse(result)
    
    def test_process_abandonments(self):
        """Test processing customer abandonments."""
        queue = BankQueue()
        
        patient = Customer(customer_id=1, arrival_time=0.0, patience=20.0)
        impatient = Customer(customer_id=2, arrival_time=0.0, patience=5.0)
        
        queue.add_customer(patient)
        queue.add_customer(impatient)
        
        abandoned = queue.process_abandonments(current_time=10.0)
        
        self.assertEqual(len(abandoned), 1)
        self.assertEqual(abandoned[0].customer_id, 2)
        self.assertTrue(abandoned[0].abandoned)
        self.assertEqual(queue.get_queue_length(), 1)
    
    def test_get_customers_by_priority(self):
        """Test getting customer counts by priority."""
        queue = BankQueue()
        
        queue.add_customer(Customer(customer_id=1, arrival_time=0.0, priority=CustomerPriority.VIP))
        queue.add_customer(Customer(customer_id=2, arrival_time=1.0, priority=CustomerPriority.VIP))
        queue.add_customer(Customer(customer_id=3, arrival_time=2.0, priority=CustomerPriority.REGULAR))
        
        counts = queue.get_customers_by_priority()
        
        self.assertEqual(counts[CustomerPriority.VIP], 2)
        self.assertEqual(counts[CustomerPriority.REGULAR], 1)
        self.assertEqual(counts[CustomerPriority.ELDERLY], 0)
    
    def test_abandonment_rate(self):
        """Test abandonment rate calculation."""
        queue = BankQueue()
        
        queue.add_customer(Customer(customer_id=1, arrival_time=0.0, patience=5.0))
        queue.add_customer(Customer(customer_id=2, arrival_time=0.0, patience=5.0))
        queue.add_customer(Customer(customer_id=3, arrival_time=0.0, patience=50.0))
        queue.add_customer(Customer(customer_id=4, arrival_time=0.0, patience=50.0))
        
        queue.process_abandonments(current_time=10.0)
        
        # 2 out of 4 abandoned
        self.assertEqual(queue.get_abandonment_rate(), 0.5)


if __name__ == '__main__':
    unittest.main()
