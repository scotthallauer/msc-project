from util.config_reader import ConfigReader
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

def set_simulator(_simulator):
  global simulator
  global individual_fitness_monitor
  global swarm_fitness_monitor
  simulator = _simulator
  individual_fitness_monitor = IndividualFitnessMonitor(config.get("pIndividualFitnessAlgorithm", "str"))
  swarm_fitness_monitor = SwarmFitnessMonitor(config.get("pSwarmFitnessAlgorithm", "str"))

def set_population(_population):
  global population
  population = _population

def set_offspring(_offspring):
  global offspring
  offspring = _offspring