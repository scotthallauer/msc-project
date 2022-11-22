from multiprocessing import Process
import util.calculate as calculate
import util.categorise as categorise
import globals
import random

class HomogenousEvaluator(Process):

  def __init__(self, config_filename: str, individual: list):
    Process.__init__(self)
    self.config_filename = config_filename
    self.individual = individual

  def run(self):
    globals.init(self.config_filename)
    fitness = self.__evaluate()
    globals.simulator.close()
    return fitness

  def __assign(self):
    for dog in categorise.get_dogs():
      dog.controller.set_genome(self.individual)

  def __evaluate(self):
    self.__assign()
    trial_scores = []
    for _ in range(globals.config.get("pEvaluationTrials", "int")):
      self.__reset()
      globals.simulator.update(globals.config.get("pSimulationLifetime", "int"))
      trial_scores.append(globals.fitness_monitor.score())
    return sum(trial_scores) / len(trial_scores)

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