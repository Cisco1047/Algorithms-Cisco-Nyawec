from simulation.engine import SimulationEngine
from simulation.teller import Teller
from simulation.metrics import Metrics
from customer.customer import Customer
from customer.customer_queue import CustomerQueue


# main.py

from customer.customer import Customer
from customer.customer_queue import CustomerQueue

q = CustomerQueue()

q.add_customer(Customer(id=1, kind="REGULAR", arrival_time=0.0, patience=10))
q.add_customer(Customer(id=2, kind="VIP", arrival_time=0.1, patience=5))
q.add_customer(Customer(id=3, kind="ELDERLY", arrival_time=0.2, patience=8))
q.add_customer(Customer(id=4, kind="REGULAR", arrival_time=0.3, patience=12))

while not q.is_empty():
    c = q.pop_next()
    print("Next served:", c)
