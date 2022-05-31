from tkinter import E
import functions.categorise as categorise

# TODO: Should factor in duration herd is kept in target zone

class SwarmFitnessMonitor:

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