import functions.calculate as calculate

def is_shepherd(id, maxRobotNumber):
  return id >= 0 and id < maxRobotNumber

def get_shepherds(controllers):
  return [c for c in controllers if is_shepherd(c.get_id(), c.config.get("pRobotNumber", "int"))]

def is_cattle(id, maxRobotNumber):
  return id >= 0 and not is_shepherd(id, maxRobotNumber)

def get_cattle(controllers):
  return [c for c in controllers if is_cattle(c.get_id(), c.config.get("pRobotNumber", "int"))]

def in_target_zone(robot):
  return calculate.distance_from_target_zone(robot.absolute_position, [robot.config.get("pTargetZoneCoordX", "int"), robot.config.get("pTargetZoneCoordY", "int")], robot.config.get("pTargetZoneRadius", "int")) == 0