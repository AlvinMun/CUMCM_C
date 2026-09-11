
"""
CUMCM 2026 国赛 C题
Question 1 Linear Programming Optimizer
"""

import numpy as np
from scipy.optimize import linprog


def optimize_day(price, load, pv, battery):
    n = len(price)

    # 10-minute interval
    DELTA_T = 10 / 60

    # Convert power(kW) → energy(kWh)

    load = load * DELTA_T
    pv = pv * DELTA_T

    charge_limit = battery.max_charge_power * DELTA_T
    discharge_limit = battery.max_discharge_power * DELTA_T

    # Variable order:
    # G C D W S

    G0 = 0
    C0 = n
    D0 = 2 * n
    W0 = 3 * n
    S0 = 4 * n

    total_vars = 5 * n + 1

    c = np.zeros(total_vars)

    # Cost = price × purchased energy

    c[G0:G0 + n] = price

    Aeq = []
    beq = []

    eta_c = battery.charge_efficiency
    eta_d = battery.discharge_efficiency

    # Power balance

    for t in range(n):

        row = np.zeros(total_vars)

        row[G0 + t] = 1
        row[C0 + t] = -1
        row[D0 + t] = 1
        row[W0 + t] = -1

        Aeq.append(row)

        beq.append(load[t] - pv[t])

    # Battery dynamics

    for t in range(n):

        row = np.zeros(total_vars)

        row[S0 + t] = -1
        row[S0 + t + 1] = 1

        row[C0 + t] = -eta_c
        row[D0 + t] = 1 / eta_d

        Aeq.append(row)
        beq.append(0)

    # Initial SOC

    row = np.zeros(total_vars)
    row[S0] = 1

    Aeq.append(row)
    beq.append(battery.initial_energy)

    # End SOC = Start SOC

    row = np.zeros(total_vars)
    row[S0 + n] = 1

    Aeq.append(row)
    beq.append(battery.initial_energy)

    Aeq = np.array(Aeq)
    beq = np.array(beq)

    bounds = []

    # Grid purchase

    bounds.extend([(0, None)] * n)

    # Charge

    bounds.extend([(0, charge_limit)] * n)

    # Discharge

    bounds.extend([(0, discharge_limit)] * n)

    # Curtailment

    bounds.extend([(0, None)] * n)

    # Battery energy

    bounds.extend(
        [(battery.min_energy, battery.max_energy)]
        * (n + 1)
    )

    result = linprog(
        c,
        A_eq=Aeq,
        b_eq=beq,
        bounds=bounds,
        method="highs",
    )

    if not result.success:
        raise RuntimeError(result.message)

    x = result.x

    grid = x[G0:G0 + n]
    charge = x[C0:C0 + n]
    discharge = x[D0:D0 + n]
    curtail = x[W0:W0 + n]
    energy = x[S0:S0 + n + 1]

    return {
        "grid_purchase": grid,
        "charge": charge,
        "discharge": discharge,
        "curtailment": curtail,
        "battery_energy": energy,
        "total_cost": float(np.dot(grid, price)),
        "message": result.message,
    }