import pickle
import os
import statistics as stat
import matplotlib.pyplot as plt
from util.config_reader import ConfigReader

# first project ASHET reference individuals into MAP-Elites to see which population individuals have the same behaviour (and can be considered duplicates)

def mean_flatten(array):
  output = []
  for i in range(len(array)):
    output.append(stat.mean(array[i]))
  return output

def graph(runs=20, generations=200):

  MAX_RUNS = runs

  AGGREGATE_PREFIXES = ["ashet-e", "ashet-m", "ashet-d", "amhet-e", "amhet-m", "amhet-d"]

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
          with open(CHECKPOINT_FILENAME, "rb") as cp_file:
            CHECKPOINT = pickle.load(cp_file)
          POPULATION = CHECKPOINT["pop"]
          swarm_sizes = []
          for individual in POPULATION:
            swarm_sizes.append(len(set(individual)))
          AGGREGATE_ARRAY[i-1].append(stat.mean(swarm_sizes))
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

  title = "Heterogeneous"

  plt.suptitle(title, weight="bold")
  plt.title("SSGA vs. MAP-Elites", fontsize=10)
  plt.xlabel("Generation")
  plt.ylabel("Average unique behaviours in swarm")
  plt.legend(loc="upper left")
  plt.savefig("output/swarm.png", bbox_inches='tight', pad_inches=0.2)