import globals
import util.categorise as categorise
import util.calculate as calculate
import util.convert as convert

class InteractionMonitor:

  def __init__(self, type):
    if type == "DOGSHEEP":
      self.monitor = DogSheepInteractionMonitor()
    else:
      raise Exception("Unsupported monitor type for interaction monitoring")
  
  def track(self, agent):
    self.monitor.track(agent)

  def get_history(self, agent):
    return self.monitor.get_history(agent)

  def reset(self):
    self.monitor.reset()


class DogSheepInteractionMonitor:

  def __init__(self):
    self.target_coords = [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")]
    self.target_radius = globals.config.get("pTargetZoneRadius", "int")
    self.dog_sensor_range = globals.config.get("dSensorRange", "int")
    self.sheep_sensor_range = globals.config.get("sDogAvoidanceRadius", "float")
    self.mutual_sensor_range = min(self.dog_sensor_range, self.sheep_sensor_range)
    self.tracking = {}
    self.history = {}

  def track(self, dog):
    for sheep in categorise.get_sheep():
      trackable = calculate.distance_between_points(dog.absolute_position, sheep.absolute_position) <= self.mutual_sensor_range
      if dog.id in self.tracking and sheep.id in self.tracking[dog.id]:
        if trackable:
          self.update_tracking(dog, sheep)
        else:
          self.stop_tracking(dog, sheep)
      elif trackable:
        self.start_tracking(dog, sheep)

  def get_history(self, agent):
    if categorise.is_dog(agent.id):
      if agent.id in self.history:
        return self.history[agent.id]
      else:
        return {}
    else:
      sheep_history = {}
      for dog_id in self.history:
        if agent.id in self.history[dog_id]:
          sheep_history[dog_id] = self.history[dog_id][agent.id]
      return sheep_history

  def start_tracking(self, dog, sheep):
    data = {
      "start": {
        "time": globals.simulator.iterations,
        "dog": get_agent_state(dog),
        "sheep": get_agent_state(sheep)
      }, 
      "end": {
        "time": globals.simulator.iterations,
        "dog": get_agent_state(dog),
        "sheep": get_agent_state(sheep)
      }
    }
    if dog.id in self.tracking:
      self.tracking[dog.id][sheep.id] = data
    else:
      self.tracking[dog.id] = {sheep.id: data}

  def update_tracking(self, dog, sheep):
    if dog.id in self.tracking and sheep.id in self.tracking[dog.id]:
      self.tracking[dog.id][sheep.id]["end"] = {
        "time": globals.simulator.iterations,
        "dog": get_agent_state(dog),
        "sheep": get_agent_state(sheep)
      }

  def stop_tracking(self, dog, sheep):
    if dog.id in self.tracking and sheep.id in self.tracking[dog.id]:
      if dog.id in self.history:
        if sheep.id in self.history[dog.id]:
          self.history[dog.id][sheep.id].append(self.tracking[dog.id][sheep.id])
        else:
          self.history[dog.id][sheep.id] = [self.tracking[dog.id][sheep.id]]
      else:
        self.history[dog.id] = {}
        self.history[dog.id][sheep.id] = [self.tracking[dog.id][sheep.id]]
      del self.tracking[dog.id][sheep.id]
      if len(self.tracking[dog.id]) == 0:
        del self.tracking[dog.id]

  def reset(self):
    self.tracking = {}
    self.history = {}


def get_agent_state(agent):
  return {
    "position": agent.absolute_position,
    "actual_orientation": convert.orientation_to_degrees(agent.absolute_orientation),
    "target_orientation": convert.orientation_to_degrees(agent.get_closest_landmark_orientation()),
    "translation": agent.translation,
    "rotation": agent.rotation
  }