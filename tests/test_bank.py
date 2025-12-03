"""
Unit tests for Bank class.
"""

import unittest
from bank_simulation.customer import Customer, CustomerPriority
from bank_simulation.teller import Teller
from bank_simulation.bank_queue import BankQueue
from bank_simulation.bank import Bank


class TestBank(unittest.TestCase):
    """Tests for Bank class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tellers = [
            Teller(teller_id=0, efficiency=1.0),
            Teller(teller_id=1, efficiency=1.5),
        ]
        self.bank = Bank(tellers=self.tellers)
    
    def test_bank_creation(self):
        """Test basic bank creation."""
        self.assertEqual(len(self.bank.tellers), 2)
        self.assertIsNotNone(self.bank.queue)
        self.assertFalse(self.bank.is_open)
    
    def test_open_bank(self):
        """Test opening the bank."""
        self.bank.open_bank(current_time=0.0)
        
        self.assertTrue(self.bank.is_open)
    
    def test_close_bank(self):
        """Test closing the bank."""
        self.bank.open_bank(current_time=0.0)
        self.bank.close_bank()
        
        self.assertFalse(self.bank.is_open)
    
    def test_customer_arrives_when_open(self):
        """Test customer arrival when bank is open."""
        self.bank.open_bank(current_time=0.0)
        customer = Customer(customer_id=1, arrival_time=5.0)
        
        result = self.bank.customer_arrives(customer)
        
        self.assertTrue(result)
        self.assertEqual(self.bank.get_queue_length(), 1)
    
    def test_customer_arrives_when_closed(self):
        """Test customer arrival when bank is closed."""
        customer = Customer(customer_id=1, arrival_time=5.0)
        
        result = self.bank.customer_arrives(customer)
        
        self.assertFalse(result)
        self.assertEqual(self.bank.get_queue_length(), 0)
    
    def test_get_available_teller(self):
        """Test getting an available teller."""
        self.bank.open_bank(current_time=0.0)
        
        teller = self.bank.get_available_teller()
        
        self.assertIsNotNone(teller)
        self.assertTrue(teller.is_available())
    
    def test_get_available_teller_none_available(self):
        """Test when no teller is available."""
        self.bank.open_bank(current_time=0.0)
        
        # Make all tellers busy
        for teller in self.bank.tellers:
            customer = Customer(customer_id=teller.teller_id, arrival_time=0.0)
            teller.start_service(customer, current_time=0.0)
        
        teller = self.bank.get_available_teller()
        
        self.assertIsNone(teller)
    
    def test_try_assign_customer_to_teller(self):
        """Test assigning a customer to an available teller."""
        self.bank.open_bank(current_time=0.0)
        customer = Customer(customer_id=1, arrival_time=0.0, service_time_required=10.0)
        self.bank.customer_arrives(customer)
        
        result = self.bank.try_assign_customer_to_teller(current_time=0.0)
        
        self.assertIsNotNone(result)
        teller, assigned_customer, end_time = result
        self.assertEqual(assigned_customer, customer)
        self.assertFalse(teller.is_available())
    
    def test_try_assign_customer_no_waiting(self):
        """Test assignment when no customers waiting."""
        self.bank.open_bank(current_time=0.0)
        
        result = self.bank.try_assign_customer_to_teller(current_time=0.0)
        
        self.assertIsNone(result)
    
    def test_try_assign_customer_no_teller_available(self):
        """Test assignment when no teller available."""
        self.bank.open_bank(current_time=0.0)
        
        # Add customers
        for i in range(3):
            customer = Customer(customer_id=i, arrival_time=0.0)
            self.bank.customer_arrives(customer)
        
        # Assign first two customers
        self.bank.try_assign_customer_to_teller(current_time=0.0)
        self.bank.try_assign_customer_to_teller(current_time=0.0)
        
        # Third assignment should fail (all tellers busy)
        result = self.bank.try_assign_customer_to_teller(current_time=0.0)
        
        self.assertIsNone(result)
    
    def test_complete_service(self):
        """Test completing service for a customer."""
        self.bank.open_bank(current_time=0.0)
        customer = Customer(customer_id=1, arrival_time=0.0, service_time_required=10.0)
        self.bank.customer_arrives(customer)
        
        teller, _, _ = self.bank.try_assign_customer_to_teller(current_time=0.0)
        completed = self.bank.complete_service(teller, current_time=10.0)
        
        self.assertEqual(completed, customer)
        self.assertTrue(teller.is_available())
    
    def test_process_abandonments(self):
        """Test processing customer abandonments."""
        self.bank.open_bank(current_time=0.0)
        
        # First occupy all tellers so customers will wait in queue
        for teller in self.bank.tellers:
            customer = Customer(customer_id=100 + teller.teller_id, arrival_time=0.0)
            self.bank.customer_arrives(customer)
            self.bank.try_assign_customer_to_teller(current_time=0.0)
        
        # Now add customers who will wait in queue
        patient = Customer(customer_id=1, arrival_time=0.0, patience=50.0)
        impatient = Customer(customer_id=2, arrival_time=0.0, patience=5.0)
        
        self.bank.customer_arrives(patient)
        self.bank.customer_arrives(impatient)
        
        abandoned = self.bank.process_abandonments(current_time=10.0)
        
        self.assertEqual(len(abandoned), 1)
        self.assertEqual(abandoned[0].customer_id, 2)
    
    def test_has_waiting_customers(self):
        """Test checking for waiting customers."""
        self.bank.open_bank(current_time=0.0)
        
        self.assertFalse(self.bank.has_waiting_customers())
        
        customer = Customer(customer_id=1, arrival_time=0.0)
        self.bank.customer_arrives(customer)
        
        self.assertTrue(self.bank.has_waiting_customers())
    
    def test_has_customers_being_served(self):
        """Test checking if customers are being served."""
        self.bank.open_bank(current_time=0.0)
        
        self.assertFalse(self.bank.has_customers_being_served())
        
        customer = Customer(customer_id=1, arrival_time=0.0)
        self.bank.customer_arrives(customer)
        self.bank.try_assign_customer_to_teller(current_time=0.0)
        
        self.assertTrue(self.bank.has_customers_being_served())


if __name__ == '__main__':
    unittest.main()
