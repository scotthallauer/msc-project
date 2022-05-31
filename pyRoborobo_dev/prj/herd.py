from pyroborobo import Pyroborobo, Controller
from config_reader import ConfigReader
from cattle_controller import CattleController
from shepherd_controller import ShepherdController
from robot_fitness_monitor import RobotFitnessMonitor
from swarm_fitness_monitor import SwarmFitnessMonitor
import functions.categorise as categorise
from scipy.stats import rankdata
import numpy as np
import random


GENERATIONS = 1000
T_MAX = 500


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

  def reset(self):
    self.controller.reset()

  def step(self):  # step is called at each time step
    global ROBOT_FITNESS, SWARM_FITNESS
    if self.get_id() == 1:
      SWARM_FITNESS.track()
    self.controller.step(ROBOT_FITNESS)


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
  ROBOT_FITNESS = RobotFitnessMonitor(
    rob.controllers, 
    [config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int")], 
    config.get("pTargetZoneRadius", "int"), 
    config.get("cShepherdAvoidanceRadius", "float"), 
    config.get("pMaxRobotNumber", "int")
  )
  SWARM_FITNESS = SwarmFitnessMonitor(
    rob.controllers, 
    [config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int")], 
    config.get("pTargetZoneRadius", "int"),
    config.get("pMaxRobotNumber", "int"),
    config.get("pMaxCattleNumber", "int"),
    T_MAX
  )
  for gen in range(GENERATIONS):
    print("*" * 10, gen, "*" * 10)
    stop = rob.update(T_MAX)
    if stop:
      break
    weights = get_weights(rob)
    fitnesses = get_fitnesses(rob, ROBOT_FITNESS)
    new_weights = fitprop(weights, fitnesses)
    apply_weights(rob, new_weights)
    reset_positions(rob)
    ROBOT_FITNESS.report()
    SWARM_FITNESS.report()
    ROBOT_FITNESS.reset()
    SWARM_FITNESS.reset()
  rob.close()
