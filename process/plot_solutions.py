import pickle
import math
import util.mapelites as mapelites
import os
import statistics as stat
import matplotlib.pyplot as plt
import process.project_archive as prja
from util.config_reader import ConfigReader

def median_flatten(array):
  output = []
  for i in range(len(array)):
    output.append(stat.median(array[i]))
  return output

def graph():

  AGGREGATE_PREFIXES = ["shom-e", "shom-d", "shet-e", "shet-m", "shet-d"]

  for prefix in AGGREGATE_PREFIXES:

    folders = [("output/" + folder) for folder in os.listdir("output") if folder.startswith("run_" + prefix)]

    AGGREGATE_ARRAY = None

    folder_count = 0

    for folder in folders:
      if os.path.exists(folder + "/checkpoints/gen_100.pkl"):
        flag = AGGREGATE_ARRAY is None
        if flag:
          AGGREGATE_ARRAY = []
        for i in range(1, 101):
          if flag:
            AGGREGATE_ARRAY.append([])
          CHECKPOINT_FILENAME = folder + "/checkpoints/gen_" + str(i) + ".pkl"
          if "shom" in folder or "shet" in folder:
            grid = prja.project(CHECKPOINT_FILENAME)
            fitness_grid = grid.quality_array
          else:
            with open(CHECKPOINT_FILENAME, "rb") as cp_file:
              CHECKPOINT = pickle.load(cp_file)
            POPULATION = CHECKPOINT["pop"]
            CONFIG_FILENAME = CHECKPOINT["cfg"]
            CONFIG = ConfigReader(CONFIG_FILENAME)
            mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]"), POPULATION)
            fitness_grid = mapelites.grid.quality_array
          solution_count = 0
          for x in range(len(fitness_grid)):
            for y in range(len(fitness_grid[x])):
              for z in range(len(fitness_grid[x][y])):
                if not math.isnan(fitness_grid[x][y][z]):
                  solution_count += 1
          AGGREGATE_ARRAY[i-1].append(solution_count)
        folder_count += 1
      else:
        print("Skipping run: " + CHECKPOINT_FILENAME + " is missing.")

    AGGREGATE_ARRAY = median_flatten(AGGREGATE_ARRAY)

    plt.plot(AGGREGATE_ARRAY, label=prefix)

    print("Results plotted for " + str(folder_count) + " run(s).")

  plt.suptitle("SSGA", weight="bold")
  plt.title("Homogenous vs. Heterogenous", fontsize=10)
  plt.xlabel("Generation")
  plt.ylabel("Median number of unique solutions in archive")
  plt.legend()
  plt.savefig("output/solutions-s.png", bbox_inches='tight', pad_inches=0.2)