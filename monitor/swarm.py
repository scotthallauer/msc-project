import math
import util.categorise as categorise
import util.calculate as calculate
import globals

class SwarmFitnessMonitor:

  def __init__(self, method):
    if method == "CROWD":
      self.monitor = CrowdFitnessMonitor()
    elif method == "DWELL":
      self.monitor = DwellFitnessMonitor()
    elif method == "MINGLE":
      self.monitor = MingleFitnessMonitor()
    else:
      raise Exception("Unsupported method code for measuring swarm fitness")

  def report(self):
    print("*" * 10, "Swarm Fitness Report", "*" * 10)
    self.monitor.report()
    print("Task performance = " + str(self.monitor.score()))

  def score(self):
    return self.monitor.score()

  def track(self):
    self.monitor.track()

  def reset(self):
    self.monitor.reset()


class MingleFitnessMonitor:

  def __init__(self):
    self.dogs = categorise.get_dogs()
    self.target_coords = [globals.config.get("pTargetZoneCoordX", "int"), globals.config.get("pTargetZoneCoordY", "int")]
    self.target_radius = globals.config.get("pTargetZoneRadius", "int")
    self.arena_width = globals.config.get("gArenaWidth", "int")
    self.arena_height = globals.config.get("gArenaHeight", "int")
    self.max_distance = max(
      calculate.distance_between_points([0, 0], self.target_coords),
      calculate.distance_between_points([0, self.arena_height], self.target_coords),
      calculate.distance_between_points([self.arena_width, 0], self.target_coords),
      calculate.distance_between_points([self.arena_width, self.arena_height], self.target_coords)
    ) - self.target_radius # distance from furthest arena corner to target zone border

  def report(self):
    print("Not implemented")

  def score(self):
    interaction_scores = []
    for dog in self.dogs:
      dog_interactions = globals.ds_interaction_monitor.get_history(dog)
      for sheep_interactions in dog_interactions.values():
        for interaction in sheep_interactions:
          interaction_scores.append(self._score_interaction(interaction))
    if len(interaction_scores) == 0:
      return 0
    else:
      return sum(interaction_scores) / len(interaction_scores)

  def track(self):
    pass

  def reset(self):
    globals.ds_interaction_monitor.reset()
    self.__init__()

  def _score_interaction(self, interaction):
    start_coords = interaction["start"]["sheep"]["position"]
    end_coords = interaction["end"]["sheep"]["position"]
    start_distance = calculate.distance_from_target_zone(start_coords, self.target_coords, self.target_radius)
    end_distance = calculate.distance_from_target_zone(end_coords, self.target_coords, self.target_radius)
    start_actual_orientation = interaction["start"]["sheep"]["actual_orientation"]
    start_target_orientation = interaction["start"]["sheep"]["target_orientation"]
    end_actual_orientation = interaction["end"]["sheep"]["actual_orientation"]
    end_target_orientation = interaction["end"]["sheep"]["target_orientation"]
    d_score = self._score_distance_delta(start_distance, end_distance)
    o_score = self._score_orientation_delta(start_coords, start_distance, start_actual_orientation, start_target_orientation, end_coords, end_distance, end_actual_orientation, end_target_orientation)
    s_score = self._score_status_delta(start_distance, end_distance)
    return (d_score + o_score + s_score) / 3

  def _score_distance_delta(self, start_distance, end_distance):
    best_delta = start_distance
    worst_delta = self.max_distance - start_distance
    if end_distance <= start_distance:
      if start_distance == 0:
        return 1
      else:
        return (start_distance - end_distance) / best_delta
    else:
      return - (end_distance - start_distance) / worst_delta

  def _score_orientation_delta(self, start_coords, start_distance, start_actual_orientation, start_target_orientation, end_coords, end_distance, end_actual_orientation, end_target_orientation):
    if start_distance == 0:
      start_relative_gain = 0
      start_relative_loss = 1
    else:
      start_offset_angle = calculate.inner_angle_between_orientations(start_actual_orientation, start_target_orientation)
      start_tangent_angle = math.asin(self.target_radius/calculate.distance_between_points(start_coords, self.target_coords))
      start_absolute_gain = max(start_offset_angle - start_tangent_angle, 0)
      start_absolute_loss = 180 - start_offset_angle
      start_relative_gain = start_absolute_gain / (start_absolute_gain + start_absolute_loss)
      start_relative_loss = 1 - start_relative_gain
    if end_distance == 0:
      end_relative_gain = 0
      end_relative_loss = 1
    else:
      end_offset_angle = calculate.inner_angle_between_orientations(end_actual_orientation, end_target_orientation)
      end_tangent_angle = math.asin(self.target_radius/calculate.distance_between_points(end_coords, self.target_coords))
      end_absolute_gain = max(end_offset_angle - end_tangent_angle, 0)
      end_absolute_loss = 180 - end_offset_angle
      end_relative_gain = end_absolute_gain / (end_absolute_gain + end_absolute_loss)
      end_relative_loss = 1 - end_relative_gain
    if end_relative_gain <= start_relative_gain:
      if start_relative_gain == 0:
        return 1
      else:
        return (start_relative_gain - end_relative_gain) / start_relative_gain
    else:
      return - (start_relative_loss - end_relative_loss) / start_relative_loss

  def _score_status_delta(self, start_distance, end_distance):
    if end_distance == 0:
      return 1
    elif start_distance == 0:
      return -1
    else:
      return 0

class CrowdFitnessMonitor:

  def __init__(self):
    self.sheep = categorise.get_sheep()
    self.time_step = 0
    self.p = 0
    self.t = 0
    self.t_max = globals.config.get("pSimulationLifetime", "int")

  def report(self):
    print("Max percent of herd gathered = " + str(self.p) + "%")
    print("Time taken to gather herd = " + str(self.t) + " time steps")

  def score(self):
    # Fs = (P / 100 + (Tmax - T) / Tmax) / 2
    return ((self.p / 100) + ((self.t_max - self.t) / self.t_max)) / 2

  def track(self):
    self.time_step += 1
    gathered_sheep = 0
    for sheep in self.sheep:
      if categorise.in_target_zone(sheep):
        gathered_sheep += 1
    new_p = gathered_sheep / len(self.sheep) * 100
    if new_p > self.p:
      self.p = new_p
      self.t = self.time_step

  def reset(self):
    self.time_step = 0
    self.p = 0
    self.t = 0


class DwellFitnessMonitor:

  def __init__(self, controllers):
    self.sheep = categorise.get_sheep()
    self.t = 0
    self.t_max = globals.config.get("pSimulationLifetime", "int")

  def report(self):
    print("Average time in target zone per sheep = " + str(self.t / len(self.sheep)) + " out of " + str(self.t_max) + " time steps")

  def score(self):
    # Fs = sum(Ti) / n * Tmax
    return self.t / (len(self.sheep) * self.t_max)

  def track(self):
    for sheep in self.sheep:
      if categorise.in_target_zone(sheep):
        self.t += 1

  def reset(self):
    self.t = 0