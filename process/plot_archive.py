import pickle
import math
import util.mapelites as mapelites
import process.project_archive as prja
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from util.config_reader import ConfigReader

def max_flatten(grid, axis):
  # axis: 0 = sd, 1 = sp, 2 = dp
  plane = np.nanmax(grid, axis)
  output = []
  for r in range(len(plane)):
    output.append([c[0] for c in plane[r].tolist()])
  return output

def graph(prefix):

  AGGREGATE_PREFIX = prefix

  folders = [("output/" + folder) for folder in os.listdir("output") if folder.startswith("run_" + AGGREGATE_PREFIX)]

  AGGREGATE_ARCHIVE = None

  count = 0

  for folder in folders:
    CHECKPOINT_FILENAME = folder + "/checkpoints/gen_100.pkl"
    if os.path.exists(CHECKPOINT_FILENAME):
      count += 1
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
      flag = AGGREGATE_ARCHIVE is None
      if flag:
        AGGREGATE_ARCHIVE = []
      for x in range(len(fitness_grid)):
        if flag:
          AGGREGATE_ARCHIVE.append([])
        for y in range(len(fitness_grid[x])):
          if flag:
            AGGREGATE_ARCHIVE[x].append([])
          for z in range(len(fitness_grid[x][y])):
            if flag:
              AGGREGATE_ARCHIVE[x][y].append(math.nan)
            if math.isnan(AGGREGATE_ARCHIVE[x][y][z]) or fitness_grid[x][y][z] > AGGREGATE_ARCHIVE[x][y][z]:
              AGGREGATE_ARCHIVE[x][y][z] = fitness_grid[x][y][z]
    else:
      print("Skipping run: " + CHECKPOINT_FILENAME + " is missing.")

  plane_name = ["sd", "sp", "dp"]
  plane_labels = [["Sheep Distance", "Dog Distance"], ["Sheep Distance", "Pen Distance"], ["Dog Distance", "Pen Distance"]]

  fig, axs = plt.subplots(ncols=4, gridspec_kw=dict(width_ratios=[4,4,4,0.2]), figsize=(15, 4.2))
  plt.suptitle(AGGREGATE_PREFIX, weight="bold")
  for i in range(len(plane_name)):
    plane = max_flatten(AGGREGATE_ARCHIVE, i)
    grid = sns.heatmap(plane, cmap="plasma", cbar=False, ax=axs[i], xticklabels=False, yticklabels=False, linewidths=0.5, linecolor="black", vmin=0.0, vmax=1.0)
    grid.invert_yaxis()
    grid.set(xlabel=plane_labels[i][0], ylabel=plane_labels[i][1])
    # fix cut off lines
    grid.set_xlim(-0.1, 9.1)
    grid.set_ylim(-0.1, 9.1)
  fig.colorbar(axs[-2].collections[0], cax=axs[-1])
  plt.savefig("output/archive_" + AGGREGATE_PREFIX + ".png", bbox_inches='tight', pad_inches=0.2)

  print("Results plotted for " + str(count) + " run(s).")