from util.config_reader import ConfigReader
from util.result_logger import ResultLogger
from fitness.individual_monitor import IndividualFitnessMonitor
from fitness.swarm_monitor import SwarmFitnessMonitor
from time import time

def init(_config_filename):
  global run_id
  global config_filename
  global config
  global fitness_logger
  run_id = str(int(time()))
  config_filename = _config_filename
  config = ConfigReader(_config_filename)
  fitness_logger = ResultLogger(run_id, "fitness", ["generation", "swarm fitness", "individual fitness"])

def set_simulator(_simulator):
  global individual_fitness_monitor
  global swarm_fitness_monitor
  individual_fitness_monitor = IndividualFitnessMonitor(config.get("pIndividualFitnessAlgorithm", "str"), _simulator.controllers)
  swarm_fitness_monitor = SwarmFitnessMonitor(config.get("pSwarmFitnessAlgorithm", "str"), _simulator.controllers)