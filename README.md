# Bank Queue Simulation Using Discrete Event System

A Python implementation of a bank queue simulation using discrete event system principles. The simulation models a bank with random customer arrivals, multiple tellers with varying efficiency levels, and a priority-based queue system.

## Features

- **Random Customer Arrivals**: Customers arrive following an exponential distribution
- **Multiple Tellers**: Configurable number of tellers with varying efficiency levels
- **Priority Service**: VIPs, elderly customers, and those with appointments receive priority service
- **FIFO Queue**: Regular customers follow a first-come-first-served rule within the same priority level
- **Customer Abandonment**: Customers may abandon the queue if they wait too long
- **Comprehensive Statistics**: Wait times, teller workload, and abandonment rates

## Installation

No external dependencies required. Uses Python 3.7+ standard library.

```bash
# Clone the repository
git clone https://github.com/Cisco1047/Algorithms-Cisco-Nyawec.git
cd Algorithms-Cisco-Nyawec
```

## Usage

### Command Line

Run the simulation with default settings:
```bash
python main.py
```

Run with custom configuration:
```bash
# 4 tellers for 2 hours with reproducible random seed
python main.py --tellers 4 --duration 120 --seed 42

# Custom teller efficiencies
python main.py --tellers 3 --efficiencies 0.8 1.0 1.5

# Adjust arrival and service rates
python main.py --arrival-rate 3.0 --service-time 4.0

# Set queue capacity limit
python main.py --queue-capacity 20
```

### Python API

```python
from bank_simulation import Simulator, SimulationConfig, CustomerPriority

# Create custom configuration
config = SimulationConfig(
    num_tellers=4,
    teller_efficiencies=[0.8, 1.0, 1.2, 1.5],
    simulation_duration=480.0,  # 8-hour day
    mean_arrival_interval=2.0,
    mean_service_time=5.0,
    mean_patience=15.0,
    priority_distribution={
        CustomerPriority.VIP: 0.05,
        CustomerPriority.ELDERLY: 0.15,
        CustomerPriority.APPOINTMENT: 0.10,
        CustomerPriority.REGULAR: 0.70,
    },
    random_seed=42
)

# Run simulation
simulator = Simulator(config=config)
stats = simulator.run(verbose=True)

# Access statistics
print(f"Customers served: {stats.get_total_customers_served()}")
print(f"Abandonment rate: {stats.get_abandonment_rate():.2%}")
print(f"Average wait time: {stats.get_average_wait_time():.2f}")
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--tellers, -t` | Number of tellers | 3 |
| `--efficiencies, -e` | Efficiency levels for each teller | 1.0 for all |
| `--duration, -d` | Simulation duration (time units) | 480 |
| `--arrival-rate, -a` | Mean time between arrivals | 2.0 |
| `--service-time, -s` | Mean service time per customer | 5.0 |
| `--patience, -p` | Mean customer patience | 15.0 |
| `--queue-capacity, -q` | Maximum queue size | Unlimited |
| `--seed` | Random seed for reproducibility | None |
| `--vip-rate` | Proportion of VIP customers | 0.05 |
| `--elderly-rate` | Proportion of elderly customers | 0.15 |
| `--appointment-rate` | Proportion of customers with appointments | 0.10 |
| `--quiet` | Suppress verbose output | False |

## Architecture

The simulation uses a discrete event system with the following components:

### Core Classes

- **Customer**: Represents a bank customer with priority level, arrival time, patience, and service requirements
- **CustomerPriority**: Enum defining priority levels (VIP > ELDERLY > APPOINTMENT > REGULAR)
- **Teller**: Represents a bank teller with configurable efficiency
- **BankQueue**: Priority-based queue using a heap data structure
- **Bank**: Orchestrates customers, tellers, and queue operations
- **Event/EventQueue**: Discrete event system components
- **Simulator**: Main simulation engine
- **SimulationStatistics**: Collects and computes statistics

### Event Types

1. `CUSTOMER_ARRIVAL`: A new customer arrives at the bank
2. `SERVICE_START`: A teller starts serving a customer
3. `SERVICE_COMPLETE`: A teller finishes serving a customer
4. `CUSTOMER_ABANDON`: A customer abandons the queue
5. `BANK_OPEN`: The bank opens
6. `BANK_CLOSE`: The bank closes

## Running Tests

```bash
python -m unittest discover tests/ -v
```

## Example Output

```
============================================================
BANK QUEUE SIMULATION - STATISTICS REPORT
============================================================

CUSTOMER STATISTICS
----------------------------------------
  Total customers served:     53
  Total customers abandoned:  2
  Abandonment rate:           3.64%

  Customers served by priority:
    VIP: 4
    ELDERLY: 5
    APPOINTMENT: 6
    REGULAR: 38

WAIT TIME STATISTICS
----------------------------------------
  Average wait time:  3.45 time units
  Maximum wait time:  15.74 time units
  Minimum wait time:  0.00 time units

  Average wait time by priority:
    VIP: 0.03 time units
    ELDERLY: 0.53 time units
    APPOINTMENT: 0.11 time units
    REGULAR: 4.73 time units

TELLER STATISTICS
----------------------------------------
  Number of tellers:           3
  Average teller utilization:  74.59%

  Individual teller statistics:
    Teller 0 (efficiency 1.0x): utilization 76.59%, 19 customers served
    Teller 1 (efficiency 1.0x): utilization 79.04%, 18 customers served
    Teller 2 (efficiency 1.0x): utilization 68.13%, 16 customers served
============================================================
```

## License

MIT License
