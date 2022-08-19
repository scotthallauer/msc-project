from pyroborobo import Pyroborobo, Controller
from config_reader import ConfigReader
from controller.shepherd import ShepherdController
from controller.cattle import CattleController
from individual_fitness_monitor import IndividualFitnessMonitor
from swarm_fitness_monitor import SwarmFitnessMonitor
from evolution_manager import EvolutionManager
from result_logger import ResultLogger
from checkpoint_manager import CheckpointManager
import functions.categorise as categorise
import random
import sys
from time import time


class AgentController(Controller):

  def __init__(self, world_model):
    global CONFIG_FILENAME
    Controller.__init__(self, world_model) # mandatory call to super constructor
    self.instance = Pyroborobo.get()
    self.config = ConfigReader(CONFIG_FILENAME)
    if categorise.is_shepherd(self.get_id(), self.config.get("pRobotNumber", "int")):
      self.controller = ShepherdController(self)
    else:
      self.controller = CattleController(self)

  def reset(self):
    self.controller.reset()

  def step(self):  # step is called at each time step
    global i_fitness_monitor, s_fitness_monitor
    if self.get_id() == 1:
      s_fitness_monitor.track()
    self.controller.step(i_fitness_monitor)


# RUN SIMULATION
if __name__ == "__main__":

  # load command-line parameters
  try:
    RUN_TYPE = "resume" if sys.argv[1] == "-r" else "start"
    if RUN_TYPE == "resume":
      CHECKPOINT_FILENAME = sys.argv[3]
      CHECKPOINT_GENERATION = int(sys.argv[4])
    CONFIG_FILENAME = sys.argv[2]
  except:
    print("*" * 10, "Usage Instructions", "*" * 10)
    print("Start Simulation:\tpython herd.py -s <config file>")
    print("Resume Simulation:\tpython herd.py -r <config file> <checkpoint file> <generation number>")
    exit(1)

  # load config and start simulator
  run_id = str(int(time()))
  config = ConfigReader(CONFIG_FILENAME)
  simulator = Pyroborobo.create(CONFIG_FILENAME, controller_class=AgentController)
  simulator.start()

  # add target zone to environment
  target_zone = simulator.add_landmark()
  target_zone.radius = config.get("pTargetZoneRadius", "int")
  target_zone.set_coordinates(config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int"))
  target_zone.show()

  # create evolution manager, checkpoint manager, fitness monitors and result loggers
  evolution_manager = EvolutionManager(config.get("pEvolutionAlgorithm", "str"), config, simulator.controllers[0].controller.get_dimensions())
  checkpoint_manager = CheckpointManager(run_id, simulator.controllers)
  i_fitness_monitor = IndividualFitnessMonitor(config.get("pIndividualFitnessAlgorithm", "str"), config, simulator.controllers)
  s_fitness_monitor = SwarmFitnessMonitor(config.get("pSwarmFitnessAlgorithm", "str"), config, simulator.controllers)
  fitness_logger = ResultLogger(run_id, "fitness", ["generation", "swarm fitness", "robot fitness"])

  # run all generation simulations
  for generation in range(config.get("pSimulationGenerations", "int")):
    print("*" * 10, generation, "*" * 10)

    # select and apply new genomes
    genomes = evolution_manager.select(config.get("pRobotNumber", "int"))
    shepherds = categorise.get_shepherds(simulator.controllers)
    for shepherd, genome in zip(shepherds, genomes):
      shepherd.controller.set_genome(genome)

    # run single generation simulation
    stop = simulator.update(config.get("pSimulationLifetime", "int"))
    if stop:
      break

    # update genome fitness
    evolution_manager.assess(genomes[0].get_id(), s_fitness_monitor.score())
    #shepherds = [c for c in simulator.controllers if categorise.is_shepherd(c.get_id(), config.get("pRobotNumber", "int"))]
    #for shepherd in shepherds:
      #EVOLUTION_MANAGER.assess(shepherd.controller.get_genome().get_id(), SWARM_FITNESS.score())
      #EVOLUTION_MANAGER.assess(shepherd.controller.get_genome().get_id(), INDIVIDUAL_FITNESS.score(shepherd))

    # propagate new genomes
    evolution_manager.propagate()

    # log and print generation results
    fitness_logger.append([generation, s_fitness_monitor.score(), i_fitness_monitor.avg_score()])
    evolution_manager.report()
    i_fitness_monitor.report()
    s_fitness_monitor.report()

    # save checkpoint every 10 generations
    if generation % 10 == 0:
      checkpoint_manager.save(generation)

    # reset agent positions and fitness
    i_fitness_monitor.reset()
    s_fitness_monitor.reset()
    for controller in simulator.controllers:
      controller.set_position(random.randint(0, controller.config.get("gArenaWidth", "int")), random.randint(0, controller.config.get("gArenaHeight", "int")))

  simulator.close()
