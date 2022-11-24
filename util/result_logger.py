import os
import globals

class ResultLogger:

  def __init__(self, run_id: str, name: str, columns: list):
    self.name = name
    self.columns = columns
    self.dir = "./output/run_" + run_id
    if not os.path.exists(self.dir):
      os.makedirs(self.dir)
    with open(self.dir + "/" + self.name + ".csv", "w") as file:
      file.write(",".join(self.columns) + "\n")

  def append(self, values: list):
    with open(self.dir + "/" + self.name + ".csv", "a") as file:
      file.write(",".join(map(str, values)) + "\n")