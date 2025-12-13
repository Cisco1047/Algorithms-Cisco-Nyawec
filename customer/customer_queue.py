from collections import deque
from .customer import Customer

class CustomerQueue:
    """
    Priority-based waiting line for customers.

    Priority order:
    1) VIP
    2) ELDERLY
    3) APPOINTMENT
    4) REGULAR (FIFO)
    """
    def __init__(self):
        self._vip = deque()
        self._elderly = deque()
        self._appointments = deque()
        self._regular = deque()

    def add_customer(self, customer: Customer) -> None:
        """Add a customer to the correct internal queue."""
        kind = customer.kind.upper()
        if kind == "VIP":
            self._vip.append(customer)
        elif kind == "ELDERLY":
            self._elderly.append(customer)
        elif kind == "APPOINTMENT":
            self._appointments.append(customer)
        elif kind == "REGULAR":
            self._regular.append(customer)
        else:
            raise ValueError(f"Unknown customer kind: {customer.kind}")
        
    def remove_customer(self, customer):
        queues = [self._vip, self._elderly, self._appointments, self._regular]
        for q in queues:
            if customer in q:
                q.remove(customer)
                return True
        return False

    def is_empty(self) -> bool:
        """Return True if no one is waiting."""
        return (not self._vip and
                not self._elderly and
                not self._appointments and
                not self._regular)

    def pop_next(self) -> Customer | None:
        if self._vip:
            return self._vip.popleft()
        if self._elderly:
            return self._elderly.popleft()
        if self._appointments:
            return self._appointments.popleft()
        if self._regular:
            return self._regular.popleft()
        return None
