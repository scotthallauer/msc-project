import math

def distance_between_points(coordsA, coordsB):
  return math.sqrt(
    math.pow(coordsA[0] - coordsB[0], 2) +
    math.pow(coordsA[1] - coordsB[1], 2)
  )

def distance_from_target_zone(robot):
  return max(0, distance_between_points(robot.absolute_position, [robot.config.get("pTargetZoneCoordX", "int"), robot.config.get("pTargetZoneCoordY", "int")]) - robot.config.get("pTargetZoneRadius", "int"))

# give best rotation for turning towards target orientation
# rotation: 1 = max clockwise, 0 = no rotation, -1 = max counter-clockwise
def rotation_for_target_orientation(current_degrees, target_degrees, coherence):
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