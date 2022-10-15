import util.calculate as calculate
import globals

def is_dog(id):
  return id >= 0 and id < globals.config.get("pNumberOfDogs", "int")

def get_dogs():
  return [c for c in globals.simulator.controllers if is_dog(c.get_id())]

def is_sheep(id):
  return id >= 0 and not is_dog(id)

def get_sheep():
  return [c for c in globals.simulator.controllers if is_sheep(c.get_id())]

def in_target_zone(robot):
  return calculate.distance_from_target_zone(robot.absolute_position, [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")], globals.config.get("pTargetZoneRadius", "int")) == 0