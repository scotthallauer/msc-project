import math

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