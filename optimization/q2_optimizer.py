
"""
CUMCM 2026 国赛 C题
Question 2 Optimizer

LP model with:
- Planned purchase
- Emergency purchase
- Battery storage
- Curtailment
- Cross-day battery continuity
"""

import numpy as np
from scipy.optimize import linprog

DELTA_T = 10 / 60  # hour


def optimize_day_q2(price, load_kw, pv_kw, battery, initial_energy):
    """
    Optimize one day (144 intervals).

    Parameters
    ----------
    price : ndarray(144,)
    load_kw : ndarray(144,)
    pv_kw : ndarray(144,)
    battery : Battery
    initial_energy : float

    Returns
    -------
    dict
    """

    n = len(price)

    load = load_kw * DELTA_T
    pv = pv_kw * DELTA_T

    charge_limit = battery.max_charge_power * DELTA_T
    discharge_limit = battery.max_discharge_power * DELTA_T

    eta_c = battery.charge_efficiency
    eta_d = battery.discharge_efficiency

    # Variable order
    #
    # G,E,C,D,W,S
    #

    G0 = 0
    E0 = G0 + n
    C0 = E0 + n
    D0 = C0 + n
    W0 = D0 + n
    S0 = W0 + n

    total_vars = 5 * n + (n + 1)

    # Objective
    c = np.zeros(total_vars)

    c[G0:G0+n] = price
    c[E0:E0+n] = 5 * price


    # Equality constraints
    Aeq = []
    beq = []

    # Power balance

    for t in range(n):

        row = np.zeros(total_vars)

        row[G0+t] = 1
        row[E0+t] = 1
        row[C0+t] = -1
        row[D0+t] = 1
        row[W0+t] = -1

        Aeq.append(row)
        beq.append(load[t] - pv[t])

    # Battery dynamics

    for t in range(n):

        row = np.zeros(total_vars)

        row[S0+t] = -1
        row[S0+t+1] = 1

        row[C0+t] = -eta_c
        row[D0+t] = 1 / eta_d

        Aeq.append(row)
        beq.append(0)

    # Initial SOC

    row = np.zeros(total_vars)
    row[S0] = 1

    Aeq.append(row)
    beq.append(initial_energy)

    Aeq = np.array(Aeq)
    beq = np.array(beq)

    # Variable bounds

    bounds = []

    # Planned purchase
    bounds.extend([(0, None)] * n)

    # Emergency purchase
    bounds.extend([(0, None)] * n)

    # Charge
    bounds.extend([(0, charge_limit)] * n)

    # Discharge
    bounds.extend([(0, discharge_limit)] * n)

    # Curtailment
    bounds.extend([(0, None)] * n)

    # Storage
    bounds.extend([(1200, 10800)] * (n + 1))

    # Solve

    result = linprog(
        c,
        A_eq=Aeq,
        b_eq=beq,
        bounds=bounds,
        method="highs",
    )

    if not result.success:
        raise RuntimeError(
            f"Optimization failed: {result.message}"
        )

    x = result.x

    G = x[G0:G0+n]
    E = x[E0:E0+n]
    C = x[C0:C0+n]
    D = x[D0:D0+n]
    W = x[W0:W0+n]
    S = x[S0:S0+n+1]

    normal_cost = np.sum(G * price)
    emergency_cost = np.sum(E * 5 * price)

    return {
        "planned_purchase": G,
        "emergency_purchase": E,
        "charge": C,
        "discharge": D,
        "curtailment": W,
        "storage": S,
        "normal_cost": normal_cost,
        "emergency_cost": emergency_cost,
        "total_cost": normal_cost + emergency_cost,
        "end_energy": S[-1],
        "status": result.status,
        "message": result.message,
    }