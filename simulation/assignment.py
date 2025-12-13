class TellerAssignmentSystem:
    def __init__(self, tellers):
        self.tellers = tellers

    def get_free_teller(self, current_time):
        for teller in self.tellers:
            if not teller.is_busy or teller.busy_until <= current_time:
                teller.is_busy = False
                return teller
        return None

    def assign_customer(self, engine, customer):
        teller = self.get_free_teller(engine.current_time)
        if teller is None:
            return None 

        service_time = teller.start_service(engine, customer)

        engine.schedule(engine.current_time + service_time,
                        lambda eng: self.finish_customer(eng, teller, customer))
        return teller

    def finish_customer(self, engine, teller, customer):
        teller.finish_service()
        print(f"[{engine.current_time}] Customer {customer.id} finished at Teller {teller.id}")
