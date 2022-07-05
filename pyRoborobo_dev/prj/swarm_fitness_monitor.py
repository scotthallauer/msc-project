import functions.categorise as categorise

class SwarmFitnessMonitor:

  def __init__(self, method, config, controllers):
    if method == "CROWD":
      self.monitor = CrowdFitnessMonitor(config, controllers)
    elif method == "DWELL":
      self.monitor = DwellFitnessMonitor(config, controllers)
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

  def __init__(self, config, controllers):
    self.cattle = [c for c in controllers if categorise.is_cattle(c.get_id(), config.get("pMaxRobotNumber", "int"))]
    self.time_step = 0
    self.p = 0
    self.t = 0
    self.t_max = config.get("pSimulationLifetime", "int")

  def report(self):
    print("Max percent of herd gathered = " + str(self.p) + "%")
    print("Time taken to gather herd = " + str(self.t) + " time steps")

  def score(self):
    # Fs = (P / 100 + (Tmax - T) / Tmax) / 2
    return ((self.p / 100) + ((self.t_max - self.t) / self.t_max)) / 2

  def track(self):
    self.time_step += 1
    gathered_cattle = 0
    for cow in self.cattle:
      if categorise.in_target_zone(cow):
        gathered_cattle += 1
    new_p = gathered_cattle / len(self.cattle) * 100
    if new_p > self.p:
      self.p = new_p
      self.t = self.time_step

  def reset(self):
    self.time_step = 0
    self.p = 0
    self.t = 0


class DwellFitnessMonitor:

  def __init__(self, config, controllers):
    self.cattle = [c for c in controllers if categorise.is_cattle(c.get_id(), config.get("pMaxRobotNumber", "int"))]
    self.t = 0
    self.t_max = config.get("pSimulationLifetime", "int")

  def report(self):
    print("Average time in target zone per cow = " + str(self.t / len(self.cattle)) + " out of " + str(self.t_max) + " time steps")

  def score(self):
    # Fs = sum(Ti) / n * Tmax
    return self.t / (len(self.cattle) * self.t_max)

  def track(self):
    for cow in self.cattle:
      if categorise.in_target_zone(cow):
        self.t += 1

  def reset(self):
    self.t = 0