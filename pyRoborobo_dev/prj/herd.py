from pyroborobo import Pyroborobo, Controller
from config_reader import ConfigReader
from cattle_controller import CattleController
from shepherd_controller import ShepherdController
from robot_fitness_monitor import RobotFitnessMonitor1, RobotFitnessMonitor2, RobotFitnessMonitor3
from swarm_fitness_monitor import SwarmFitnessMonitor
from result_logger import ResultLogger
from checkpoint_manager import CheckpointManager
import functions.categorise as categorise
from scipy.stats import rankdata
import numpy as np
import random
from time import time


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
  shepherds = categorise.get_shepherds(rob.controllers)
  for shepherd in shepherds:
    weights.append(shepherd.controller.get_flat_weights())
  return weights

def get_fitnesses(rob, monitor):
  fitnesses = []
  shepherds = categorise.get_shepherds(rob.controllers)
  for shepherd in shepherds:
    fitnesses.append(monitor.score(shepherd))
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
  shepherds = categorise.get_shepherds(rob.controllers)
  for shepherd, weight in zip(shepherds, weights):
    shepherd.controller.set_weights(weight)

def reset_positions(rob):
  for controller in rob.controllers:
    controller.set_position(random.randint(0, controller.config.get("gArenaWidth", "int")), random.randint(0, controller.config.get("gArenaHeight", "int")))

if __name__ == "__main__":
  id = str(int(time())) + "#" + str(random.randint(1000, 9999))
  rob = Pyroborobo.create(AgentController.config_filename, controller_class=AgentController)
  rob.start()
  config = ConfigReader(AgentController.config_filename)
  landmark = rob.add_landmark()
  landmark.radius = config.get("pTargetZoneRadius", "int")
  landmark.set_coordinates(config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int"))
  landmark.show()
  ROBOT_FITNESS = RobotFitnessMonitor3(
    rob.controllers, 
    [config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int")], 
    config.get("pTargetZoneRadius", "int"), 
    config.get("cShepherdAvoidanceRadius", "float"), 
    config.get("pMaxRobotNumber", "int")
  )
  SWARM_FITNESS = SwarmFitnessMonitor("CROWD", config, rob.controllers)
  #FITNESS_LOGGER = ResultLogger(id, "fitness", ["generation", "swarm fitness", "robot fitness"])
  #CHECKPOINT_MANAGER = CheckpointManager(id, rob.controllers)
  for gen in range(config.get("pSimulationGenerations", "int")):
    print("*" * 10, gen, "*" * 10)
    stop = rob.update(config.get("pSimulationLifetime", "int"))
    if stop:
      break
    weights = get_weights(rob)
    fitnesses = get_fitnesses(rob, ROBOT_FITNESS)
    new_weights = fitprop(weights, fitnesses)
    apply_weights(rob, new_weights)
    reset_positions(rob)
    ROBOT_FITNESS.report()
    SWARM_FITNESS.report()
    #FITNESS_LOGGER.append([gen, SWARM_FITNESS.score(), ROBOT_FITNESS.avg_score()])
    #if gen % 10 == 0:
    #  CHECKPOINT_MANAGER.save(gen)
    ROBOT_FITNESS.reset()
    SWARM_FITNESS.reset()
  rob.close()
