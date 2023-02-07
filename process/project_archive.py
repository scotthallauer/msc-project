import os
import pickle
import util.mapelites as mapelites
from util.config_reader import ConfigReader

def project(checkpoint_filename):

  with open(checkpoint_filename, "rb") as cp_file:
    CHECKPOINT = pickle.load(cp_file)
  
  POPULATION = CHECKPOINT["pop"]
  CONFIG_FILENAME = CHECKPOINT["cfg"]
  CONFIG = ConfigReader(CONFIG_FILENAME)
  mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]"))
  mapelites.grid.update(POPULATION)

  return mapelites.grid