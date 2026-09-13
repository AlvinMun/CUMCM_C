import numpy as np

from optimization.q2_optimizer import optimize_day

DT = 1 / 6


def optimize_day_q3(
    price,
    load_kw,
    pv_actual_kw,
    forecasts,
    battery,
    initial_energy,
):
    """
    Question 3 rolling optimization.

    Rolling update times:
        0:00 (initial plan)
        6:00
        12:00
        18:00

    Returns:
        initial planned purchase
        adjusted purchase
        adjustment cost
        battery trajectories
    """

    # --------------------------------------------------
    # Initial optimization (0:00 forecast)
    # --------------------------------------------------

    plan = optimize_day(
        price=price,
        load_kw=load_kw,
        pv_kw=forecasts["0:00"],
        battery=battery,
        initial_energy=initial_energy,
    )

    planned_purchase = plan["planned_purchase"].copy()
    final_purchase = planned_purchase.copy()

    charge = plan["charge"].copy()
    discharge = plan["discharge"].copy()
    storage = plan["storage"].copy()
    emergency = plan["emergency_purchase"].copy()
    curtailment = plan["curtailment"].copy()

    adjustment_cost = 0.0

    # Rolling update starting indices
    updates = [
        ("6:00", 36),
        ("12:00", 72),
        ("18:00", 108),
    ]

    # --------------------------------------------------
    # Rolling optimization
    # --------------------------------------------------

    for release, start in updates:

        current_soc = storage[start]

        remain = optimize_day(
            price=price[start:],
            load_kw=load_kw[start:],
            pv_kw=forecasts[release][start:],
            battery=battery,
            initial_energy=current_soc,
        )

        new_purchase = remain["planned_purchase"]

        # Difference from previous plan
        diff = new_purchase - final_purchase[start:]

        increase = np.maximum(diff, 0)
        decrease = np.maximum(-diff, 0)

        # --------------------------------------------------
        # FIXED adjustment cost
        # Electricity itself is already counted in normal_cost.
        # Only charge the additional adjustment penalty.
        # --------------------------------------------------

        adjustment_cost += (
            (0.5 * price[start:] * increase * DT).sum()
            + (0.5 * price[start:] * decrease * DT).sum()
        )

        # Update future schedule
        final_purchase[start:] = new_purchase
        charge[start:] = remain["charge"]
        discharge[start:] = remain["discharge"]
        emergency[start:] = remain["emergency_purchase"]
        curtailment[start:] = remain["curtailment"]
        storage[start:] = remain["storage"]

    # --------------------------------------------------
    # Cost calculation
    # --------------------------------------------------

    normal_cost = (price * final_purchase * DT).sum()

    emergency_cost = (5 * price * emergency * DT).sum()

    total_cost = (
        normal_cost
        + adjustment_cost
        + emergency_cost
    )

    return {
        "planned_purchase": planned_purchase,
        "adjusted_purchase": final_purchase,
        "charge": charge,
        "discharge": discharge,
        "storage": storage,
        "emergency_purchase": emergency,
        "curtailment": curtailment,
        "normal_cost": normal_cost,
        "adjustment_cost": adjustment_cost,
        "emergency_cost": emergency_cost,
        "total_cost": total_cost,
        "end_energy": storage[-1],
    }