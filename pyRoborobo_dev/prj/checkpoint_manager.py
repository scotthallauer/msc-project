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
    if not os.path.exists(self.dir):
      os.makedirs(self.dir)
    with open(self.dir + "/" + self.id + "_checkpoints.json", "w") as file:
      data = {
        "metadata": {
          "id": id
        },
        "checkpoints": []
      }
      json.dump(data, file)

  def load(self, generation):
    with open(self.dir + "/" + self.id + "_checkpoints.json", "r") as file:
      data = json.load(file)
      for checkpoint in data["checkpoints"]:
        if checkpoint["generation"] == generation:
          for shepherd, weight in zip(self.shepherds, np.array(checkpoint["weights"])):
            shepherd.controller.set_weights(weight)
          break

  def save(self, generation):
    data = {}
    with open(self.dir + "/" + self.id + "_checkpoints.json", "r") as file:
      data = json.load(file)
    with open(self.dir + "/" + self.id + "_checkpoints.json", "w") as file:
      checkpoint = {
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "generation": generation,
        "nb_shepherds": len(self.shepherds),
        "nb_cattle": len(self.cattle),
        "weights": [s.controller.get_flat_weights().tolist() for s in self.shepherds]
      }
      data["checkpoints"].append(checkpoint)
      json.dump(data, file)
