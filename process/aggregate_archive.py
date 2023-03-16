import pickle
import os
import process.project_archive as prja
import util.mapelites as mapelites
from util.config_reader import ConfigReader

def aggregate(prefix, gen=200):

  AGGREGATE_PREFIX = prefix
  AGGREGATE_GENERATION = gen

  folders = [("output/" + folder) for folder in os.listdir("output") if folder.startswith("run_" + AGGREGATE_PREFIX)]

  archive_created = False
  count = 0

  for folder in folders:
    CHECKPOINT_FILENAME = folder + "/checkpoints/gen_" + AGGREGATE_GENERATION + ".pkl"
    if os.path.exists(CHECKPOINT_FILENAME):
      count += 1
      with open(CHECKPOINT_FILENAME, "rb") as cp_file:
        CHECKPOINT = pickle.load(cp_file)
      CONFIG_FILENAME = CHECKPOINT["cfg"]
      CONFIG = ConfigReader(CONFIG_FILENAME)
      if "shom" in folder or "shet" in folder:
        POPULATION = prja.project(CHECKPOINT_FILENAME)
      else: 
        POPULATION = CHECKPOINT["pop"]
      if not archive_created:
        mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]"), POPULATION)
        archive_created = True
      else:
        mapelites.grid.update(POPULATION)
    else:
      print("Skipping run: " + CHECKPOINT_FILENAME + " is missing.")

  content = dict(
    agg=AGGREGATE_PREFIX,
    gen=AGGREGATE_GENERATION, 
    pop=mapelites.grid,
    sol=[mapelites.grid.solutions[key][0] for key in mapelites.grid.solutions if len(mapelites.grid.solutions[key]) != 0]
  )

  file_dir = "./output/aggregates/"
  if not os.path.exists(file_dir):
    os.makedirs(file_dir)
  with open(file_dir + "/archive_" + AGGREGATE_PREFIX + "-" + str(AGGREGATE_GENERATION) + ".pkl", "wb") as file:
    pickle.dump(content, file)

  print("Archives aggregated for " + str(count) + " run(s) with " + str(len(content["sol"])) + " resulting solution(s).")