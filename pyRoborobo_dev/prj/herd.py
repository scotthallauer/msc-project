from pyroborobo import Pyroborobo, Controller
import math
import numpy as np
from configparser import ConfigParser

def distance(coordsA, coordsB):
  return math.sqrt(
    math.pow(coordsA[0] - coordsB[0], 2) +
    math.pow(coordsA[1] - coordsB[1], 2)
  )

# orientation (input/degrees): 0 = right, 90 = down, 180 = left, 270 = up
# orientation (output/roborobo): -2.0/0.0/2.0 = right, -1.5/0.5 = down, -1.0/1.0 = left, -0.5/1.5 = up
def orientation_to_degrees(orientation):
  if orientation < 0:
    return 360 - ((-orientation % 2) * 180)
  else:
    return (orientation % 2) * 180

# translation: 1 = max forward, 0 = no movement, -1 = max reverse
# x: right = +, left = -
# y: up = -, down = +
def velocity_to_displacement(orientation, translation):
  dx = 0
  dy = 0
  degrees = orientation_to_degrees(orientation)
  if degrees < 90:
    dx = translation * math.cos(math.radians(degrees))
    dy = translation * math.sin(math.radians(degrees))
  elif degrees < 180:
    dx = -translation * math.cos(math.radians(180 - degrees))
    dy = translation * math.sin(math.radians(180 - degrees))
  elif degrees < 270:
    dx = -translation * math.cos(math.radians(degrees - 180))
    dy = -translation * math.sin(math.radians(degrees - 180))
  else: # degrees < 360
    dx = translation * math.cos(math.radians(360 - degrees))
    dy = -translation * math.sin(math.radians(360 - degrees))
  epsilon = 1.0e-10
  if abs(dx) < epsilon:
    dx = 0
  if abs(dy) < epsilon:
    dy = 0
  return (dx, dy)

# does not handle reversing
def displacement_to_velocity(dx, dy):
  degrees = 0
  translation = 0
  if dx == 0:
    degrees = (90 if dy > 0 else 270)
    translation = dy
  elif dy == 0:
    degrees = (0 if dx > 0 else 180)
    translation = dx
  else:
    angle = math.degrees(math.atan(abs(dy/dx)))
    if dx >= 0 and dy >= 0:
      degrees = angle
    elif dx < 0 and dy >= 0:
      degrees = 180 - angle
    elif dx < 0 and dy < 0:
      degrees = 180 + angle
    else: # dx >= 0 and dy < 0
      degrees = 360 - angle
    translation = abs(dy) / math.sin(math.radians(angle))
  return (degrees, translation)

# give best rotation for turning towards target orientation
# rotation: 1 = max clockwise, 0 = no rotation, -1 = max counter-clockwise
def rotation_for_target(current_degrees, target_degrees, coherence):
  if current_degrees < target_degrees:
    delta_clockwise = target_degrees - current_degrees
    delta_counter_clockwise = 360 - delta_clockwise
  else:
    delta_counter_clockwise = current_degrees - target_degrees
    delta_clockwise = 360 - delta_counter_clockwise
  if delta_clockwise < delta_counter_clockwise:
    return coherence
  elif delta_counter_clockwise < delta_clockwise:
    return -coherence
  else:
    return 0

# https://github.com/beneater/boids/blob/master/boids.js#L71-L93
def flyTowardsCenter(robot):
  centerX = 0
  centerY = 0
  numNeighbors = 0
  for controller in robot.instance.controllers:
    if distance(robot.absolute_position, controller.absolute_position) < robot.config.get("cSensorRange", "int") and is_cattle(controller.id, robot.config.get("pMaxRobotNumber", "int")): 
      centerX += controller.absolute_position[0]
      centerY += controller.absolute_position[1]
      numNeighbors += 1
  if numNeighbors > 0:
    centerX = centerX / numNeighbors
    centerY = centerY / numNeighbors
    dX = centerX - robot.absolute_position[0]
    dY = centerY - robot.absolute_position[1]
    if dX != 0:
      angleTowardsCentre = math.degrees(math.atan(dY/dX))
      robot.set_rotation(rotation_for_target(orientation_to_degrees(robot.absolute_orientation), angleTowardsCentre, robot.config.get("cFlockingCoherence", "float")))

# https://github.com/beneater/boids/blob/master/boids.js#L116-L138
def matchVelocity(robot):
  avgDX = 0
  avgDY = 0
  numNeighbors = 0
  for controller in robot.instance.controllers:
    if distance(robot.absolute_position, controller.absolute_position) < robot.config.get("cSensorRange", "int") and is_cattle(controller.id, robot.config.get("pMaxRobotNumber", "int")): 
      dx, dy = velocity_to_displacement(controller.absolute_orientation, controller.translation)
      avgDX += dx
      avgDY += dy
      numNeighbors += 1
  if numNeighbors > 1:
    avgDX = avgDX / numNeighbors
    avgDY = avgDY / numNeighbors
    dx, dy = velocity_to_displacement(robot.absolute_orientation, robot.translation)
    dx += (avgDX - dx) * robot.config.get("cFlockingAlignment", "float")
    dy += (avgDY - dy) * robot.config.get("cFlockingAlignment", "float")
    degrees, translation = displacement_to_velocity(dx, dy)
    if translation != 0:
      robot.set_rotation(rotation_for_target(orientation_to_degrees(robot.absolute_orientation), degrees, robot.config.get("cFlockingCoherence", "float")))

def is_shepherd(id, maxRobotNumber):
  return id > 0 and id < maxRobotNumber

def is_cattle(id, maxRobotNumber):
  return id > 0 and not is_shepherd(id, maxRobotNumber)

def in_target_zone(robot):
  return get_target_zone_dist(robot) == 0

def get_target_zone_dist(robot):
  return max(0, distance(robot.absolute_position, [robot.config.get("pTargetZoneCoordX", "int"), robot.config.get("pTargetZoneCoordY", "int")]) - robot.config.get("pTargetZoneRadius", "int"))

FITNESS_P = 0
FITNESS_T = 0
TIME_STEP = 0

def monitor_fitness(instance):
  global FITNESS_P, FITNESS_T, TIME_STEP
  gathered_cattle = 0
  total_cattle = 0
  for robot in instance.controllers:
    if is_cattle(robot.get_id(), robot.config.get("pMaxRobotNumber", "int")):
      total_cattle += 1
      if in_target_zone(robot):
        gathered_cattle += 1
  new_p = gathered_cattle / total_cattle * 100
  if FITNESS_P < new_p:
    FITNESS_P = new_p
    FITNESS_T = TIME_STEP

def get_fitness(instance):
  return ((FITNESS_P / 100) + ((5000 - FITNESS_T) / 5000)) / 2




class ConfigReader():

  def __init__(self, config_filename):
    self.config_filename = config_filename
    self.config_parser = ConfigParser()
    with open(self.config_filename) as stream:
      self.config_parser.read_string("[root]\n" + stream.read())

  def get(self, parameter, type):
    value = self.config_parser.get("root", parameter)
    if type == "int":
      return int(value)
    elif type == "float":
      return float(value)
    else:
      return str(value)



class AgentController(Controller):

  config_filename = "config/herd.properties"
  props = {}

  def __init__(self, world_model):
    Controller.__init__(self, world_model) # mandatory call to super constructor
    self.config = ConfigReader(AgentController.config_filename)
    if is_shepherd(self.get_id(), self.config.get("pMaxRobotNumber", "int")):
      self.controller = ShepherdController(self)
    else:
      self.controller = CattleController(self)

  def reset(self):
    self.controller.reset()

  def step(self):  # step is called at each time step
    self.controller.step()



class ShepherdController:

  def __init__(self, agent):
    self.agent = agent
    self.agent.instance = Pyroborobo.get()
    self.agent.set_color(*[255, 0, 0])
    self.agent.camera_max_range = 0
    self.agent.orientation_radius = 0

  def reset(self):
    self.agent.orientation_radius = 0.6

  def step(self):
    self.agent.set_translation(0.25)  # Let's go forward
    self.agent.set_rotation(0)

    camera_dist = self.agent.get_all_distances()
    camera_wall = self.agent.get_all_walls()
    camera_robot_id = self.agent.get_all_robot_ids()
    camera_angle_rad = self.agent.get_all_sensor_angles()
    camera_angle_deg = camera_angle_rad * 180 / np.pi

    for sensor_id in np.argsort(camera_dist): # get the index from the closest to the farthest
      # object is out of range
      if camera_angle_deg[sensor_id] < -270 or camera_angle_deg[sensor_id] > 270:
        continue
      # object is a wall
      if camera_wall[sensor_id] and camera_dist[sensor_id] < self.agent.config.get("sWallAvoidanceRadius", "float"):
        if camera_angle_deg[sensor_id] != 0:
          self.agent.set_rotation(-camera_angle_rad[sensor_id] / np.pi)
        else:
          self.agent.set_rotation(1)
        break
      # object is a shepherd
      if is_shepherd(camera_robot_id[sensor_id], self.agent.config.get("pMaxRobotNumber", "int")) and camera_dist[sensor_id] < self.agent.config.get("sShepherdAvoidanceRadius", "float"):
        if camera_angle_deg[sensor_id] != 0:
          self.agent.set_rotation(-camera_angle_rad[sensor_id] / np.pi)
        else:
          self.agent.set_rotation(1)
        break
      # object is a cattle
      if is_cattle(camera_robot_id[sensor_id], self.agent.config.get("pMaxRobotNumber", "int")) and camera_dist[sensor_id] < self.agent.config.get("sCattleAvoidanceRadius", "float"):
        if camera_angle_deg[sensor_id] != 0:
          self.agent.set_rotation(-camera_angle_rad[sensor_id] / np.pi)
        else:
          self.agent.set_rotation(1)
        break



class CattleController:

  def __init__(self, agent):
    self.agent = agent
    self.agent.instance = Pyroborobo.get()
    self.agent.set_color(*[0, 255, 0])
    self.agent.camera_max_range = 0
    self.agent.orientation_radius = 0

  def reset(self):
    self.agent.orientation_radius = 0.6

  def step(self):
    global FITNESS_P, FITNESS_T, TIME_STEP
    self.agent.set_translation(1)  # Let's go forward
    self.agent.set_rotation(0)

    if self.agent.get_id() == 11:
      TIME_STEP += 1
      monitor_fitness(self.agent.instance)
      print("fitness = " + str(get_fitness(self.agent.instance)) + " (p = " + str(FITNESS_P) + ", t = " + str(FITNESS_T) + ")")

    flyTowardsCenter(self.agent)
    matchVelocity(self.agent)

    camera_dist = self.agent.get_all_distances()
    camera_wall = self.agent.get_all_walls()
    camera_robot_id = self.agent.get_all_robot_ids()
    camera_angle_rad = self.agent.get_all_sensor_angles()
    camera_angle_deg = camera_angle_rad * 180 / np.pi

    for sensor_id in np.argsort(camera_dist): # get the index from the closest to the farthest
      # object is out of range
      if camera_angle_deg[sensor_id] < -270 or camera_angle_deg[sensor_id] > 270:
        continue
      # object is a wall
      if camera_wall[sensor_id] and camera_dist[sensor_id] < self.agent.config.get("cWallAvoidanceRadius", "float"):
        if camera_angle_deg[sensor_id] != 0:
          self.agent.set_rotation(-camera_angle_rad[sensor_id] / np.pi)
        else:
          self.agent.set_rotation(1)
        break
      # object is a shepherd
      if is_shepherd(camera_robot_id[sensor_id], self.agent.config.get("pMaxRobotNumber", "int")) and camera_dist[sensor_id] < self.agent.config.get("cShepherdAvoidanceRadius", "float"):
        if camera_angle_deg[sensor_id] != 0:
          self.agent.set_rotation(-camera_angle_rad[sensor_id] / np.pi)
        else:
          self.agent.set_rotation(1)
        break
      # object is a cattle
      if is_cattle(camera_robot_id[sensor_id], self.agent.config.get("pMaxRobotNumber", "int")) and camera_dist[sensor_id] < self.agent.config.get("cCattleAvoidanceRadius", "float"):
        if camera_angle_deg[sensor_id] != 0:
          self.agent.set_rotation(-camera_angle_rad[sensor_id] / np.pi)
        else:
          self.agent.set_rotation(1)
        break



if __name__ == "__main__":
  rob = Pyroborobo.create(AgentController.config_filename, controller_class=AgentController)
  rob.start()
  config = ConfigReader(AgentController.config_filename)
  landmark = rob.add_landmark()
  landmark.radius = config.get("pTargetZoneRadius", "int")
  landmark.set_coordinates(config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int"))
  landmark.show()
  rob.update(100000)
  rob.close()
