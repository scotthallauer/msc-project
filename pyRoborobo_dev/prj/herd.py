from pyroborobo import Pyroborobo, Controller
from config_reader import ConfigReader
from cattle_controller import CattleController
from shepherd_controller import ShepherdController
from individual_fitness_monitor import IndividualFitnessMonitor
from swarm_fitness_monitor import SwarmFitnessMonitor
from evolution_manager import EvolutionManager
from result_logger import ResultLogger
from checkpoint_manager import CheckpointManager
import functions.categorise as categorise
import random
from time import time


class AgentController(Controller):

  config_filename = "config/herd.properties"

  def __init__(self, world_model):
    Controller.__init__(self, world_model) # mandatory call to super constructor
    self.instance = Pyroborobo.get()
    self.config = ConfigReader(AgentController.config_filename)
    if categorise.is_shepherd(self.get_id(), self.config.get("pRobotNumber", "int")):
      self.controller = ShepherdController(self)
    else:
      self.controller = CattleController(self)

  def reset(self):
    self.controller.reset()

  def step(self):  # step is called at each time step
    global INDIVIDUAL_FITNESS, SWARM_FITNESS
    if self.get_id() == 1:
      SWARM_FITNESS.track()
    self.controller.step(INDIVIDUAL_FITNESS)


def apply_genomes(rob, genomes):
  shepherds = categorise.get_shepherds(rob.controllers)
  for shepherd, genome in zip(shepherds, genomes):
    shepherd.controller.set_genome(genome)

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
  INDIVIDUAL_FITNESS = IndividualFitnessMonitor("SUPDST", config, rob.controllers)
  SWARM_FITNESS = SwarmFitnessMonitor("DWELL", config, rob.controllers)
  EVOLUTION_MANAGER = EvolutionManager("SSGA", config, rob.controllers[0].controller.get_dimensions())
  #FITNESS_LOGGER = ResultLogger(id, "fitness", ["generation", "swarm fitness", "robot fitness"])
  #CHECKPOINT_MANAGER = CheckpointManager(id, rob.controllers)
  for gen in range(config.get("pSimulationGenerations", "int")):
    print("*" * 10, gen, "*" * 10)
    genomes = EVOLUTION_MANAGER.select(config.get("pRobotNumber", "int"))
    apply_genomes(rob, genomes)
    stop = rob.update(config.get("pSimulationLifetime", "int"))
    if stop:
      break
    EVOLUTION_MANAGER.assess(genomes[0].get_id(), SWARM_FITNESS.score())
    EVOLUTION_MANAGER.propagate()
    EVOLUTION_MANAGER.report()
    reset_positions(rob)
    #INDIVIDUAL_FITNESS.report()
    #SWARM_FITNESS.report()
    #FITNESS_LOGGER.append([gen, SWARM_FITNESS.score(), INDIVIDUAL_FITNESS.avg_score()])
    #if gen % 10 == 0:
    #  CHECKPOINT_MANAGER.save(gen)
    INDIVIDUAL_FITNESS.reset()
    SWARM_FITNESS.reset()
  rob.close()
