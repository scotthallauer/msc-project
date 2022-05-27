from pyroborobo import Pyroborobo, Controller
from config_reader import ConfigReader
from cattle_controller import CattleController
from shepherd_controller import ShepherdController
from fitness_monitor import FitnessMonitor
import functions.categorise as categorise
from scipy.stats import rankdata
import numpy as np
import random


FITNESS_P = 0
FITNESS_T = 0
GENERATIONS = 10
T_MAX = 5000
TIME_STEP = 0


class AgentController(Controller):

  config_filename = "config/herd.properties"

  def __init__(self, world_model):
    Controller.__init__(self, world_model) # mandatory call to super constructor
    self.instance = Pyroborobo.get()
    self.config = ConfigReader(AgentController.config_filename)
    if categorise.is_shepherd(self.get_id(), self.config.get("pMaxRobotNumber", "int")):
      self.controller = ShepherdController(self)
    else:
      self.controller = CattleController(self)

  def monitor_swarm_fitness(self):
    global FITNESS_P, FITNESS_T, TIME_STEP, T_MAX
    gathered_cattle = 0
    total_cattle = 0
    for robot in self.instance.controllers:
      if categorise.is_cattle(robot.get_id(), robot.config.get("pMaxRobotNumber", "int")):
        total_cattle += 1
        if categorise.in_target_zone(robot):
          gathered_cattle += 1
    new_p = gathered_cattle / total_cattle * 100
    if FITNESS_P < new_p:
      FITNESS_P = new_p
      FITNESS_T = TIME_STEP

  def get_swarm_fitness(self):
    return ((FITNESS_P / 100) + ((T_MAX - FITNESS_T) / T_MAX)) / 2

  def reset(self):
    self.controller.reset()

  def step(self):  # step is called at each time step
    global TIME_STEP, FITNESS
    if self.get_id() == 1:
      TIME_STEP += 1
      self.monitor_swarm_fitness()
    self.controller.step(FITNESS)


def get_weights(rob):
  weights = []
  controllers = [c for c in rob.controllers if categorise.is_shepherd(c.get_id(), c.config.get("pMaxRobotNumber", "int"))]
  for controller in controllers:
    weights.append(controller.controller.get_flat_weights())
  return weights

def get_fitnesses(rob, monitor):
  fitnesses = []
  controllers = [c for c in rob.controllers if categorise.is_shepherd(c.get_id(), c.config.get("pMaxRobotNumber", "int"))]
  for controller in controllers:
    fitnesses.append(monitor.score(controller))
  return fitnesses

def fitprop(weights, fitnesses):
  adjust_fit = rankdata(fitnesses)
  # adjust_fit = np.clip(fitnesses, 0.00001, None)
  normfit = adjust_fit / np.sum(adjust_fit)
  # select
  new_weights_i = np.random.choice(len(weights), len(weights), replace=True, p=normfit)
  new_weights = np.asarray(weights)[new_weights_i]
  # mutate
  new_weights_mutate = np.random.normal(new_weights, 0.01)
  return new_weights_mutate

def apply_weights(rob, weights):
  controllers = [c for c in rob.controllers if categorise.is_shepherd(c.get_id(), c.config.get("pMaxRobotNumber", "int"))]
  for controller, weight in zip(controllers, weights):
    controller.controller.set_weights(weight)

def reset_positions(rob):
  for controller in rob.controllers:
    controller.set_position(random.randint(0, controller.config.get("gArenaWidth", "int")), random.randint(0, controller.config.get("gArenaHeight", "int")))

if __name__ == "__main__":
  rob = Pyroborobo.create(AgentController.config_filename, controller_class=AgentController)
  rob.start()
  config = ConfigReader(AgentController.config_filename)
  landmark = rob.add_landmark()
  landmark.radius = config.get("pTargetZoneRadius", "int")
  landmark.set_coordinates(config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int"))
  landmark.show()
  FITNESS = FitnessMonitor(
    rob.controllers, 
    [config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int")], 
    config.get("pTargetZoneRadius", "int"), 
    config.get("cShepherdAvoidanceRadius", "float"), 
    config.get("pMaxRobotNumber", "int")
  )
  for gen in range(GENERATIONS):
    print("*" * 10, gen, "*" * 10)
    stop = rob.update(T_MAX)
    if stop:
      break
    weights = get_weights(rob)
    fitnesses = get_fitnesses(rob, FITNESS)
    new_weights = fitprop(weights, fitnesses)
    apply_weights(rob, new_weights)
    reset_positions(rob)
    FITNESS.reset()
  rob.close()
