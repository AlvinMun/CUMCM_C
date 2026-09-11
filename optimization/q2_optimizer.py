
import numpy as np
from scipy.optimize import linprog


def optimize_day(price, load_kw, pv_kw, battery, initial_energy):
    """
    Optimize one day (144 time steps).

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
    dt = 1 / 6  # 10 minutes = 1/6 hour

    # Variable order
    # [Grid | Charge | Discharge | Curtail | SOC]

    G0 = 0
    C0 = G0 + n
    D0 = C0 + n
    P0 = D0 + n
    S0 = P0 + n

    total_vars = S0 + n + 1

    # Objective

    c = np.zeros(total_vars)

    # Purchase cost
    c[G0:G0 + n] = price * dt

    # Tiny penalty for curtailment
    c[P0:P0 + n] = 1e-6

    # Equality constraints

    Aeq = []
    beq = []

    eta_c = battery.charge_efficiency
    eta_d = battery.discharge_efficiency

    # Power balance

    for t in range(n):

        row = np.zeros(total_vars)

        row[G0 + t] = 1
        row[D0 + t] = 1
        row[C0 + t] = -1
        row[P0 + t] = -1

        Aeq.append(row)
        beq.append(load_kw[t] - pv_kw[t])

    # SOC dynamics

    for t in range(n):

        row = np.zeros(total_vars)

        row[S0 + t] = -1
        row[S0 + t + 1] = 1

        row[C0 + t] = -eta_c * dt
        row[D0 + t] = dt / eta_d

        Aeq.append(row)
        beq.append(0)

    # Initial SOC ONLY

    row = np.zeros(total_vars)
    row[S0] = 1

    Aeq.append(row)
    beq.append(initial_energy)

    Aeq = np.array(Aeq)
    beq = np.array(beq)

    # Inequality constraints
    # Prevent simultaneous charging/discharging

    Aub = []
    bub = []

    M = max(
        battery.max_charge_power,
        battery.max_discharge_power,
    )

    for t in range(n):

        row = np.zeros(total_vars)

        row[C0 + t] = 1
        row[D0 + t] = 1

        Aub.append(row)
        bub.append(M)

    Aub = np.array(Aub)
    bub = np.array(bub)

    # Bounds

    bounds = []

    # Grid
    bounds.extend([(0, None)] * n)

    # Charge
    bounds.extend([(0, battery.max_charge_power)] * n)

    # Discharge
    bounds.extend([(0, battery.max_discharge_power)] * n)

    # Curtailment
    bounds.extend([(0, None)] * n)

    # SOC
    soc_min = 0.10 * battery.capacity

    bounds.extend([(soc_min, battery.capacity)] * (n + 1))

    # Solve

    result = linprog(
        c,
        A_eq=Aeq,
        b_eq=beq,
        A_ub=Aub,
        b_ub=bub,
        bounds=bounds,
        method="highs",
    )

    if not result.success:
        raise RuntimeError(
            f"Optimization failed: {result.message}"
        )

    x = result.x

    grid = x[G0:G0 + n]
    charge = x[C0:C0 + n]
    discharge = x[D0:D0 + n]
    curtail = x[P0:P0 + n]
    soc = x[S0:S0 + n + 1]

    total_cost = np.sum(grid * price * dt)

    # No emergency purchase in current model
    emergency_purchase = np.zeros(n)

    return {

        "planned_purchase": grid,
        "grid_purchase": grid,
        "emergency_purchase": emergency_purchase,

        "charge": charge,
        "discharge": discharge,

        "storage": soc,
        "battery_energy": soc,

        "curtailment": curtail,

        "normal_cost": total_cost,
        "emergency_cost": 0.0,
        "total_cost": total_cost,

        "end_energy": soc[-1],

        "status": result.status,
        "message": result.message,
    }