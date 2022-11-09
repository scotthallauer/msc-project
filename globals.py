from util.config_reader import ConfigReader
from monitor.interaction import InteractionMonitor
from monitor.behaviour import BehaviourMonitor
from monitor.individual import IndividualFitnessMonitor
from monitor.swarm import SwarmFitnessMonitor

def init(_config_filename: str, _run_id: str):
  global run_id
  global config_filename
  global config
  run_id = _run_id
  config_filename = _config_filename
  config = ConfigReader(_config_filename)

def set_simulator(_simulator):
  global simulator
  global ds_interaction_monitor
  global zone_behaviour_monitor
  global dog_behaviour_monitor
  global sheep_behaviour_monitor
  global individual_fitness_monitor
  global swarm_fitness_monitor
  simulator = _simulator
  ds_interaction_monitor = InteractionMonitor("DOG_SHEEP")
  zone_behaviour_monitor = BehaviourMonitor("ZONE_DISTANCE")
  dog_behaviour_monitor = BehaviourMonitor("DOG_DISTANCE")
  sheep_behaviour_monitor = BehaviourMonitor("SHEEP_DISTANCE")
  individual_fitness_monitor = IndividualFitnessMonitor(config.get("pIndividualFitnessAlgorithm", "str"))
  swarm_fitness_monitor = SwarmFitnessMonitor(config.get("pSwarmFitnessAlgorithm", "str"))

def set_population(_population):
  global population
  population = _population

def set_offspring(_offspring):
  global offspring
  offspring = _offspring