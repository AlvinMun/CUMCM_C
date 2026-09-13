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

    Forecast release times:
        00:00
        06:00
        12:00
        18:00

    Official pricing rules:
        Cancel planned purchase   -> 50% of electricity price
        Increase purchase         -> 1.5× electricity price
        Emergency purchase        -> 5× electricity price
    """


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

    updates = [
        ("6:00", 36),
        ("12:00", 72),
        ("18:00", 108),
    ]


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

        old_plan = final_purchase[start:]

        increase = np.maximum(new_purchase - old_plan, 0)
        decrease = np.maximum(old_plan - new_purchase, 0)

        adjustment_cost += np.sum(
            1.5 * price[start:] * increase * DT
            + 0.5 * price[start:] * decrease * DT
        )

        # Update future schedule

        final_purchase[start:] = new_purchase
        charge[start:] = remain["charge"]
        discharge[start:] = remain["discharge"]
        emergency[start:] = remain["emergency_purchase"]
        curtailment[start:] = remain["curtailment"]

        storage[start:] = remain["storage"]


    normal_cost = np.sum(price * planned_purchase * DT)

    emergency_cost = np.sum(5 * price * emergency * DT)

    total_cost = normal_cost + adjustment_cost + emergency_cost

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