import globals
import random
import util.categorise as categorise

def ssga(individual):

  # reset robot positions
  for controller in globals.simulator.controllers:
    x = random.randint(0, globals.config.get("gArenaWidth", "int"))
    y = random.randint(0, globals.config.get("gArenaHeight", "int"))
    controller.set_position(x, y)

  # reset fitness monitor
  globals.swarm_fitness_monitor.reset()

  # assign same genome to all dogs
  for dog in categorise.get_dogs(globals.simulator.controllers):
    dog.controller.set_genome(individual)
  
  # run simulation
  globals.simulator.update(globals.config.get("pSimulationLifetime", "int"))

  return globals.swarm_fitness_monitor.score(),