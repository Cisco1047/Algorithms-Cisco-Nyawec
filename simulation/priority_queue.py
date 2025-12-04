class PriorityBasedScheduler:
    def __init__(self):
        self.vip = []
        self.elderly = []
        self.regular = []

    def ArrivalType(self):
        self.walkin = 'Regular'
        self.appointment = 'vip'

    def put(self, item, priority):
        self.elements.append((priority, item))
        self.elements.sort(key=lambda x: x[0])  # Sort by priority

    def get(self):
        return self.elements.pop(0)[1]  # Return the item with highest priority (lowest number)