import pickle
import os
import statistics as stat
import matplotlib.pyplot as plt

def mean_flatten(array):
  output = []
  for i in range(len(array)):
    output.append(stat.mean(array[i]))
  return output

def graph(variant, runs=20):

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
      CHECKPOINT_FILENAME = folder + "/checkpoints/gen_100.pkl"
      if os.path.exists(CHECKPOINT_FILENAME):
        flag = AGGREGATE_MEAN_ARRAY is None
        if flag:
          AGGREGATE_MEAN_ARRAY = []
          AGGREGATE_MAX_ARRAY = []
        with open(CHECKPOINT_FILENAME, "rb") as cp_file:
          CHECKPOINT = pickle.load(cp_file)
        LOGBOOK = CHECKPOINT["log"]
        if "fitness" in LOGBOOK.chapters:
          results = LOGBOOK.chapters["fitness"].select("avg", "max")
        else:
          results = LOGBOOK.select("avg", "max")
        for i in range(len(results[0])):
          if flag:
            AGGREGATE_MEAN_ARRAY.append([])
            AGGREGATE_MAX_ARRAY.append([])
          AGGREGATE_MEAN_ARRAY[i].append(results[0][i])
          AGGREGATE_MAX_ARRAY[i].append(results[1][i])
        folder_count += 1
      else:
        print("Skipping run: " + CHECKPOINT_FILENAME + " is missing.")

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