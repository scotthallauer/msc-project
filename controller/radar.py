# This class simplifies the input from a robot's sensors into two values,
# representing the nearest neighbour (of a particular object type) that is detected:
# (1) distance (in the range [0, 1], where 0 = no object detected, and 1 = object detected as close as possible)
# (2) angle (in the range (-1, 1], where negative represents left and positive represents right)

import util.globals as globals
import util.categorise as categorise
import numpy as np

class RadarSensor:

  def __init__(self, agent, type, range, fov=(-180, 180)):
    self.agent = agent
    self.type = type # wall, dog or sheep
    self.range = range # sensory radius in pixels
    self.fov = fov # tuple with max left angle and max right angle in degrees

  def detect(self, normalised=True):
    # get all distance detections and sensor angles (in either absolute values (pixels and degrees) or normalised values)
    distances = self.agent.get_all_distances() * globals.config.get("gSensorRange", "int")
    distances[distances > self.range] = -1 # undetected (becomes 0 when normalised)
    if normalised:
      distances[distances != -1] = 1 - (distances[distances != -1] / self.range)
      angles = self.agent.get_all_sensor_angles() / np.pi
      min_angle = self.fov[0] / 180
      max_angle = self.fov[1] / 180
      undetected_distance = 0
      closest_distance = 0
    else:
      angles = (self.agent.get_all_sensor_angles() / np.pi) * 180
      min_angle = self.fov[0]
      max_angle = self.fov[1]
      undetected_distance = -1
      closest_distance = 9999999999999
    # filter distance detections based on object type for radar
    if self.type == "wall":
      is_walls = self.agent.get_all_walls()
      distances = np.where(is_walls, distances, undetected_distance)
    elif self.type == "dog":
      robot_ids = self.agent.get_all_robot_ids()
      distances = list(map(lambda i: distances[i] if categorise.is_dog(robot_ids[i]) else undetected_distance, range(len(robot_ids))))
    elif self.type == "sheep":
      robot_ids = self.agent.get_all_robot_ids()
      distances = list(map(lambda i: distances[i] if categorise.is_sheep(robot_ids[i]) else undetected_distance, range(len(robot_ids))))
    distances[distances == -1] = undetected_distance
    # exclude distance detections that are outside FOV range
    distances = [distances[i] for i in range(len(angles)) if min_angle <= angles[i] and angles[i] <= max_angle]
    angles = [angle for angle in angles if min_angle <= angle and angle <= max_angle]
    # get nearest distance detection to return
    closest_index = -1
    for i in range(len(distances)):
      if (normalised and distances[i] > closest_distance) or (not normalised and distances[i] != -1 and distances[i] < closest_distance):
        closest_index = i
        closest_distance = distances[i]
    if closest_index == -1:
      return (undetected_distance, 0)
    else:
      return (distances[closest_index], angles[closest_index])
