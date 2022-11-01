from pyroborobo import Pyroborobo
import globals
import math
import util.categorise as categorise
import util.calculate as calculate
import util.convert as convert
import numpy as np

class SheepController:

  def __init__(self, agent):
    self.agent = agent
    self.agent.set_color(*[0, 255, 0])
    self.agent.status = 1 # 1 = free, 0 = captured (only used in CAPTURE task, always free in CONTAIN)

  def reset(self):
    pass

  def step(self):
    # globals.individual_fitness_monitor.track(self.agent)

    if self.agent.status == 0:
      self.agent.set_rotation(0)
      self.agent.set_translation(0)
      return
    elif globals.config.get("pTaskEnvironment", "str") == "CAPTURE" and categorise.in_target_zone(self.agent):
      self.agent.status = 0
      self.agent.set_position(-100, -100)
      self.agent.set_rotation(0)
      self.agent.set_translation(0)
      return

    self.agent.set_translation(0.8)
    self.agent.set_rotation(0)

    self.fly_towards_center()
    self.match_velocity()

    camera_dist = self.agent.get_all_distances() * globals.config.get("gSensorRange", "int")
    camera_wall = self.agent.get_all_walls()
    camera_robot_id = self.agent.get_all_robot_ids()
    camera_angle_rad = self.agent.get_all_sensor_angles()
    camera_angle_deg = camera_angle_rad * 180 / np.pi

    for sensor_id in np.argsort(camera_dist): # get the index from the closest to the farthest
      # object is out of range
      if camera_angle_deg[sensor_id] < -270 or camera_angle_deg[sensor_id] > 270:
        continue
      # object is a wall
      if camera_wall[sensor_id] and camera_dist[sensor_id] < globals.config.get("sWallAvoidanceRadius", "float"):
        rotation = self.rotation_for_avoidance(camera_dist[sensor_id], camera_angle_deg[sensor_id], globals.config.get("sWallAvoidanceRadius", "float"))
        self.agent.set_rotation(rotation)
        break
      # object is a dog
      if categorise.is_dog(camera_robot_id[sensor_id]) and camera_dist[sensor_id] < globals.config.get("sDogAvoidanceRadius", "float"):
        rotation = self.rotation_for_avoidance(camera_dist[sensor_id], camera_angle_deg[sensor_id], globals.config.get("sDogAvoidanceRadius", "float"))
        self.agent.set_rotation(rotation)
        break
      # object is a sheep
      if categorise.is_sheep(camera_robot_id[sensor_id]) and camera_dist[sensor_id] < globals.config.get("sSheepAvoidanceRadius", "float"):
        rotation = self.rotation_for_avoidance(camera_dist[sensor_id], camera_angle_deg[sensor_id], globals.config.get("sSheepAvoidanceRadius", "float"))
        self.agent.set_rotation(rotation)
        break
      # object is pen
      if globals.config.get("pTaskEnvironment", "str") == "CAPTURE":
        target_coords = [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")]
        target_radius = globals.config.get("pTargetZoneRadius", "int")
        target_distance = calculate.distance_from_target_zone(self.agent.absolute_position, target_coords, target_radius)
        target_avoidance = globals.config.get("sTargetZoneAvoidanceRadius", "float")
        if target_distance <= target_avoidance:
          target_angle = self.agent.get_closest_landmark_orientation() * 180
          rotation = self.rotation_for_avoidance(target_distance, target_angle, target_avoidance) * 0.5
          self.agent.set_rotation(rotation)
          break

  def rotation_for_avoidance(self, distance, angle, avoidance_radius):
    # rotate towards the opposite side that the object was detected on
    rotation_direction = 1 if angle <= 0 else -1
    # most important to avoid when directly in front (i.e. severity = 1 when angle = 0)
    angle_severity = 1 - (abs(angle) / 180)
    # most important to avoid when very close (i.e. severity = 1 when distance = 0)
    distance_severity = 1 - (distance / avoidance_radius)
    return rotation_direction * angle_severity * distance_severity

  # https://github.com/beneater/boids/blob/master/boids.js#L71-L93
  def fly_towards_center(self):
    centerX = 0
    centerY = 0
    numNeighbors = 0
    controllers = Pyroborobo.get().controllers
    for controller in controllers:
      if calculate.distance_between_points(self.agent.absolute_position, controller.absolute_position) < globals.config.get("sSensorRange", "int") and categorise.is_sheep(controller.id): 
        centerX += controller.absolute_position[0]
        centerY += controller.absolute_position[1]
        numNeighbors += 1
    if numNeighbors > 0:
      centerX = centerX / numNeighbors
      centerY = centerY / numNeighbors
      dX = centerX - self.agent.absolute_position[0]
      dY = centerY - self.agent.absolute_position[1]
      if dX != 0:
        angleTowardsCentre = math.degrees(math.atan(dY/dX))
        self.agent.set_rotation(calculate.rotation_for_target_orientation(convert.orientation_to_degrees(self.agent.absolute_orientation), angleTowardsCentre, globals.config.get("sFlockingCoherence", "float")))

  # https://github.com/beneater/boids/blob/master/boids.js#L116-L138
  def match_velocity(self):
    avgDX = 0
    avgDY = 0
    numNeighbors = 0
    controllers = Pyroborobo.get().controllers
    for controller in controllers:
      if calculate.distance_between_points(self.agent.absolute_position, controller.absolute_position) < globals.config.get("sSensorRange", "int") and categorise.is_sheep(controller.id): 
        dx, dy = convert.velocity_to_displacement(controller.absolute_orientation, controller.translation)
        avgDX += dx
        avgDY += dy
        numNeighbors += 1
    if numNeighbors > 1:
      avgDX = avgDX / numNeighbors
      avgDY = avgDY / numNeighbors
      dx, dy = convert.velocity_to_displacement(self.agent.absolute_orientation, self.agent.translation)
      dx += (avgDX - dx) * globals.config.get("sFlockingAlignment", "float")
      dy += (avgDY - dy) * globals.config.get("sFlockingAlignment", "float")
      degrees, translation = convert.displacement_to_velocity(dx, dy)
      if translation != 0:
        self.agent.set_rotation(calculate.rotation_for_target_orientation(convert.orientation_to_degrees(self.agent.absolute_orientation), degrees, globals.config.get("sFlockingCoherence", "float")))