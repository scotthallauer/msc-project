import pickle
import math
import util.mapelites as mapelites
import os
import statistics as stat
import matplotlib.pyplot as plt
import process.project_archive as prja
from util.config_reader import ConfigReader

def mean_flatten(array):
  output = []
  for i in range(len(array)):
    output.append(stat.mean(array[i]))
  return output

def graph(variant, runs=20, generations=200):

  MAX_RUNS = runs

  if variant == "hom":
    AGGREGATE_PREFIXES = ["shom-e", "shom-m", "shom-d", "mhom-e", "mhom-m", "mhom-d"]
  elif variant == "het":
    AGGREGATE_PREFIXES = ["shet-e", "shet-m", "shet-d", "mhet-e", "mhet-m", "mhet-d"]

  for prefix in AGGREGATE_PREFIXES:

    folders = [("output/" + folder) for folder in os.listdir("output") if folder.startswith("run_" + prefix)]

    if len(folders) > MAX_RUNS:
      folders = folders[:MAX_RUNS]

    AGGREGATE_ARRAY = None

    folder_count = 0

    for folder in folders:
      if os.path.exists(folder + "/checkpoints/gen_" + str(generations) + ".pkl"):
        flag = AGGREGATE_ARRAY is None
        if flag:
          AGGREGATE_ARRAY = []
        for i in range(1, generations+1):
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
          qd_score = 0
          for x in range(len(fitness_grid)):
            for y in range(len(fitness_grid[x])):
              for z in range(len(fitness_grid[x][y])):
                if not math.isnan(fitness_grid[x][y][z]):
                  qd_score += fitness_grid[x][y][z][0]
          AGGREGATE_ARRAY[i-1].append(qd_score)
        folder_count += 1
      else:
        print("Skipping run: " + (folder + "/checkpoints/gen_" + str(generations) + ".pkl") + " is missing.")

    AGGREGATE_ARRAY = mean_flatten(AGGREGATE_ARRAY)

    style = "-" if "sh" in prefix else "--"
    
    if "-e" in prefix:
      color = "g"
    elif "-m" in prefix:
      color = "b"
    elif "-d" in prefix:
      color = "r"

    plt.plot(AGGREGATE_ARRAY, label=prefix, c=color, ls=style)

    print("Results plotted for " + str(folder_count) + " run(s).")

  title = "Homogenous" if variant == "hom" else "Heterogenous"

  plt.suptitle(title, weight="bold")
  plt.title("SSGA vs. MAP-Elites", fontsize=10)
  plt.xlabel("Generation")
  plt.ylabel("Average QD score")
  plt.legend(loc="upper left")
  plt.savefig("output/qdscore-" + variant + ".png", bbox_inches='tight', pad_inches=0.2)