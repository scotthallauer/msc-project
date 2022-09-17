import util.categorise as categorise
import globals

class SwarmFitnessMonitor:

  def __init__(self, method, controllers):
    if method == "CROWD":
      self.monitor = CrowdFitnessMonitor(controllers)
    elif method == "DWELL":
      self.monitor = DwellFitnessMonitor(controllers)
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


class CrowdFitnessMonitor:

  def __init__(self, controllers):
    self.sheep = [c for c in controllers if categorise.is_sheep(c.get_id())]
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
    self.sheep = [c for c in controllers if categorise.is_sheep(c.get_id())]
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