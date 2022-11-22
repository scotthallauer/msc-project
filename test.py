from pyroborobo import Pyroborobo
from concurrent.futures import ProcessPoolExecutor, as_completed
from controller.base import BaseController
import util.convert as convert
import multiprocessing
import random
import time
import math
import globals


class Progress:

  def __init__(self, total):
    self.total = total
    self.count = 0
    self.history = []

  def increment(self):
    self.count += 1
    self.history.append(time.time())
    if len(self.history) >= 10:
      self.history.pop(0)

  def report(self):
    average_duration = (self.history[-1] - self.history[0]) / len(self.history)
    remaining_duration = (self.total - self.count) * average_duration
    return "Progress: " + str(math.floor((self.count / self.total) * 100.0)) + "% | Time Remaining: " + convert.seconds_to_readable_duration(remaining_duration) + " | Average Duration: " + convert.seconds_to_readable_duration(average_duration)


def sleep(id):
  globals.init("config/trials.properties", id, 1)
  simulator = Pyroborobo.create("config/trials.properties", controller_class=BaseController)
  simulator.start()
  duration = random.randint(10, 15)
  time.sleep(duration)
  return id


if __name__ == '__main__':
  with ProcessPoolExecutor() as executor:
    total = 100
    print(multiprocessing.cpu_count())
    progress = Progress(total)
    pool = [executor.submit(sleep, i) for i in range(total)]
    for i in as_completed(pool):
      progress.increment()
      print(end='\x1b[2K')
      print(progress.report(), end="\r", flush=True)