import pickle
import os
import statistics as stat
import matplotlib.pyplot as plt

def mean_flatten(array):
  output = []
  for i in range(len(array)):
    output.append(stat.mean(array[i]))
  return output

def graph():

  AGGREGATE_PREFIXES = ["shom-e", "shom-d", "mhom-e", "mhom-m", "mhom-d"]

  for prefix in AGGREGATE_PREFIXES:

    folders = [("output/" + folder) for folder in os.listdir("output") if folder.startswith("run_" + prefix)]

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

    plt.figure(1)
    plt.plot(AGGREGATE_MEAN_ARRAY, label=prefix)

    plt.figure(2)
    plt.plot(AGGREGATE_MAX_ARRAY, label=prefix)

    print("Results plotted for " + str(folder_count) + " run(s).")

  plt.figure(1)
  plt.suptitle("Homogenous", weight="bold")
  plt.title("SSGA vs. MAP-Elites", fontsize=10)
  plt.xlabel("Generation")
  plt.ylabel("Average mean solution fitness")
  plt.ylim(top=1.0)
  plt.legend()
  plt.savefig("output/fitness-mean-hom.png", bbox_inches='tight', pad_inches=0.2)

  plt.figure(2)
  plt.suptitle("Homogenous", weight="bold")
  plt.title("SSGA vs. MAP-Elites", fontsize=10)
  plt.xlabel("Generation")
  plt.ylabel("Average max solution fitness")
  plt.ylim(top=1.0)
  plt.legend()
  plt.savefig("output/fitness-max-hom.png", bbox_inches='tight', pad_inches=0.2)