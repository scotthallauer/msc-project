import functions.calculate as calculate
import functions.categorise as categorise

class IndividualFitnessMonitor:

  def __init__(self, method, config, controllers):
    if method == "REGCNT":
      self.monitor = RegularCountFitnessMonitor(config, controllers)
    elif method == "SUPCNT":
      self.monitor = SuperCountFitnessMonitor(config, controllers)
    elif method == "SUPDST":
      self.monitor = SuperDistanceFitnessMonitor(config, controllers)
    else:
      raise Exception("Unsupported method code for measuring individual fitness")

  def report(self):
    print("*" * 10, "Individual Fitness Report", "*" * 10)
    self.monitor.report()

  def score(self, shepherd):
    return self.monitor.score(shepherd)

  def avg_score(self):
    return self.monitor.avg_score()

  def track(self, cow):
    self.monitor.track(cow)

  def reset(self):
    self.monitor.reset()


class RegularCountFitnessMonitor:

  def __init__(self, config, controllers):
    self.shepherds = [c for c in controllers if categorise.is_shepherd(c.get_id(), config.get("pMaxRobotNumber", "int"))]
    self.target_coords = [config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int")]
    self.target_radius = config.get("pTargetZoneRadius", "int")
    self.avoidance_radius = config.get("cShepherdAvoidanceRadius", "float")
    self.tracking = {}
    self.history = {}
    self.p_max = 1
    self.n_max = 1

  def report(self):
    for shepherd in self.shepherds:
      if shepherd.id in self.history:
        history = self.history[shepherd.id]
      else:
        history = {'p': 0, 'n': 0}
      print("Shepherd #" + str(shepherd.id) + ": History = " + str(history) + ", Fitness = " + str(self.score(shepherd)))

  def score(self, shepherd):
    if shepherd.id in self.history:
      p = self.history[shepherd.id]["p"]
      n = self.history[shepherd.id]["n"]
      # Fi = (1 + P / Pmax - N / Nmax) / 2
      return (1 + (p / self.p_max) - (n / self.n_max)) / 2
    else:
      return 0.5

  def avg_score(self):
    total_fitness = 0
    for shepherd in self.shepherds:
      total_fitness += self.score(shepherd)
    return total_fitness / len(self.shepherds)

  def track(self, cow):
    for shepherd in self.shepherds:
      trackable = calculate.distance_between_points(cow.absolute_position, shepherd.absolute_position) <= self.avoidance_radius
      if cow.id in self.tracking and shepherd.id in self.tracking[cow.id]:
        if trackable:
          self.update_tracking(shepherd.id, cow.id, cow.absolute_position)
        else:
          self.end_tracking(shepherd.id, cow.id)
      elif trackable:
        self.start_tracking(shepherd.id, cow.id, cow.absolute_position)

  def start_tracking(self, shepherd_id, cattle_id, start_coords):
    data = {"start": start_coords, "last": start_coords}
    if cattle_id in self.tracking:
      self.tracking[cattle_id][shepherd_id] = data
    else:
      self.tracking[cattle_id] = {shepherd_id: data}

  def update_tracking(self, shepherd_id, cattle_id, current_coords):
    if cattle_id in self.tracking and shepherd_id in self.tracking[cattle_id]:
      self.tracking[cattle_id][shepherd_id]["last"] = current_coords

  def end_tracking(self, shepherd_id, cattle_id):
    if cattle_id in self.tracking and shepherd_id in self.tracking[cattle_id]:
      start_coords = self.tracking[cattle_id][shepherd_id]["start"]
      end_coords = self.tracking[cattle_id][shepherd_id]["last"]
      start_dist = calculate.distance_from_target_zone(start_coords, self.target_coords, self.target_radius)
      end_dist = calculate.distance_from_target_zone(end_coords, self.target_coords, self.target_radius)
      if start_dist > end_dist:
        self.record_positive_movement(shepherd_id)
      elif end_dist > start_dist:
        self.record_negative_movement(shepherd_id)
      del self.tracking[cattle_id][shepherd_id]
      if len(self.tracking[cattle_id]) == 0:
        del self.tracking[cattle_id]

  def record_positive_movement(self, shepherd_id):
    if shepherd_id in self.history:
      self.history[shepherd_id]["p"] += 1
    else:
      self.history[shepherd_id] = {"p": 1, "n": 0}
    self.p_max = max(self.p_max, self.history[shepherd_id]["p"])

  def record_negative_movement(self, shepherd_id):
    if shepherd_id in self.history:
      self.history[shepherd_id]["n"] += 1
    else:
      self.history[shepherd_id] = {"p": 0, "n": 1}
    self.n_max = max(self.n_max, self.history[shepherd_id]["n"])

  def reset(self):
    self.tracking = {}
    self.history = {}
    self.p_max = 1
    self.n_max = 1


class SuperCountFitnessMonitor:

  def __init__(self, config, controllers):
    self.shepherds = [c for c in controllers if categorise.is_shepherd(c.get_id(), config.get("pMaxRobotNumber", "int"))]
    self.target_coords = [config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int")]
    self.target_radius = config.get("pTargetZoneRadius", "int")
    self.avoidance_radius = config.get("cShepherdAvoidanceRadius", "float")
    self.tracking = {}
    self.history = {}
    self.c_p = 10
    self.c_n = 10
    self.p_max = 1
    self.n_max = 1

  def report(self):
    for shepherd in self.shepherds:
      if shepherd.id in self.history:
        history = self.history[shepherd.id]
      else:
        history = {'p_0': 0, 'p_s': 0, 'n_0': 0, 'n_s': 0}
      print("Shepherd #" + str(shepherd.id) + ": History = " + str(history) + ", Fitness = " + str(self.score(shepherd)))

  def score(self, shepherd):
    if shepherd.id in self.history:
      p_0 = self.history[shepherd.id]["p_0"]
      p_s = self.history[shepherd.id]["p_s"]
      n_0 = self.history[shepherd.id]["n_0"]
      n_s = self.history[shepherd.id]["n_s"]
      # Fi = (1 + (P0 + CP * P+) / Pmax - (N0 + CN * N+) / Nmax) / 2
      return (1 + ((p_0 + self.c_p * p_s) / self.p_max) - ((n_0 + self.c_n * n_s) / self.n_max)) / 2
    else:
      return 0.5

  def avg_score(self):
    total_fitness = 0
    for shepherd in self.shepherds:
      total_fitness += self.score(shepherd)
    return total_fitness / len(self.shepherds)

  def track(self, cow):
    for shepherd in self.shepherds:
      trackable = calculate.distance_between_points(cow.absolute_position, shepherd.absolute_position) <= self.avoidance_radius
      if cow.id in self.tracking and shepherd.id in self.tracking[cow.id]:
        if trackable:
          self.update_tracking(shepherd.id, cow.id, cow.absolute_position)
        else:
          self.end_tracking(shepherd.id, cow.id)
      elif trackable:
        self.start_tracking(shepherd.id, cow.id, cow.absolute_position)

  def start_tracking(self, shepherd_id, cattle_id, start_coords):
    data = {"start": start_coords, "last": start_coords}
    if cattle_id in self.tracking:
      self.tracking[cattle_id][shepherd_id] = data
    else:
      self.tracking[cattle_id] = {shepherd_id: data}

  def update_tracking(self, shepherd_id, cattle_id, current_coords):
    if cattle_id in self.tracking and shepherd_id in self.tracking[cattle_id]:
      self.tracking[cattle_id][shepherd_id]["last"] = current_coords

  def end_tracking(self, shepherd_id, cattle_id):
    if cattle_id in self.tracking and shepherd_id in self.tracking[cattle_id]:
      start_coords = self.tracking[cattle_id][shepherd_id]["start"]
      end_coords = self.tracking[cattle_id][shepherd_id]["last"]
      start_dist = calculate.distance_from_target_zone(start_coords, self.target_coords, self.target_radius)
      end_dist = calculate.distance_from_target_zone(end_coords, self.target_coords, self.target_radius)
      if start_dist > end_dist:
        if end_dist != 0:
          self.record_regular_positive_movement(shepherd_id)
        elif end_dist == 0:
          self.record_super_positive_movement(shepherd_id)
      elif end_dist > start_dist:
        if start_dist != 0:
          self.record_regular_negative_movement(shepherd_id)
        elif start_dist == 0:
          self.record_super_negative_movement(shepherd_id)
      del self.tracking[cattle_id][shepherd_id]
      if len(self.tracking[cattle_id]) == 0:
        del self.tracking[cattle_id]

  def record_regular_positive_movement(self, shepherd_id):
    if shepherd_id in self.history:
      self.history[shepherd_id]["p_0"] += 1
    else:
      self.history[shepherd_id] = {"p_0": 1, "p_s": 0, "n_0": 0, "n_s": 0}
    p = self.history[shepherd_id]["p_0"] + self.c_p * self.history[shepherd_id]["p_s"]
    self.p_max = max(self.p_max, p)

  def record_super_positive_movement(self, shepherd_id):
    if shepherd_id in self.history:
      self.history[shepherd_id]["p_s"] += 1
    else:
      self.history[shepherd_id] = {"p_0": 0, "p_s": 1, "n_0": 0, "n_s": 0}
    p = self.history[shepherd_id]["p_0"] + self.c_p * self.history[shepherd_id]["p_s"]
    self.p_max = max(self.p_max, p)

  def record_regular_negative_movement(self, shepherd_id):
    if shepherd_id in self.history:
      self.history[shepherd_id]["n_0"] += 1
    else:
      self.history[shepherd_id] = {"p_0": 0, "p_s": 0, "n_0": 1, "n_s": 0}
    n = self.history[shepherd_id]["n_0"] + self.c_n * self.history[shepherd_id]["n_s"]
    self.n_max = max(self.n_max, n)

  def record_super_negative_movement(self, shepherd_id):
    if shepherd_id in self.history:
      self.history[shepherd_id]["n_s"] += 1
    else:
      self.history[shepherd_id] = {"p_0": 0, "p_s": 0, "n_0": 0, "n_s": 1}
    n = self.history[shepherd_id]["n_0"] + self.c_n * self.history[shepherd_id]["n_s"]
    self.n_max = max(self.n_max, n)

  def reset(self):
    self.tracking = {}
    self.history = {}
    self.p_max = 1
    self.n_max = 1


class SuperDistanceFitnessMonitor:

  def __init__(self, config, controllers):
    self.shepherds = [c for c in controllers if categorise.is_shepherd(c.get_id(), config.get("pMaxRobotNumber", "int"))]
    self.target_coords = [config.get("pTargetZoneCoordX", "int"), config.get("pTargetZoneCoordY", "int")]
    self.target_radius = config.get("pTargetZoneRadius", "int")
    self.avoidance_radius = config.get("cShepherdAvoidanceRadius", "float")
    self.tracking = {}
    self.history = {}
    self.c_p = 100
    self.c_n = 100
    self.p_max = 0.00000001
    self.n_max = 0.00000001

  def report(self):
    p_total = 0
    n_total = 0
    for shepherd in self.shepherds:
      if shepherd.id in self.history:
        history = self.history[shepherd.id]
      else:
        history = {'p_0': 0, 'p_s': 0, 'n_0': 0, 'n_s': 0}
      p_total += history['p_0']
      n_total += history['n_0']
      print("Shepherd #" + str(shepherd.id) + ": History = " + str(history) + ", Fitness = " + str(self.score(shepherd)))
    print("Total positive distance = " + str(p_total))
    print("Total negative distance = " + str(n_total))

  def score(self, shepherd):
    if shepherd.id in self.history:
      p_0 = self.history[shepherd.id]["p_0"]
      p_s = self.history[shepherd.id]["p_s"]
      n_0 = self.history[shepherd.id]["n_0"]
      n_s = self.history[shepherd.id]["n_s"]
      # Fi = (1 + sum(Pi) / Pmax - sum(Ni) / Nmax) / 2
      return (1 + ((p_0 + self.c_p * p_s) / self.p_max) - ((n_0 + self.c_n * n_s) / self.n_max)) / 2
    else:
      return 0.5

  def avg_score(self):
    total_fitness = 0
    for shepherd in self.shepherds:
      total_fitness += self.score(shepherd)
    return total_fitness / len(self.shepherds)

  def track(self, cow):
    for shepherd in self.shepherds:
      trackable = calculate.distance_between_points(cow.absolute_position, shepherd.absolute_position) <= self.avoidance_radius
      if cow.id in self.tracking and shepherd.id in self.tracking[cow.id]:
        if trackable:
          self.update_tracking(shepherd.id, cow.id, cow.absolute_position)
        else:
          self.end_tracking(shepherd.id, cow.id)
      elif trackable:
        self.start_tracking(shepherd.id, cow.id, cow.absolute_position)

  def start_tracking(self, shepherd_id, cattle_id, start_coords):
    data = {"start": start_coords, "last": start_coords}
    if cattle_id in self.tracking:
      self.tracking[cattle_id][shepherd_id] = data
    else:
      self.tracking[cattle_id] = {shepherd_id: data}

  def update_tracking(self, shepherd_id, cattle_id, current_coords):
    if cattle_id in self.tracking and shepherd_id in self.tracking[cattle_id]:
      self.tracking[cattle_id][shepherd_id]["last"] = current_coords

  def end_tracking(self, shepherd_id, cattle_id):
    if cattle_id in self.tracking and shepherd_id in self.tracking[cattle_id]:
      start_coords = self.tracking[cattle_id][shepherd_id]["start"]
      end_coords = self.tracking[cattle_id][shepherd_id]["last"]
      start_dist = calculate.distance_from_target_zone(start_coords, self.target_coords, self.target_radius)
      end_dist = calculate.distance_from_target_zone(end_coords, self.target_coords, self.target_radius)
      diff_dist = abs(start_dist - end_dist)
      if start_dist > end_dist:
        if end_dist != 0:
          self.record_regular_positive_movement(shepherd_id, diff_dist)
        elif end_dist == 0:
          self.record_super_positive_movement(shepherd_id, diff_dist)
      elif end_dist > start_dist:
        if start_dist != 0:
          self.record_regular_negative_movement(shepherd_id, diff_dist)
        elif start_dist == 0:
          self.record_super_negative_movement(shepherd_id, diff_dist)
      del self.tracking[cattle_id][shepherd_id]
      if len(self.tracking[cattle_id]) == 0:
        del self.tracking[cattle_id]

  def record_regular_positive_movement(self, shepherd_id, distance):
    if shepherd_id in self.history:
      self.history[shepherd_id]["p_0"] += distance
    else:
      self.history[shepherd_id] = {"p_0": distance, "p_s": 0, "n_0": 0, "n_s": 0}
    p = self.history[shepherd_id]["p_0"] + self.c_p * self.history[shepherd_id]["p_s"]
    self.p_max = max(self.p_max, p)

  def record_super_positive_movement(self, shepherd_id, distance):
    if shepherd_id in self.history:
      self.history[shepherd_id]["p_0"] += distance
      self.history[shepherd_id]["p_s"] += distance
    else:
      self.history[shepherd_id] = {"p_0": distance, "p_s": 1, "n_0": 0, "n_s": 0}
    p = self.history[shepherd_id]["p_0"] + self.c_p * self.history[shepherd_id]["p_s"]
    self.p_max = max(self.p_max, p)

  def record_regular_negative_movement(self, shepherd_id, distance):
    if shepherd_id in self.history:
      self.history[shepherd_id]["n_0"] += distance
    else:
      self.history[shepherd_id] = {"p_0": 0, "p_s": 0, "n_0": distance, "n_s": 0}
    n = self.history[shepherd_id]["n_0"] + self.c_n * self.history[shepherd_id]["n_s"]
    self.n_max = max(self.n_max, n)

  def record_super_negative_movement(self, shepherd_id, distance):
    if shepherd_id in self.history:
      self.history[shepherd_id]["n_0"] += distance
      self.history[shepherd_id]["n_s"] += 1
    else:
      self.history[shepherd_id] = {"p_0": 0, "p_s": 0, "n_0": distance, "n_s": 1}
    n = self.history[shepherd_id]["n_0"] + self.c_n * self.history[shepherd_id]["n_s"]
    self.n_max = max(self.n_max, n)

  def reset(self):
    self.tracking = {}
    self.history = {}
    self.p_max = 0.00000001
    self.n_max = 0.00000001


# TODO: Consider cattle start trajectory and end trajectory (facing in direction towards target zone centre is better than facing away or tangential)