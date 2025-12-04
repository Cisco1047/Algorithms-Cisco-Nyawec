from dataclasses import dataclass
"""
This module defines the Customer data structure for a queuing system simulation.
"""
@dataclass
class Customer:
    id: int
    kind: str
    arrival_time: float
    patience: float

    def __repr__(self) -> str:
        return (f"Customer(id={self.id}, kind='{self.kind}', "
                f"arrival_time={self.arrival_time}, patience={self.patience})")