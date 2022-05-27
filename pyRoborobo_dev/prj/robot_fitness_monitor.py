import functions.calculate as calculate
import functions.categorise as categorise

class RobotFitnessMonitor:

  def __init__(self, controllers, target_coords, target_radius, avoidance_radius, max_robots):
    self.controllers = controllers
    self.target_coords = target_coords
    self.target_radius = target_radius
    self.avoidance_radius = avoidance_radius
    self.max_robots = max_robots
    self.tracking = {}
    self.history = {}
    self.c_0 = 1.5
    self.c_max = 2
    self.p_max = 1
    self.n_max = 1

  def report(self):
    print("*" * 10, "Robot Fitness Report", "*" * 10)
    for controller in self.controllers:
      if categorise.is_shepherd(controller.id, self.max_robots):
        shepherd_id = controller.id
        if shepherd_id in self.history:
          history = self.history[shepherd_id]
        else:
          history = {'p': 0, 'n': 0}
        print("Shepherd #" + str(shepherd_id) + ": History = " + str(history) + ", Fitness = " + str(self.score(controller)))

  def score(self, shepherd):
    if shepherd.id in self.history:
      p = self.history[shepherd.id]["p"]
      n = self.history[shepherd.id]["n"]
      #return (1 + (self.c_0 * p / self.p_max) - ((self.c_max - self.c_0) * n / self.n_max)) / 2
      return (1 + (p / self.p_max) - (n / self.n_max)) / 2
    else:
      return 0.5

  def track(self, cattle):
    cattle_id = cattle.id
    for controller in self.controllers:
      if categorise.is_shepherd(controller.id, self.max_robots):
        shepherd_id = controller.id
        trackable = calculate.distance_between_points(cattle.absolute_position, controller.absolute_position) <= self.avoidance_radius
        if cattle_id in self.tracking and shepherd_id in self.tracking[cattle_id]:
          if trackable:
            self.update_tracking(shepherd_id, cattle_id, cattle.absolute_position)
          else:
            self.end_tracking(shepherd_id, cattle_id)
        elif trackable:
          self.start_tracking(shepherd_id, cattle_id, cattle.absolute_position)

  def start_tracking(self, shepherd_id, cattle_id, start_coords):
    #if shepherd_id == 1:
    #  print("Shepherd #1: Started tracking Cattle #" + str(cattle_id))
    data = {"start": start_coords, "last": start_coords}
    if cattle_id in self.tracking:
      self.tracking[cattle_id][shepherd_id] = data
    else:
      self.tracking[cattle_id] = {shepherd_id: data}

  def update_tracking(self, shepherd_id, cattle_id, current_coords):
    #if shepherd_id == 1:
    #  print("Shepherd #1: Updated tracking Cattle #" + str(cattle_id))
    if cattle_id in self.tracking and shepherd_id in self.tracking[cattle_id]:
      self.tracking[cattle_id][shepherd_id]["last"] = current_coords

  def end_tracking(self, shepherd_id, cattle_id):
    #if shepherd_id == 1:
    #  print("Shepherd #1: Ended tracking Cattle #" + str(cattle_id))
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
    #if shepherd_id == 1:
    #  print("Shepherd #1: Tracking history is " + str(self.history[shepherd_id]))
    #  print("Shepherd #1: Current p_max is " + str(self.p_max))
    #  print("Shepherd #1: Current n_max is " + str(self.n_max))

  def record_negative_movement(self, shepherd_id):
    if shepherd_id in self.history:
      self.history[shepherd_id]["n"] += 1
    else:
      self.history[shepherd_id] = {"p": 0, "n": 1}
    self.n_max = max(self.n_max, self.history[shepherd_id]["n"])
    #if shepherd_id == 1:
    #  print("Shepherd #1: Tracking history is " + str(self.history[shepherd_id]))
    #  print("Shepherd #1: Current p_max is " + str(self.p_max))
    #  print("Shepherd #1: Current n_max is " + str(self.n_max))

  def reset(self):
    self.tracking = {}
    self.history = {}
    self.p_max = 1
    self.n_max = 1