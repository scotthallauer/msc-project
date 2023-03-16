import pickle
import os
import math
import util.mapelites as mapelites
import statistics as stat
import matplotlib.pyplot as plt
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

    AGGREGATE_MEAN_ARRAY = None
    AGGREGATE_MAX_ARRAY = None

    folder_count = 0

    for folder in folders:
      if os.path.exists(folder + "/checkpoints/gen_" + str(generations) + ".pkl"):
        flag = AGGREGATE_MEAN_ARRAY is None
        if flag:
          AGGREGATE_MEAN_ARRAY = []
          AGGREGATE_MAX_ARRAY = []
        for i in range(1, generations+1):
          if flag:
            AGGREGATE_MEAN_ARRAY.append([])
            AGGREGATE_MAX_ARRAY.append([])
          CHECKPOINT_FILENAME = folder + "/checkpoints/gen_" + str(i) + ".pkl"
          if "shom" in folder or "shet" in folder:
            with open(CHECKPOINT_FILENAME, "rb") as cp_file:
              CHECKPOINT = pickle.load(cp_file)
            POPULATION = CHECKPOINT["pop"]
            total = 0
            max = 0
            sum = 0
            for ind in POPULATION:
              fitness = ind.fitness.values[0]
              total += 1
              sum += fitness
              if fitness > max:
                max = fitness
          else:
            with open(CHECKPOINT_FILENAME, "rb") as cp_file:
              CHECKPOINT = pickle.load(cp_file)
            POPULATION = CHECKPOINT["pop"]
            CONFIG_FILENAME = CHECKPOINT["cfg"]
            CONFIG = ConfigReader(CONFIG_FILENAME)
            mapelites.init(CONFIG.get("pBehaviourFeatures", "[str]"), POPULATION)
            fitness_grid = mapelites.grid.quality_array
            total = 0
            max = 0
            sum = 0
            for x in range(len(fitness_grid)):
              for y in range(len(fitness_grid[x])):
                for z in range(len(fitness_grid[x][y])):
                  if not math.isnan(fitness_grid[x][y][z]):
                    fitness = fitness_grid[x][y][z][0]
                    total += 1
                    sum += fitness
                    if fitness > max:
                      max = fitness
          AGGREGATE_MEAN_ARRAY[i-1].append(sum/total)
          AGGREGATE_MAX_ARRAY[i-1].append(max)
        folder_count += 1
      else:
        print("Skipping run: " + (folder + "/checkpoints/gen_" + str(generations) + ".pkl") + " is missing.")

    AGGREGATE_MEAN_ARRAY = mean_flatten(AGGREGATE_MEAN_ARRAY)   
    AGGREGATE_MAX_ARRAY = mean_flatten(AGGREGATE_MAX_ARRAY)

    style = "-" if "sh" in prefix else "--"
    
    if "-e" in prefix:
      color = "g"
    elif "-m" in prefix:
      color = "b"
    elif "-d" in prefix:
      color = "r"

    plt.figure(1)
    plt.plot(AGGREGATE_MEAN_ARRAY, label=prefix, c=color, ls=style)

    plt.figure(2)
    plt.plot(AGGREGATE_MAX_ARRAY, label=prefix, c=color, ls=style)

    print("Results plotted for " + str(folder_count) + " run(s).")

  title = "Homogenous" if variant == "hom" else "Heterogenous"

  plt.figure(1)
  plt.suptitle(title, weight="bold")
  plt.title("SSGA vs. MAP-Elites", fontsize=10)
  plt.xlabel("Generation")
  plt.ylabel("Average mean fitness")
  plt.ylim(top=1.0)
  plt.legend(loc="upper left")
  plt.savefig("output/fitness-mean-" + variant + ".png", bbox_inches='tight', pad_inches=0.2)

  plt.figure(2)
  plt.suptitle(title, weight="bold")
  plt.title("SSGA vs. MAP-Elites", fontsize=10)
  plt.xlabel("Generation")
  plt.ylabel("Average max fitness")
  plt.ylim(top=1.0)
  plt.legend(loc="upper left")
  plt.savefig("output/fitness-max-" + variant + ".png", bbox_inches='tight', pad_inches=0.2)