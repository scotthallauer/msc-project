import os
import globals

class ResultLogger:

  def __init__(self, name, columns):
    self.name = name
    self.columns = columns
    self.dir = "./output/run_" + globals.run_id
    if not os.path.exists(self.dir):
      os.makedirs(self.dir)
    with open(self.dir + "/" + self.name + ".csv", "a") as file:
      file.write(",".join(self.columns) + "\n")

  def append(self, values):
    with open(self.dir + "/" + self.id + "_" + self.name + ".csv", "a") as file:
      file.write(",".join(map(str, values)) + "\n")