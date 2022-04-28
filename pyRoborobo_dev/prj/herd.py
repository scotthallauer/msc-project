from pyroborobo import Pyroborobo, Controller
from config_reader import ConfigReader
from cattle_controller import CattleController
from shepherd_controller import ShepherdController
from fitness_monitor import FitnessMonitor
import functions.categorise as categorise


FITNESS_P = 0
FITNESS_T = 0
GENERATIONS = 10
T_MAX = 5000
TIME_STEP = 0


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

  def monitor_swarm_fitness(self):
    global FITNESS_P, FITNESS_T, TIME_STEP, T_MAX
    gathered_cattle = 0
    total_cattle = 0
    for robot in self.instance.controllers:
      if categorise.is_cattle(robot.get_id(), robot.config.get("pMaxRobotNumber", "int")):
        total_cattle += 1
        if categorise.in_target_zone(robot):
          gathered_cattle += 1
    new_p = gathered_cattle / total_cattle * 100
    if FITNESS_P < new_p:
      FITNESS_P = new_p
      FITNESS_T = TIME_STEP

  def get_swarm_fitness(self):
    return ((FITNESS_P / 100) + ((T_MAX - FITNESS_T) / T_MAX)) / 2

  def reset(self):
    self.controller.reset()

  def step(self):  # step is called at each time step
    global TIME_STEP, FITNESS
    if self.get_id() == 1:
      TIME_STEP += 1
      self.monitor_swarm_fitness()
    self.controller.step(FITNESS)


if __name__ == "__main__":
  rob = Pyroborobo.create(AgentController.config_filename, controller_class=AgentController)
  rob.start()
  config = ConfigReader(AgentController.config_filename)
  landmark = rob.add_landmark()
  landmark.radius = config.get("pTargetZoneRadius", "int")
  landmark.set_coordinates(config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int"))
  landmark.show()
  FITNESS = FitnessMonitor(
    rob.controllers, 
    [config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int")], 
    config.get("pTargetZoneRadius", "int"), 
    config.get("cShepherdAvoidanceRadius", "float"), 
    config.get("pMaxRobotNumber", "int")
  )
  for gen in range(GENERATIONS):
    print("*" * 10, gen, "*" * 10)
    stop = rob.update(T_MAX)
    if stop:
      break
  rob.close()
