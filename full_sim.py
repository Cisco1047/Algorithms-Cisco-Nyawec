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
SWITCH_AFTER = 0.75          # minutes after arrival to attempt switching
PATIENCE_BONUS = 0.75        # extra minutes added to patience after switching
switched_once = set()

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

# Create tellers with different service rates
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
    teller.customers_served += 1
    customer.service_end = engine.current_time

    # After a customer finishes, attempt to assign another one
    try_assign_customer(engine)


# ======================================================
# ASSIGN CUSTOMERS TO AVAILABLE TELLERS (LOAD-BALANCED)
# ======================================================
def try_assign_customer(engine):  # Customer wait in queue.
    """
    Assign customers from the queue while tellers are free.
    Least busy teller is chosen first (load balancing).
    """
    while True:
        if not assigner.get_free_tellers(engine.current_time):
            return

        customer = queue.pop_next()
        if customer is None:
            return

        teller = assigner.assign_teller_to_priority_customer(engine.current_time, customer.kind)
        if teller is None:
            queue.add_customer(customer)  # Put the customer back
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
# Switching Stategies
# ======================================================
def schedule_switch_attempt(customer):
    switch_time = customer.arrival_time + SWITCH_AFTER

    def upgrade_customer_kind(customer) -> bool:
        """Upgrade one level: REGULAR->APPOINTMENT->ELDERLY->VIP. Return True if upgraded."""
        k = customer.kind.upper()
        if k == "REGULAR":
            customer.kind = "APPOINTMENT"
            return True
        if k == "APPOINTMENT":
            customer.kind = "ELDERLY"
            return True
        if k == "ELDERLY":
            customer.kind = "VIP"
            return True
        return False

    def switch_action(engine, cust=customer):
        # already switched, already in service, or already abandoned => no action
        if cust.id in switched_once or cust.service_start is not None or cust.abandoned:
            return

        # only switch if they are still waiting in the queue
        if queue.remove_customer(cust):
            if upgrade_customer_kind(cust):
                switched_once.add(cust.id)

                # increase patience a bit after switching
                cust.patience += PATIENCE_BONUS

                queue.add_customer(cust)
                print(f"[{engine.current_time:.2f}] Customer SWITCHED → {cust}")

                # schedule a new abandonment check using the updated patience
                schedule_abandonment(cust)

                # attempt assignment immediately
                try_assign_customer(engine)
            else:
                # couldn't upgrade (VIP), put back
                queue.add_customer(cust)

    engine.schedule(switch_time, switch_action)


# ======================================================
# ABANDONMENT EVENT — fires when patience expires
# ======================================================
def schedule_abandonment(customer):
    abandon_time = customer.arrival_time + customer.patience

    def abandonment_action(engine, cust=customer):
        # Only abandon if NOT already served
        if engine.current_time < cust.arrival_time + cust.patience:
            return

        if cust.service_start is None and not cust.abandoned:
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
    schedule_switch_attempt(customer)

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
        inter = random.expovariate(ARRIVAL_RATE)  # Random customer inter-arrival time
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

    sim_time = engine.current_time if engine.current_time > 0 else 1.0

    print("\n========== SIMULATION COMPLETE ==========")
    print(f"Total Simulation Time: {sim_time:.2f} minutes")
    print(f"Average Wait Time:     {results['average_wait']:.2f} minutes")
    print(f"Abandonment Rate:      {results['abandonment_rate']*100:.2f}%")
    print(f"Average Queue Length:  {results['queue_length_avg']:.2f}\n")

    print("Teller Utilization:")
    for teller in tellers:
        utilization = (teller.total_busy_time / sim_time)
        throughput = teller.customers_served / sim_time
        avg_serve_time = (teller.total_busy_time / teller.customers_served) if teller.customers_served else 0.0
        efficiency_time = (teller.customers_served / teller.total_busy_time) if teller.total_busy_time > 0 else 0.0
        print(f"Teller {teller.id}:\n------------------------------\n"
              f"{teller.total_busy_time:.2f} minutes busy\n"
              f"Utilization: {utilization*100:.2f}%\n"
              f"Throughput: {throughput:.2f} customers/minute\n"
              f"Average Service Time: {avg_serve_time:.2f} minutes/customer\n"
              f"Efficiency Rate(customers per busy minute): {efficiency_time:.2f}\n")


# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    random.seed(42)

    schedule_customer_arrivals()
    engine.run()
    end_simulation()
