from pyroborobo import Pyroborobo
from util.config_reader import ConfigReader
from controller.base import BaseController
from monitor.swarm import SwarmFitnessMonitor
from monitor.behaviour import BehaviourMonitor

def init(_config_filename: str, _run_id: str, _start_generation: int):
  global config_filename
  global config
  global run_id
  global start_generation
  global current_generation
  global simulator
  global fitness_monitor
  global pen_behaviour_monitor
  global dog_behaviour_monitor
  global sheep_behaviour_monitor
  config_filename = _config_filename
  config = ConfigReader(_config_filename)
  run_id = _run_id
  start_generation = _start_generation
  current_generation = _start_generation
  try:
    simulator = Pyroborobo.get() 
  except:
    simulator = Pyroborobo.create(config_filename, controller_class=BaseController)
  simulator.start()
  fitness_monitor = SwarmFitnessMonitor(config.get("pSwarmFitnessAlgorithm", "str"))
  pen_behaviour_monitor = BehaviourMonitor("PEN_DISTANCE")
  dog_behaviour_monitor = BehaviourMonitor("DOG_DISTANCE")
  sheep_behaviour_monitor = BehaviourMonitor("SHEEP_DISTANCE")