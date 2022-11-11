import globals
import math
import util.convert as convert
from time import time

class ProgressMonitor:

  def __init__(self, start_generation: int):
    self.total_generations = globals.config.get("pSimulationGenerations", "int")
    self.total_individuals = globals.config.get("pPopulationSize", "int")
    self.total_trials = globals.config.get("pEvaluationTrials", "int")
    self.current_generation = start_generation
    self.current_individual = 1
    self.current_trial = 1
    self.generation_timer = Timer()
    self.individual_timer = Timer()
    self.trial_timer = Timer()
    self.duration_history = []
  
  def start_generation(self):
    self.generation_timer.start()

  def end_generation(self):
    self.generation_timer.stop()
    self.current_generation += 1
    self.current_individual = 1
    self.current_trial = 1
    return self.generation_timer.raw_duration()

  def start_individual(self):
    self.individual_timer.start()

  def end_individual(self):
    self.individual_timer.stop()
    self.current_individual += 1
    self.current_trial = 1
    return self.individual_timer.raw_duration()

  def start_trial(self):
    self.trial_timer.start()

  def end_trial(self):
    self.trial_timer.stop()
    self.duration_history.append(self.trial_timer.raw_duration())
    if len(self.duration_history) > 10:
      self.duration_history.pop(0)
    self.current_trial += 1
    return self.trial_timer.raw_duration()

  def report(self, type="percent", scope="run"):
    if scope == "run":
      remaining_generations = self.total_generations - self.current_generation
    else:
      remaining_generations = 0
    remaining_individuals = (remaining_generations * self.total_individuals) + (self.total_individuals - self.current_individual)
    remaining_trials = (remaining_individuals * self.total_trials) + (self.total_trials - self.current_trial)
    if type == "percent":
      if scope == "run":
        total_trials = self.total_generations * self.total_individuals * self.total_trials
        current_trial = ((self.current_generation - 1) * self.total_individuals * self.total_trials) + ((self.current_individual - 1) * self.total_trials) + (self.current_trial - 1)
      elif scope == "generation":
        total_trials = self.total_individuals * self.total_trials
        current_trial = ((self.current_individual - 1) * self.total_trials) + (self.current_trial - 1)
      return str(math.floor(current_trial / total_trials * 100.0)) + "%"
    elif type == "duration":
      if len(self.duration_history) == 0:
        return "Estimating..."
      average_duration = sum(self.duration_history) / len(self.duration_history)
      return convert.seconds_to_readable_duration(average_duration * remaining_trials)

  def print(self):
    print(end='\x1b[2K') # clear line
    print("Progress: " + self.report("percent", "generation") + " | Time Remaining: " + self.report("duration", "generation") + " (gen), " + self.report("duration", "run") + " (run)", end="\r", flush=True)


class Timer:

  def __init__(self):
    self.start_time = None
    self.end_time = None

  def start(self):
    self.reset()
    self.start_time = time()

  def stop(self):
    self.end_time = time()

  def raw_duration(self):
    return (self.end_time - self.start_time)

  def readable_duration(self):
    return convert.seconds_to_readable_duration(self.raw_duration())

  def reset(self):
    self.start_time = None
    self.end_time = None