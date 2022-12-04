import math

def distance_between_points(coords_a, coords_b):
  return math.sqrt(
    math.pow(coords_a[0] - coords_b[0], 2) +
    math.pow(coords_a[1] - coords_b[1], 2)
  )

def max_distance_between_points(arena_width: int, arena_height: int):
  return distance_between_points([0, 0], [arena_width, arena_height])

def distance_from_target_zone(robot_coords, target_coords, target_radius):
  return max(0, distance_between_points(robot_coords, target_coords) - target_radius)

# distance from furthest arena corner to target zone border
def max_distance_from_target_zone(target_coords: list, target_radius: int, arena_width: int, arena_height: int):
  return max(
    distance_between_points([0, 0], target_coords),
    distance_between_points([0, arena_height], target_coords),
    distance_between_points([arena_width, 0], target_coords),
    distance_between_points([arena_width, arena_height], target_coords)
  ) - target_radius

def inner_angle_between_orientations(orient_a, orient_b):
  angle = abs(orient_a - orient_b)
  if angle <= 180:
    return angle
  else:
    return 360 - angle

def outer_angle_between_orientations(orient_a, orient_b):
  angle = abs(orient_a - orient_b)
  if angle >= 180:
    return angle
  else:
    return 360 - angle

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