import globals
import random
import util.calculate as calculate
import util.categorise as categorise

global evaluators 

# STEADY STATE GENETIC ALGORITHM
def ssga(individual):

  # assign same genome to all dogs
  for dog in categorise.get_dogs():
    dog.controller.set_genome(individual)
  
  # run simulation
  reset_simulator()
  globals.simulator.update(globals.config.get("pSimulationLifetime", "int"))
  globals.current_evaluations += 1
  print("Progress: " + str(int((globals.current_evaluations / globals.total_evaluations) * 100.0)) + "%", end="\r", flush=True)

  return globals.swarm_fitness_monitor.score(),

# N-STATE GENETIC ALGORITHM
def nsga(individual):

  # assign different genomes to all dogs
  id = 0
  dogs = categorise.get_dogs()
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
  globals.current_evaluations += 1
  print("Progress: " + str(int((globals.current_evaluations / globals.total_evaluations) * 100.0)) + "%", end="\r", flush=True)

  return globals.swarm_fitness_monitor.score(),

# helper function to reset simulation environment
def reset_simulator():

  # reset robot positions
  for controller in globals.simulator.controllers:
    padding = 20 # distance from sides of arena to avoid placing robots inside walls
    arena_width = globals.config.get("gArenaWidth", "int")
    arena_height = globals.config.get("gArenaHeight", "int")
    target_coords = [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")]
    target_radius = globals.config.get("pTargetZoneRadius", "int")
    target_spawning = globals.config.get("pTargetZoneSpawning", "bool")
    while True:
      x = random.randint(padding, arena_width - padding)
      y = random.randint(padding, arena_height - padding)
      if target_spawning or calculate.distance_from_target_zone([x, y], target_coords, target_radius) > 0:
        controller.set_position(x, y)
        break

  # reset monitors
  globals.swarm_fitness_monitor.reset()
  globals.zone_behaviour_monitor.reset()
  globals.dog_behaviour_monitor.reset()
  globals.sheep_behaviour_monitor.reset()

# global list of evaluation algorithms
evaluators = {
  "SSGA": ssga,
  "NSGA": nsga
}