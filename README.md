# CUMCM 2026 – Problem C: Microgrid Electricity Purchase Optimization with Energy Storage

A complete Python implementation of **CUMCM 2026 National Mathematical Modeling Competition – Problem C**, covering deterministic scheduling, annual optimization, rolling forecast adjustment, and real-time electricity price optimization for a photovoltaic microgrid with battery storage.

## Project Overview

This project studies optimal electricity purchasing strategies for a microgrid equipped with:

* Residential load demand
* Photovoltaic (PV) generation
* Battery energy storage system (BESS)
* Time-of-use and real-time electricity pricing

The objective is to minimize electricity purchasing costs while satisfying load demand, battery operating constraints, and forecast updates.

The implementation reproduces the optimization framework required by the competition and automatically generates Excel result files and publication-ready figures.

---

## Project Structure

```text
CUMCM_C/
│
├── data/
│   ├── 附件1.xlsx
│   ├── 附件2.xlsx
│   ├── 附件3.xlsx
│   ├── 附件4.xlsx
│   └── generated result files
│
├── optimization/
│   ├── q1_optimizer.py
│   ├── q2_optimizer.py
│   ├── q3_optimizer.py
│   ├── q4_optimizer.py
│   └── q4_rolling_optimizer.py
│
├── utils/
│   ├── data_loader.py
│   ├── battery.py
│   ├── q1_plotting.py
│   ├── q2_plotting.py
│   ├── q3_plotting.py
│   └── plots.py
│
├── figures/
│   └── generated figures
│
├── results/
│   └── exported Excel results
│
├── paper/
│   ├── main.tex
│   ├── references.bib
│   └── sections/
│
├── main_q1.py
├── main_q2.py
├── main_q3.py
├── main_q4_2.py
├── main_q4_3.py
└── requirements.txt
```

---

## Mathematical Models

### Problem 1

* Linear Programming (SciPy HiGHS)
* Battery SOC constraints
* Charging/discharging efficiency
* Minimum daily electricity purchase cost

### Problem 2

* Annual day-by-day optimization
* Continuous battery state transfer
* PV curtailment handling
* Emergency purchase framework

### Problem 3

* Rolling forecast optimization
* Four forecast updates (00:00, 06:00, 12:00, 18:00)
* Plan adjustment cost
* Dynamic battery scheduling

### Problem 4

* Real-time electricity price optimization
* Dynamic electricity pricing
* Annual optimization
* Rolling optimization with price fluctuations

---

## Battery Configuration

| Parameter               |     Value |
| ----------------------- | --------: |
| Capacity                | 12000 kWh |
| Initial SOC             |  6000 kWh |
| Maximum Charge Power    |   5000 kW |
| Maximum Discharge Power |   5000 kW |
| Charge Efficiency       |       90% |
| Discharge Efficiency    |       90% |
| Minimum SOC             |  1200 kWh |

---

## Main Results

### Problem 1

| Metric         |           Result |
| -------------- | ---------------: |
| Daily Cost     |   **35126.95 元** |
| Daily Purchase | **59482.70 kWh** |
| Final SOC      |     **6000 kWh** |

### Problem 2

| Metric           |           Result |
| ---------------- | ---------------: |
| Annual Cost      | **13,768,401 元** |
| Planned Purchase |    **22.69 GWh** |
| PV Curtailment   |      **733 MWh** |

### Problem 3

| Metric          |             Result |
| --------------- | -----------------: |
| Annual Cost     |   **23,574,822 元** |
| Adjustment Cost | **8.13 million 元** |

### Problem 4-2

| Metric      |           Result |
| ----------- | ---------------: |
| Annual Cost | **14,235,646 元** |

### Problem 4-3

| Metric          |             Result |
| --------------- | -----------------: |
| Annual Cost     |   **24,539,300 元** |
| Adjustment Cost | **8.30 million 元** |

---

## Example Figures

The project automatically generates figures such as:

* Battery SOC curves
* Typical seasonal dispatch
* Annual electricity purchase statistics
* Rolling forecast updates
* Monthly adjustment distributions
* Cost comparison charts

Example outputs:

* `图1_电池荷电状态变化曲线.png`
* `图2-5a_全年每日购电成本.png`
* `图3-2_月度调整费用分布.png`
* `图4-4_四种策略全年成本比较.png`

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/CUMCM_C.git
cd CUMCM_C
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run each problem independently.

### Problem 1

```bash
python main_q1.py
```

### Problem 2

```bash
python main_q2.py
```

### Problem 3

```bash
python main_q3.py
```

### Problem 4-2

```bash
python main_q4_2.py
```

### Problem 4-3

```bash
python main_q4_3.py
```

Generated outputs will be saved automatically.

---

## Dependencies

* Python 3.11+
* NumPy
* Pandas
* SciPy
* Matplotlib
* OpenPyXL

---

## Technical Highlights

* Linear Programming with SciPy HiGHS
* Rolling horizon optimization
* Battery state-of-charge modeling
* PV forecast integration
* Automatic Excel report generation
* Publication-ready figure generation
* Modular project architecture

---

## Notes

This repository is an independent implementation based on the official CUMCM Problem C dataset and requirements.

The optimization models were implemented using Python and reproduce the scheduling framework described in the competition problem statement while generating reproducible numerical results and visualizations.
