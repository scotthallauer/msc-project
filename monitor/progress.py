from multiprocessing import Process
import util.convert as convert
import time
import math

class ProgressMonitor(Process):

  def __init__(self, nb_processes: int, nb_evaluations: int, nb_generations: int, current_generation: int, process_output: dict):
    Process.__init__(self)
    self.nb_processes = nb_processes
    self.nb_evaluations = nb_evaluations
    self.nb_generations = nb_generations
    self.complete_evaluations = 0
    self.complete_generations = current_generation - 1
    self.process_output = process_output
    self.start_time = time.time()
    self.update_time = None

  def run(self):
    while True:
      self.__update_complete_evaluations()
      print(end='\x1b[2K') # clear line
      print("Progress: " + self.__get_generation_percent() + " | Time Remaining: " + self.__get_generation_duration() + " (generation), " + self.__get_run_duration() + " (run)", end="\r", flush=True)
      if self.complete_evaluations == self.nb_evaluations:
        break
      time.sleep(1)

  def __update_complete_evaluations(self):
    count = 0
    for i in range(self.nb_processes):
      if i in self.process_output:
        count += len(self.process_output[i])
    if count > self.complete_evaluations:
      self.complete_evaluations = count
      self.update_time = time.time()

  def __get_generation_percent(self):
    return str(math.floor((self.complete_evaluations / self.nb_evaluations) * 100.0)) + "%"

  def __get_generation_duration(self):
    if self.update_time is None:
      return "Estimating..."
    else:
      evaluation_duration = (self.update_time - self.start_time) / self.complete_evaluations
      generation_duration = (self.nb_evaluations - self.complete_evaluations) * evaluation_duration - (time.time() - self.update_time)
      generation_duration = max(0, generation_duration)
      return convert.seconds_to_readable_duration(generation_duration)

  def __get_run_duration(self):
    if self.update_time is None:
      return "Estimating..."
    else:
      evaluation_duration = (self.update_time - self.start_time) / self.complete_evaluations
      full_generation_duration = self.nb_evaluations * evaluation_duration
      current_generation_duration = (self.nb_evaluations - self.complete_evaluations) * evaluation_duration - (time.time() - self.update_time)
      current_generation_duration = max(0, current_generation_duration)
      run_duration = ((self.nb_generations - self.complete_generations - 1) * full_generation_duration) + current_generation_duration
      return convert.seconds_to_readable_duration(run_duration)