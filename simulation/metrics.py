class Metrics:
    def __init__(self):
        self.wait_times = []
        self.abandoned = 0
        self.total_arrivals = 0
        self.queue_lengths = []
        self.teller_utilization = []

    def record_arrival(self):
        self.total_arrivals += 1

    def record_wait(self, wait):
        self.wait_times.append(wait)

    def record_abandonment(self):
        self.abandoned += 1

    def record_queue_length(self, qlen):
        self.queue_lengths.append(qlen)

    def compute_results(self):
        avg_wait = sum(self.wait_times)/len(self.wait_times) if self.wait_times else 0
        abandonment_rate = self.abandoned / self.total_arrivals if self.total_arrivals else 0

        return {
            "average_wait": avg_wait,
            "abandonment_rate": abandonment_rate,
            "queue_length_avg": sum(self.queue_lengths)/len(self.queue_lengths) if self.queue_lengths else 0,
        }
