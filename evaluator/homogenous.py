from multiprocessing import Process
from util.suppress import suppressor
import util.calculate as calculate
import util.categorise as categorise
import globals
import random

class HomogenousEvaluator(Process):

  def __init__(self, id: int, config_filename: str, run_id: str, start_generation: int, individuals: list, process_output: dict):
    Process.__init__(self)
    self.id = id
    self.config_filename = config_filename
    self.run_id = run_id
    self.start_generation = start_generation
    self.individuals = individuals
    self.process_output = process_output

  def run(self):
    self.process_output[self.id] = []
    with suppressor():
      globals.init(self.config_filename, self.run_id, self.start_generation)
      for individual in self.individuals:
        self.process_output[self.id] = self.process_output[self.id] + [self.__evaluate(individual)]
      globals.simulator.close()

  def __evaluate(self, individual):
    for dog in categorise.get_dogs():
      dog.controller.set_genome(individual)
    trial_scores = []
    for _ in range(globals.config.get("pEvaluationTrials", "int")):
      self.__reset()
      globals.simulator.update(globals.config.get("pSimulationLifetime", "int"))
      trial_scores.append(globals.fitness_monitor.score())
    return (sum(trial_scores) / len(trial_scores)),

  def __reset(self):
    # reset robot positions
    for controller in globals.simulator.controllers:
      padding = 20 # distance from sides of arena to avoid placing robots inside walls
      arena_width = globals.config.get("gArenaWidth", "int")
      arena_height = globals.config.get("gArenaHeight", "int")
      pen_coords = [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")]
      pen_radius = globals.config.get("pTargetZoneRadius", "int")
      pen_spawning = globals.config.get("pTargetZoneSpawning", "bool")
      while True:
        x = random.randint(padding, arena_width - padding)
        y = random.randint(padding, arena_height - padding)
        if pen_spawning or calculate.distance_from_target_zone([x, y], pen_coords, pen_radius) > 0:
          controller.set_position(x, y)
          break
    # reset monitors
    globals.fitness_monitor.reset()
    globals.pen_behaviour_monitor.reset()
    globals.dog_behaviour_monitor.reset()
    globals.sheep_behaviour_monitor.reset()