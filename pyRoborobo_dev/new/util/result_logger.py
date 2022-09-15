import os

class ResultLogger:

  def __init__(self, id, name, columns):
    self.id = id
    self.name = name
    self.columns = columns
    self.dir = "./results"
    if not os.path.exists(self.dir):
      os.makedirs(self.dir)
    with open(self.dir + "/" + self.id + "_" + self.name + ".csv", "a") as file:
      file.write(",".join(self.columns) + "\n")

  def append(self, values):
    with open(self.dir + "/" + self.id + "_" + self.name + ".csv", "a") as file:
      file.write(",".join(map(str, values)) + "\n")