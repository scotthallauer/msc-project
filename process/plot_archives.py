import pickle
import math
import util.mapelites as mapelites
import process.project_archive as prja
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from util.config_reader import ConfigReader

def max_flatten(grid, axis):
  # axis: 0 = sd, 1 = sp, 2 = dp
  plane = np.nanmax(grid, axis)
  output = []
  for r in range(len(plane)):
    output.append([c[0] for c in plane[r].tolist()])
  return output

def graph(runs=20, generations=200):

  MAX_RUNS = runs

  AGGREGATE_PREFIXES = ["ashet", "amhet"]
  DIFFICULTY_SUFFIXES = ["e", "m", "d"]

  AGGREGATE_ARCHIVES = {}

  for algorithm in AGGREGATE_PREFIXES:

    AGGREGATE_ARCHIVES[algorithm] = {}

    for difficulty in DIFFICULTY_SUFFIXES:

      AGGREGATE_ARCHIVES[algorithm][difficulty] = None
      
      folders = [("output/" + folder) for folder in os.listdir("output") if folder.startswith("run_" + algorithm + "-" + difficulty)]

      if len(folders) > MAX_RUNS:
        folders = folders[:MAX_RUNS]

      count = 0

      for folder in folders:
        CHECKPOINT_FILENAME = folder + "/checkpoints/gen_" + str(generations) + ".pkl"
        if os.path.exists(CHECKPOINT_FILENAME):
          count += 1
          if "shom" in folder or "shet" in folder or "amhet" in folder:
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
          flag = AGGREGATE_ARCHIVES[algorithm][difficulty] is None
          if flag:
            AGGREGATE_ARCHIVES[algorithm][difficulty] = []
          for x in range(len(fitness_grid)):
            if flag:
              AGGREGATE_ARCHIVES[algorithm][difficulty].append([])
            for y in range(len(fitness_grid[x])):
              if flag:
                AGGREGATE_ARCHIVES[algorithm][difficulty][x].append([])
              for z in range(len(fitness_grid[x][y])):
                if flag:
                  AGGREGATE_ARCHIVES[algorithm][difficulty][x][y].append(math.nan)
                if math.isnan(AGGREGATE_ARCHIVES[algorithm][difficulty][x][y][z]) or fitness_grid[x][y][z] > AGGREGATE_ARCHIVES[algorithm][difficulty][x][y][z]:
                  AGGREGATE_ARCHIVES[algorithm][difficulty][x][y][z] = fitness_grid[x][y][z]
        else:
          print("Skipping run: " + CHECKPOINT_FILENAME + " is missing.")

  plane_name = ["sd", "sp", "dp"]
  plane_labels = [["S", "D"], ["S", "P"], ["D", "P"]]


  fig = plt.figure(figsize=(13, 4.75)) #13, 8.5
  axs = {}
  outer = gridspec.GridSpec(len(AGGREGATE_PREFIXES)+1, len(DIFFICULTY_SUFFIXES), wspace=0.25, hspace=0.7)

  for y, algorithm in enumerate(AGGREGATE_PREFIXES):
    axs[algorithm] = {}
    for x, difficulty in enumerate(DIFFICULTY_SUFFIXES):
      axs[algorithm][difficulty] = []
      inner = gridspec.GridSpecFromSubplotSpec(1, len(plane_name), subplot_spec=outer[y*len(DIFFICULTY_SUFFIXES)+x], wspace=0.27, hspace=0.2)
      for i in range(len(plane_name)):
        ax = plt.Subplot(fig, inner[i])
        axs[algorithm][difficulty].append(ax)
        if i == 1:
          ax.set_title(algorithm + "-" + difficulty, weight="bold", size=10)
        plane = max_flatten(AGGREGATE_ARCHIVES[algorithm][difficulty], i)
        grid = sns.heatmap(plane, cmap="plasma", cbar=False, ax=ax, xticklabels=False, yticklabels=False, linewidths=0.5, linecolor="black", vmin=0.0, vmax=1.0)
        grid.invert_yaxis()
        grid.set_xlabel(plane_labels[i][0], labelpad=0, size=8)
        grid.set_ylabel(plane_labels[i][1], labelpad=0, size=8)
        # fix cut off lines
        grid.set_xlim(-0.1, 9.2)
        grid.set_ylim(-0.2, 9.1)
        fig.add_subplot(ax)
        print("Plotted " + algorithm + "-" + difficulty)

  axs["none"] = {}
  for x, difficulty in enumerate(DIFFICULTY_SUFFIXES):
    axs["none"][difficulty] = []
    inner = gridspec.GridSpecFromSubplotSpec(1, len(plane_name), subplot_spec=outer[len(AGGREGATE_PREFIXES)*len(DIFFICULTY_SUFFIXES)+x], wspace=0.3, hspace=0)
    for i in range(len(plane_name)):
      ax = plt.Subplot(fig, inner[i])
      axs["none"][difficulty].append(ax)
  
  fig.colorbar(axs["amhet"]["m"][0].collections[0], ax=axs["none"]["m"], label="Fitness", orientation="horizontal", location="bottom")
  plt.savefig("output/allocation-archives.png", bbox_inches='tight', pad_inches=0.2)

  print("Results plotted.")
  return


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
  fig.colorbar(axs[-2].collections[0], cax=axs[-1], label="Fitness")
  plt.savefig("output/archive_" + AGGREGATE_PREFIX + ".png", bbox_inches='tight', pad_inches=0.2)

  print("Results plotted for " + str(count) + " run(s).")