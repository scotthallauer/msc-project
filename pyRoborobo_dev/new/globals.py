from util.config_reader import ConfigReader
from util.result_logger import ResultLogger
from monitor.individual import IndividualFitnessMonitor
from monitor.swarm import SwarmFitnessMonitor

def init(_config_filename, _run_id):
  global run_id
  global config_filename
  global config
  global fitness_logger
  run_id = _run_id
  config_filename = _config_filename
  config = ConfigReader(_config_filename)
  fitness_logger = ResultLogger("fitness", ["generation", "average fitness", "max fitness"])

def set_simulator(_simulator):
  global simulator
  global controllers
  global individual_fitness_monitor
  global swarm_fitness_monitor
  simulator = _simulator
  controllers = _simulator.controllers
  individual_fitness_monitor = IndividualFitnessMonitor(config.get("pIndividualFitnessAlgorithm", "str"), _simulator.controllers)
  swarm_fitness_monitor = SwarmFitnessMonitor(config.get("pSwarmFitnessAlgorithm", "str"), _simulator.controllers)