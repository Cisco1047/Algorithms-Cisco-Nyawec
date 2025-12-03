"""
Unit tests for Event and EventQueue classes.
"""

import unittest
from bank_simulation.event import Event, EventType, EventQueue


class TestEventType(unittest.TestCase):
    """Tests for EventType enum."""
    
    def test_event_types_exist(self):
        """Test that all expected event types exist."""
        self.assertIsNotNone(EventType.CUSTOMER_ARRIVAL)
        self.assertIsNotNone(EventType.SERVICE_START)
        self.assertIsNotNone(EventType.SERVICE_COMPLETE)
        self.assertIsNotNone(EventType.CUSTOMER_ABANDON)
        self.assertIsNotNone(EventType.BANK_OPEN)
        self.assertIsNotNone(EventType.BANK_CLOSE)


class TestEvent(unittest.TestCase):
    """Tests for Event class."""
    
    def test_event_creation(self):
        """Test basic event creation."""
        event = Event(
            time=10.0,
            sequence=0,
            event_type=EventType.CUSTOMER_ARRIVAL
        )
        
        self.assertEqual(event.time, 10.0)
        self.assertEqual(event.sequence, 0)
        self.assertEqual(event.event_type, EventType.CUSTOMER_ARRIVAL)
        self.assertIsNone(event.data)
    
    def test_event_with_data(self):
        """Test event creation with data."""
        event = Event(
            time=10.0,
            sequence=0,
            event_type=EventType.SERVICE_COMPLETE,
            data={'teller_id': 1}
        )
        
        self.assertEqual(event.data, {'teller_id': 1})
    
    def test_event_ordering_by_time(self):
        """Test that events are ordered by time."""
        event1 = Event(time=10.0, sequence=0, event_type=EventType.CUSTOMER_ARRIVAL)
        event2 = Event(time=20.0, sequence=1, event_type=EventType.CUSTOMER_ARRIVAL)
        
        self.assertLess(event1, event2)
    
    def test_event_ordering_by_sequence(self):
        """Test that events with same time are ordered by sequence."""
        event1 = Event(time=10.0, sequence=0, event_type=EventType.CUSTOMER_ARRIVAL)
        event2 = Event(time=10.0, sequence=1, event_type=EventType.CUSTOMER_ARRIVAL)
        
        self.assertLess(event1, event2)


class TestEventQueue(unittest.TestCase):
    """Tests for EventQueue class."""
    
    def test_empty_queue(self):
        """Test empty queue behavior."""
        queue = EventQueue()
        
        self.assertTrue(queue.is_empty())
        self.assertEqual(len(queue), 0)
        self.assertIsNone(queue.pop())
        self.assertIsNone(queue.peek())
    
    def test_schedule_and_pop(self):
        """Test scheduling and popping events."""
        queue = EventQueue()
        
        queue.schedule(time=10.0, event_type=EventType.CUSTOMER_ARRIVAL)
        
        self.assertFalse(queue.is_empty())
        self.assertEqual(len(queue), 1)
        
        event = queue.pop()
        
        self.assertEqual(event.time, 10.0)
        self.assertEqual(event.event_type, EventType.CUSTOMER_ARRIVAL)
        self.assertTrue(queue.is_empty())
    
    def test_peek(self):
        """Test peeking at the next event."""
        queue = EventQueue()
        
        queue.schedule(time=10.0, event_type=EventType.CUSTOMER_ARRIVAL)
        
        event = queue.peek()
        self.assertEqual(event.time, 10.0)
        self.assertFalse(queue.is_empty())  # Event still in queue
    
    def test_chronological_order(self):
        """Test that events are returned in chronological order."""
        queue = EventQueue()
        
        queue.schedule(time=30.0, event_type=EventType.CUSTOMER_ARRIVAL)
        queue.schedule(time=10.0, event_type=EventType.CUSTOMER_ARRIVAL)
        queue.schedule(time=20.0, event_type=EventType.CUSTOMER_ARRIVAL)
        
        event1 = queue.pop()
        event2 = queue.pop()
        event3 = queue.pop()
        
        self.assertEqual(event1.time, 10.0)
        self.assertEqual(event2.time, 20.0)
        self.assertEqual(event3.time, 30.0)
    
    def test_sequence_order_for_simultaneous_events(self):
        """Test that simultaneous events are ordered by sequence."""
        queue = EventQueue()
        
        queue.schedule(time=10.0, event_type=EventType.CUSTOMER_ARRIVAL, data={'id': 1})
        queue.schedule(time=10.0, event_type=EventType.CUSTOMER_ARRIVAL, data={'id': 2})
        queue.schedule(time=10.0, event_type=EventType.CUSTOMER_ARRIVAL, data={'id': 3})
        
        event1 = queue.pop()
        event2 = queue.pop()
        event3 = queue.pop()
        
        # Should be returned in order they were scheduled
        self.assertEqual(event1.data, {'id': 1})
        self.assertEqual(event2.data, {'id': 2})
        self.assertEqual(event3.data, {'id': 3})


if __name__ == '__main__':
    unittest.main()
