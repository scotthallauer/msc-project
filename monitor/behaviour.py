import globals
import util.categorise as categorise
import util.calculate as calculate

# normalise outputs

class BehaviourMonitor:

  def __init__(self, type):
    if type == "PEN_DISTANCE":
      self.monitor = PenDistanceBehaviourMonitor()
    elif type == "DOG_DISTANCE":
      self.monitor = DogDistanceBehaviourMonitor()
    elif type == "SHEEP_DISTANCE":
      self.monitor = SheepDistanceBehaviourMonitor()
    else:
      raise Exception("Unsupported monitor type for behaviour monitoring")

  def track(self):
    self.monitor.track()

  def get_history(self):
    return self.monitor.get_history()

  def get_average(self):
    return self.monitor.get_average()

  def reset(self):
    self.monitor.reset()


class PenDistanceBehaviourMonitor:

  def __init__(self):
    self.target_coords = [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")]
    self.target_radius = globals.config.get("pTargetZoneRadius", "int")
    self.history = []

  def track(self):
    dogs = categorise.get_dogs()
    total_distance = 0.0
    for dog in dogs:
      total_distance += calculate.distance_from_target_zone(dog.absolute_position, self.target_coords, self.target_radius)
    avg_distance = total_distance / len(dogs)
    self.history.append(avg_distance)

  def get_history(self):
    return self.history

  def get_average(self):
    if len(self.history) == 0:
      return -1
    else:
      return sum(self.history) / len(self.history)

  def reset(self):
    self.history = []


class DogDistanceBehaviourMonitor:

  def __init__(self):
    self.history = []

  def track(self):
    dogs = categorise.get_dogs()
    total_distance = 0.0
    for dogA in dogs:
      closest_distance = 99999999999999999
      for dogB in dogs:
        if dogA.id != dogB.id:
          distance = calculate.distance_between_points(dogA.absolute_position, dogB.absolute_position)
          if distance < closest_distance:
            closest_distance = distance
      total_distance += closest_distance
    avg_distance = total_distance / len(dogs)
    self.history.append(avg_distance)

  def get_history(self):
    return self.history

  def get_average(self):
    if len(self.history) == 0:
      return -1
    else:
      return sum(self.history) / len(self.history)

  def reset(self):
    self.history = []


class SheepDistanceBehaviourMonitor:

  def __init__(self):
    self.history = []

  def track(self):
    dogs = categorise.get_dogs()
    sheeps = categorise.get_sheep()
    total_distance = 0.0
    for dog in dogs:
      closest_distance = 99999999999999999
      for sheep in sheeps:
        distance = calculate.distance_between_points(dog.absolute_position, sheep.absolute_position)
        if distance < closest_distance:
          closest_distance = distance
      total_distance += closest_distance
    avg_distance = total_distance / len(dogs)
    self.history.append(avg_distance)

  def get_history(self):
    return self.history

  def get_average(self):
    if len(self.history) == 0:
      return -1
    else:
      return sum(self.history) / len(self.history)

  def reset(self):
    self.history = []