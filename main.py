#!/usr/bin/env python3
"""
Bank Queue Simulation - Main Entry Point

This script runs a discrete event simulation of a bank queue system with:
- Random customer arrivals
- Multiple tellers with varying efficiency levels
- Priority service (VIPs, elderly, appointments)
- FIFO queue for regular customers
- Statistics tracking for wait times, teller workload, and abandonment rates

Usage:
    python main.py [options]

Example:
    python main.py --tellers 4 --duration 480 --seed 42
"""

import argparse
import sys
from bank_simulation import Simulator, SimulationConfig, CustomerPriority


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Bank Queue Simulation using Discrete Event System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    # Run with default settings (3 tellers, 8-hour day)
    python main.py

    # Run with 5 tellers for 4 hours with fixed random seed
    python main.py --tellers 5 --duration 240 --seed 42

    # Run with custom arrival and service rates
    python main.py --arrival-rate 3.0 --service-time 4.0

    # Run with queue capacity limit
    python main.py --queue-capacity 20
        '''
    )
    
    parser.add_argument(
        '--tellers', '-t',
        type=int,
        default=3,
        help='Number of tellers (default: 3)'
    )
    
    parser.add_argument(
        '--efficiencies', '-e',
        type=float,
        nargs='+',
        default=None,
        help='Efficiency levels for each teller (default: all 1.0)'
    )
    
    parser.add_argument(
        '--duration', '-d',
        type=float,
        default=480.0,
        help='Simulation duration in time units (default: 480 = 8 hours)'
    )
    
    parser.add_argument(
        '--arrival-rate', '-a',
        type=float,
        default=2.0,
        help='Mean time between customer arrivals (default: 2.0)'
    )
    
    parser.add_argument(
        '--service-time', '-s',
        type=float,
        default=5.0,
        help='Mean service time per customer (default: 5.0)'
    )
    
    parser.add_argument(
        '--patience', '-p',
        type=float,
        default=15.0,
        help='Mean customer patience/wait tolerance (default: 15.0)'
    )
    
    parser.add_argument(
        '--queue-capacity', '-q',
        type=int,
        default=None,
        help='Maximum queue capacity (default: unlimited)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Random seed for reproducibility'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress verbose output'
    )
    
    parser.add_argument(
        '--vip-rate',
        type=float,
        default=0.05,
        help='Proportion of VIP customers (default: 0.05)'
    )
    
    parser.add_argument(
        '--elderly-rate',
        type=float,
        default=0.15,
        help='Proportion of elderly customers (default: 0.15)'
    )
    
    parser.add_argument(
        '--appointment-rate',
        type=float,
        default=0.10,
        help='Proportion of customers with appointments (default: 0.10)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the simulation."""
    args = parse_args()
    
    # Validate efficiencies if provided
    if args.efficiencies is not None:
        if len(args.efficiencies) != args.tellers:
            print(f"Error: Number of efficiencies ({len(args.efficiencies)}) "
                  f"must match number of tellers ({args.tellers})")
            sys.exit(1)
    
    # Calculate regular customer rate
    priority_rates = args.vip_rate + args.elderly_rate + args.appointment_rate
    if priority_rates > 1.0:
        print("Error: Sum of priority rates cannot exceed 1.0")
        sys.exit(1)
    regular_rate = 1.0 - priority_rates
    
    # Create configuration
    config = SimulationConfig(
        num_tellers=args.tellers,
        teller_efficiencies=args.efficiencies,
        simulation_duration=args.duration,
        mean_arrival_interval=args.arrival_rate,
        mean_service_time=args.service_time,
        mean_patience=args.patience,
        queue_capacity=args.queue_capacity,
        random_seed=args.seed,
        priority_distribution={
            CustomerPriority.VIP: args.vip_rate,
            CustomerPriority.ELDERLY: args.elderly_rate,
            CustomerPriority.APPOINTMENT: args.appointment_rate,
            CustomerPriority.REGULAR: regular_rate,
        }
    )
    
    # Print configuration summary
    if not args.quiet:
        print("=" * 60)
        print("BANK QUEUE SIMULATION - CONFIGURATION")
        print("=" * 60)
        print(f"  Number of tellers:       {config.num_tellers}")
        if args.efficiencies:
            print(f"  Teller efficiencies:     {args.efficiencies}")
        print(f"  Simulation duration:     {config.simulation_duration} time units")
        print(f"  Mean arrival interval:   {config.mean_arrival_interval} time units")
        print(f"  Mean service time:       {config.mean_service_time} time units")
        print(f"  Mean customer patience:  {config.mean_patience} time units")
        if config.queue_capacity:
            print(f"  Queue capacity:          {config.queue_capacity}")
        print(f"  Random seed:             {config.random_seed or 'None (random)'}")
        print()
        print("  Priority distribution:")
        for priority, rate in config.priority_distribution.items():
            print(f"    {priority.name}: {rate:.1%}")
        print()
    
    # Create and run simulation
    simulator = Simulator(config=config)
    
    if not args.quiet:
        print("Running simulation...")
        print()
    
    stats = simulator.run(verbose=not args.quiet)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
