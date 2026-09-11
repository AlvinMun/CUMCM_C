
from dataclasses import dataclass


@dataclass
class Battery:
    """Official battery parameters for CUMCM C Question 1."""

    capacity: float
    initial_energy: float
    max_charge_power: float
    max_discharge_power: float
    charge_efficiency: float
    discharge_efficiency: float

    min_energy: float = 1200.0
    max_energy: float = 10800.0

    def next_energy(self, current, charge, discharge):
        return (
            current
            + self.charge_efficiency * charge
            - discharge / self.discharge_efficiency
        )