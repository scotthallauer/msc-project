import functions.calculate as calculate

def is_shepherd(id, maxRobotNumber):
  return id > 0 and id < maxRobotNumber

def is_cattle(id, maxRobotNumber):
  return id > 0 and not is_shepherd(id, maxRobotNumber)

def in_target_zone(robot):
  return calculate.distance_from_target_zone(robot) == 0