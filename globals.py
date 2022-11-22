from pyroborobo import Pyroborobo
from util.config_reader import ConfigReader
from controller.base import BaseController
from monitor.swarm import SwarmFitnessMonitor
from monitor.behaviour import BehaviourMonitor

def init(config_filename: str):
  global config
  global simulator
  global fitness_monitor
  global pen_behaviour_monitor
  global dog_behaviour_monitor
  global sheep_behaviour_monitor
  config = ConfigReader(config_filename)
  try:
    simulator = Pyroborobo.get() 
  except:
    simulator = Pyroborobo.create(config_filename, controller_class=BaseController)
  simulator.start()
  fitness_monitor = SwarmFitnessMonitor(config.get("pSwarmFitnessAlgorithm", "str"))
  pen_behaviour_monitor = BehaviourMonitor("PEN_DISTANCE")
  dog_behaviour_monitor = BehaviourMonitor("DOG_DISTANCE")
  sheep_behaviour_monitor = BehaviourMonitor("SHEEP_DISTANCE")