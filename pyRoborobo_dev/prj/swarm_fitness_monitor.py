import functions.categorise as categorise

# Fs = (P / 100 + (Tmax - T) / Tmax) / 2
class SwarmFitnessMonitor1:

  def __init__(self, controllers, target_coords, target_radius, max_robots, t_max):
    self.controllers = controllers
    self.target_coords = target_coords
    self.target_radius = target_radius
    self.max_robots = max_robots
    self.time_step = 0
    self.p = 0
    self.t = 0
    self.t_max = t_max

  def report(self):
    print("*" * 10, "Swarm Fitness Report", "*" * 10)
    print("Max percent of herd gathered = " + str(self.p) + "%")
    print("Time taken to gather herd = " + str(self.t) + " time steps")
    print("Task performance = " + str(self.score()))

  def score(self):
    return ((self.p / 100) + ((self.t_max - self.t) / self.t_max)) / 2

  def track(self):
    self.time_step += 1
    gathered_cattle = 0
    total_cattle = 0
    for controller in self.controllers:
      if categorise.is_cattle(controller.id, self.max_robots):
        total_cattle += 1
        if categorise.in_target_zone(controller):
          gathered_cattle += 1
    new_p = gathered_cattle / total_cattle * 100
    if self.p < new_p:
      self.p = new_p
      self.t = self.time_step

  def reset(self):
    self.time_step = 0
    self.p = 0
    self.t = 0

# Fs = sum(Ti) / n * Tmax
class SwarmFitnessMonitor2:

  def __init__(self, controllers, target_coords, target_radius, max_robots, max_cattle, t_max):
    self.cattle = [c for c in controllers if categorise.is_cattle(c.get_id(), max_robots)]
    self.target_coords = target_coords
    self.target_radius = target_radius
    self.max_cattle = max_cattle
    self.t = 0
    self.t_max = t_max

  def report(self):
    print("*" * 10, "Swarm Fitness Report", "*" * 10)
    print("Average time in target zone per cow = " + str(self.t / self.max_cattle) + " out of " + str(self.t_max) + " time steps")
    print("Task performance = " + str(self.score()))

  def score(self):
    return self.t / (self.max_cattle * self.t_max)

  def track(self):
    for cow in self.cattle:
      if categorise.in_target_zone(cow):
        self.t += 1

  def reset(self):
    self.t = 0