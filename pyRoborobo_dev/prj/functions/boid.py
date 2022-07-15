import math
import functions.convert as convert
import functions.calculate as calculate
import functions.categorise as categorise

# https://github.com/beneater/boids/blob/master/boids.js#L71-L93
def fly_towards_center(robot):
  centerX = 0
  centerY = 0
  numNeighbors = 0
  for controller in robot.instance.controllers:
    if calculate.distance_between_points(robot.absolute_position, controller.absolute_position) < robot.config.get("cSensorRange", "int") and categorise.is_cattle(controller.id, robot.config.get("pRobotNumber", "int")): 
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
      robot.set_rotation(calculate.rotation_for_target_orientation(convert.orientation_to_degrees(robot.absolute_orientation), angleTowardsCentre, robot.config.get("cFlockingCoherence", "float")))

# https://github.com/beneater/boids/blob/master/boids.js#L116-L138
def match_velocity(robot):
  avgDX = 0
  avgDY = 0
  numNeighbors = 0
  for controller in robot.instance.controllers:
    if calculate.distance_between_points(robot.absolute_position, controller.absolute_position) < robot.config.get("cSensorRange", "int") and categorise.is_cattle(controller.id, robot.config.get("pRobotNumber", "int")): 
      dx, dy = convert.velocity_to_displacement(controller.absolute_orientation, controller.translation)
      avgDX += dx
      avgDY += dy
      numNeighbors += 1
  if numNeighbors > 1:
    avgDX = avgDX / numNeighbors
    avgDY = avgDY / numNeighbors
    dx, dy = convert.velocity_to_displacement(robot.absolute_orientation, robot.translation)
    dx += (avgDX - dx) * robot.config.get("cFlockingAlignment", "float")
    dy += (avgDY - dy) * robot.config.get("cFlockingAlignment", "float")
    degrees, translation = convert.displacement_to_velocity(dx, dy)
    if translation != 0:
      robot.set_rotation(calculate.rotation_for_target_orientation(convert.orientation_to_degrees(robot.absolute_orientation), degrees, robot.config.get("cFlockingCoherence", "float")))