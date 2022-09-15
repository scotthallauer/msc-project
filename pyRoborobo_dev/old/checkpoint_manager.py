import json
import os
import functions.categorise as categorise
from datetime import datetime
import numpy as np

class CheckpointManager:

  def __init__(self, id, controllers):
    self.id = id
    self.shepherds = categorise.get_shepherds(controllers)
    self.cattle = categorise.get_cattle(controllers)
    self.dir = "./results"
    self.perm_file = self.dir + "/" + self.id + "_checkpoints.json"
    self.temp_file = self.dir + "/" + self.id + "_checkpoints.tmp"
    if not os.path.exists(self.dir):
      os.makedirs(self.dir)
    if not os.path.exists(self.perm_file):
      with open(self.perm_file, "w") as file:
        data = {
          "metadata": {
            "id": id
          },
          "checkpoints": []
        }
        json.dump(data, file)

  def load(self, generation):
    with open(self.perm_file, "r") as file:
      data = json.load(file)
      for checkpoint in data["checkpoints"]:
        if checkpoint["generation"] == generation:
          for shepherd, weight in zip(self.shepherds, np.array(checkpoint["weights"])):
            shepherd.controller.set_weights(weight)
          break

  def save(self, generation):
    data = {}
    with open(self.perm_file, "r") as file:
      data = json.load(file)
    with open(self.temp_file, "w") as file:
      checkpoint = {
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "generation": generation,
        "nb_shepherds": len(self.shepherds),
        "nb_cattle": len(self.cattle),
        "weights": [s.controller.get_genome().get_flat_weights() for s in self.shepherds]
      }
      data["checkpoints"].append(checkpoint)
      json.dump(data, file)
    os.replace(self.temp_file, self.perm_file)
