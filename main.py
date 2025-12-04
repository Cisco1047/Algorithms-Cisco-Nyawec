from simulation.engine import SimulationEngine

def say_hello(engine):
    print(f"[{engine.current_time}] Hello!")

def say_bye(engine):
    print(f"[{engine.current_time}] Goodbye!")

sim = SimulationEngine()
sim.schedule(5, say_hello)
sim.schedule(2, say_bye)

sim.run()
