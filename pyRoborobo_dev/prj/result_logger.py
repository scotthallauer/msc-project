import os

class ResultLogger:

  def __init__(self, id, name, columns):
    self.id = id
    self.name = name
    self.columns = columns
    self.dir = "./results"
    if not os.path.exists(self.dir):
      os.makedirs(self.dir)
    self.file = open(self.dir + "/" + self.id + "_" + self.name + ".csv", "a")
    self.file.write(",".join(self.columns) + "\n")

  def append(self, values):
    self.file.write(",".join(map(str, values)) + "\n")

  def close(self):
    self.file.close()