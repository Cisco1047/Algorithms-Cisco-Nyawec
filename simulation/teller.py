class Teller:
    def __init__(self, id, service_rate):
        self.id = id
        self.service_rate = service_rate

        self.is_busy = False
        self.busy_until = 0
        self.total_busy_time = 0

        self.customers_served = 0

    def start_service(self, engine, customer):
        self.is_busy = True

        import random
        service_time = random.expovariate(self.service_rate)

        self.total_busy_time += service_time
        self.busy_until = engine.current_time + service_time
        return service_time

    def finish_service(self):
        self.is_busy = False

