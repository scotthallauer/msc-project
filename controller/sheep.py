from pyroborobo import Pyroborobo
import globals
import math
import util.categorise as categorise
import util.calculate as calculate
import util.convert as convert
from controller.radar import RadarSensor
import numpy as np

class SheepController:

  def __init__(self, agent):
    self.agent = agent
    self.agent.set_color(*[0, 255, 0])
    self.agent.status = 1 # 1 = free, 0 = captured (only used in CAPTURE task, always free in CONTAIN)
    self.sensor_fov = (-180, 180)
    self.sensor_range = globals.config.get("sSensorRange", "int")
    self.dog_sensor = RadarSensor(self.agent, "dog", self.sensor_range, self.sensor_fov)
    self.sheep_sensor = RadarSensor(self.agent, "sheep", self.sensor_range, self.sensor_fov)
    self.wall_sensor = RadarSensor(self.agent, "wall", self.sensor_range, self.sensor_fov)

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
      self.agent.set_position(0, 0)
      self.agent.set_rotation(0)
      self.agent.set_translation(0)
      return

    self.agent.set_translation(0.8)
    self.agent.set_rotation(0)

    self.fly_towards_center()
    self.match_velocity()

    wall_distance, wall_angle = self.wall_sensor.detect(normalised=False)
    dog_distance, dog_angle = self.dog_sensor.detect(normalised=False)
    sheep_distance, sheep_angle = self.sheep_sensor.detect(normalised=False)

    distances = [wall_distance, dog_distance, sheep_distance]
    angles = [wall_angle, dog_angle, sheep_angle]
    avoidances = [
      globals.config.get("sWallAvoidanceRadius", "float"), 
      globals.config.get("sDogAvoidanceRadius", "float"), 
      globals.config.get("sSheepAvoidanceRadius", "float")
    ]

    # target zone avoidance (for CAPTURE task)
    if globals.config.get("pTaskEnvironment", "str") == "CAPTURE" and (dog_distance == 0 or dog_distance > avoidances[1]):
      target_coords = [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")]
      target_radius = globals.config.get("pTargetZoneRadius", "int")
      target_distance = calculate.distance_from_target_zone(self.agent.absolute_position, target_coords, target_radius)
      target_avoidance = globals.config.get("sTargetZoneAvoidanceRadius", "float")
      if target_distance <= target_avoidance:
        target_angle = self.agent.get_closest_landmark_orientation() * 180
        rotation = self.rotation_for_avoidance(target_distance, target_angle, target_avoidance) * globals.config.get("sTargetZoneAvoidanceStrength", "float")
        self.agent.set_rotation(rotation)
        return

    # wall, dog and sheep avoidance
    for index in np.argsort(distances):
      if 0 < distances[index] and distances[index] <= avoidances[index]:
        rotation = self.rotation_for_avoidance(distances[index], angles[index], avoidances[index])
        self.agent.set_rotation(rotation)
        return

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