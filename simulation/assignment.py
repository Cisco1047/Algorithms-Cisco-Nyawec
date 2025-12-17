class TellerAssignmentSystem:
    def __init__(self, tellers):
        self.tellers = tellers

    """
    Changed implementation to line up more with the requirement of having 
    "faster tellers assigned to high-priority queue."
    """
    def get_free_tellers(self, current_time):
        available_tellers = []
        for teller in self.tellers:
            if not teller.is_busy or teller.busy_until <= current_time:
                teller.is_busy = False
                available_tellers.append(teller)
        return available_tellers

    def assign_teller_to_priority_customer(self, customer_time, customer_kind: str):
        available_tellers = self.get_free_tellers(customer_time)
        if not available_tellers:
            return None

        kind = customer_kind.upper()

        # Assign the fastest available teller to high-priority customers
        if kind in ('VIP', 'ELDERLY', 'APPOINTMENT'):
            return max(available_tellers, key=lambda t: t.service_rate)
        return min(available_tellers, key=lambda t: (t.total_busy_time, t.service_rate))
