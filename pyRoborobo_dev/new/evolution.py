import globals
import random
import util.categorise as categorise

global evaluators 

# STEADY STATE GENETIC ALGORITHM
def ssga(individual):

  # assign same genome to all dogs
  for dog in categorise.get_dogs(globals.simulator.controllers):
    dog.controller.set_genome(individual)
  
  # run simulation
  reset_simulator()
  globals.simulator.update(globals.config.get("pSimulationLifetime", "int"))

  return globals.swarm_fitness_monitor.score(),

# N-STATE GENETIC ALGORITHM
def nsga(individual):

  # assign different genomes to all dogs
  id = 0
  dogs = categorise.get_dogs(globals.simulator.controllers)
  genomes = random.sample(globals.offspring, len(dogs)-1)
  for dog in dogs:
    if id == 0:
      dog.controller.set_genome(individual)
    else:
      dog.controller.set_genome(genomes.pop())
    id += 1
  
  # run simulation
  reset_simulator()
  globals.simulator.update(globals.config.get("pSimulationLifetime", "int"))

  return globals.swarm_fitness_monitor.score(),

# helper function to reset simulation environment
def reset_simulator():
  # reset robot positions
  for controller in globals.simulator.controllers:
    x = random.randint(0, globals.config.get("gArenaWidth", "int"))
    y = random.randint(0, globals.config.get("gArenaHeight", "int"))
    controller.set_position(x, y)

  # reset fitness monitor
  globals.swarm_fitness_monitor.reset()

# global list of evaluation algorithms
evaluators = {
  "SSGA": ssga,
  "NSGA": nsga
}