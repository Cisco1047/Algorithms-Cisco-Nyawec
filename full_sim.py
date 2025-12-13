import random
from simulation.engine import SimulationEngine
from simulation.assignment import TellerAssignmentSystem
from simulation.teller import Teller
from simulation.metrics import Metrics
from customer.customer_queue import CustomerQueue
from customer.customer import Customer


# ======================================================
# CONFIGURATION — tuned to produce wait + abandonment
# ======================================================
NUM_CUSTOMERS = 60
ARRIVAL_RATE = 3.0          # arrivals per minute (faster than service capacity)
PATIENCE_MIN = 0.5
PATIENCE_MAX = 2.0

SERVICE_RATES = {           # customers per minute
    "FAST": 1.2,
    "MEDIUM": 0.9,
    "SLOW": 0.5
}


# ======================================================
# SYSTEM COMPONENTS
# ======================================================
engine = SimulationEngine()
queue = CustomerQueue()
metrics = Metrics()

tellers = [
    Teller(1, SERVICE_RATES["FAST"]),
    Teller(2, SERVICE_RATES["MEDIUM"]),
    Teller(3, SERVICE_RATES["SLOW"])
]

assigner = TellerAssignmentSystem(tellers)


# ======================================================
# SERVICE COMPLETION EVENT
# ======================================================
def finish_service(engine, teller, customer):
    teller.finish_service()
    customer.service_end = engine.current_time

    # After a customer finishes, attempt to assign another one
    try_assign_customer(engine)


# ======================================================
# ASSIGN CUSTOMERS TO AVAILABLE TELLERS (LOAD-BALANCED)
# ======================================================
def try_assign_customer(engine):
    """
    Assign customers from the queue while tellers are free.
    Least busy teller is chosen first (load balancing).
    """
    while True:
        teller = assigner.get_free_teller(engine.current_time)
        if teller is None:
            return

        customer = queue.pop_next()
        if customer is None:
            return

        # Customer begins service now
        customer.service_start = engine.current_time
        wait_time = customer.service_start - customer.arrival_time
        metrics.record_wait(wait_time)

        # Generate service time
        service_time = teller.start_service(engine, customer)

        # Schedule the departure event
        engine.schedule(
            engine.current_time + service_time,
            lambda eng, t=teller, c=customer: finish_service(eng, t, c)
        )


# ======================================================
# ABANDONMENT EVENT — fires when patience expires
# ======================================================
def schedule_abandonment(customer):
    abandon_time = customer.arrival_time + customer.patience

    def abandonment_action(engine, cust=customer):
        # Only abandon if NOT already served
        if cust.service_start is None:
            removed = queue.remove_customer(cust)
            if removed:
                cust.abandoned = True
                metrics.record_abandonment()
                print(f"[{engine.current_time:.2f}] Customer ABANDONED → {cust}")
                try_assign_customer(engine)

    engine.schedule(abandon_time, abandonment_action)


# ======================================================
# ARRIVAL EVENT
# ======================================================
def arrival_event(engine, customer):
    metrics.record_arrival()
    queue.add_customer(customer)

    # Log queue length
    metrics.record_queue_length(
        len(queue._vip) +
        len(queue._elderly) +
        len(queue._appointments) +
        len(queue._regular)
    )

    print(f"[{engine.current_time:.2f}] Customer ARRIVED → {customer}")

    # Schedule possible abandonment
    schedule_abandonment(customer)

    # Immediately attempt assignment
    try_assign_customer(engine)


# ======================================================
# GENERATE ARRIVALS
# ======================================================
def schedule_customer_arrivals():
    current_time = 0

    for i in range(1, NUM_CUSTOMERS + 1):
        inter = random.expovariate(ARRIVAL_RATE)
        current_time += inter

        cust = Customer(
            id=i,
            kind=random.choice(["VIP", "ELDERLY", "APPOINTMENT", "REGULAR"]),
            arrival_time=current_time,
            patience=random.uniform(PATIENCE_MIN, PATIENCE_MAX)
        )

        engine.schedule(current_time, lambda eng, c=cust: arrival_event(eng, c))


# ======================================================
# FINAL REPORT
# ======================================================
def end_simulation():
    results = metrics.compute_results()

    print("\n========== SIMULATION COMPLETE ==========")
    print(f"Average Wait Time:     {results['average_wait']:.2f} minutes")
    print(f"Abandonment Rate:      {results['abandonment_rate']*100:.2f}%")
    print(f"Average Queue Length:  {results['queue_length_avg']:.2f}\n")

    print("Teller Utilization:")
    for teller in tellers:
        print(f"  Teller {teller.id}: {teller.total_busy_time:.2f} minutes busy")


# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    random.seed(42)

    schedule_customer_arrivals()
    engine.run()
    end_simulation()


