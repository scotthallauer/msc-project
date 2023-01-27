from util.suppress import suppressor
import csv
import math
import sys
import os

if __name__ == "__main__":
  
  AGGREGATE_PREFIX = sys.argv[1]

  folders = [("output/" + folder) for folder in os.listdir("output") if folder.startswith("run_" + AGGREGATE_PREFIX)]

  for folder in folders:
    checkpoint = folder + "/checkpoints/gen_100.pkl"
    if os.path.exists(checkpoint):
      with suppressor():
        os.system("python run.py -e " + checkpoint)
    else:
      print("Skipping run: " + checkpoint + " is missing.")
      folders.remove(folder)

  fitness_avg = {}
  fitness_std = {}
  fitness_min = {}
  fitness_max = {}

  for folder in folders:
    with open(folder + "/results.csv", "r") as results:
      reader = csv.DictReader(results)
      for row in reader:
        generation = int(row["generation"])
        if generation not in fitness_avg:
          fitness_avg[generation] = []
          fitness_std[generation] = []
          fitness_min[generation] = []
          fitness_max[generation] = []
        fitness_avg[generation].append(float(row["avg"]))
        fitness_std[generation].append(float(row["std"]))
        fitness_min[generation].append(float(row["min"]))
        fitness_max[generation].append(float(row["max"]))

  with open("output/aggregate_" + AGGREGATE_PREFIX + ".csv", "w") as file:
    file.write(",".join(["generation", "avg", "std", "min", "max"]) + "\n")
    for generation in range(1, 101):
      avg = sum(fitness_avg[generation]) / len(fitness_avg[generation])
      std = math.sqrt(sum([pow(x, 2) for x in fitness_std[generation]]) / len(fitness_std[generation]))
      min = sum(fitness_min[generation]) / len(fitness_min[generation])
      max = sum(fitness_max[generation]) / len(fitness_max[generation])
      file.write(",".join(map(str, [generation, avg, std, min, max])) + "\n")

  print("Results aggregated for " + str(len(folders)) + " run(s).")