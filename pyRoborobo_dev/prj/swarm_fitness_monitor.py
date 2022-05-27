import functions.categorise as categorise

class SwarmFitnessMonitor:

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