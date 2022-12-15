from qdpy.containers import Grid
from qdpy.plots import plotGrid, plotGridSubplots
import matplotlib.pyplot as plt

def init(_behaviour_features: list, _grid: Grid = None):
  global grid
  global behaviour_features
  behaviour_features = _behaviour_features
  max_bins = 1000
  nb_features = len(behaviour_features)
  nb_bins_per_dim = int(pow(max_bins, 1./nb_features))
  nb_bins = (nb_bins_per_dim,) * nb_features
  max_items_per_bin = 1
  fitness_domain = ((0., 1.),)
  features_domain = [(0., 1.)] * nb_features
  if _grid is None:
    grid = Grid(shape=nb_bins, max_items_per_bin=max_items_per_bin, fitness_domain=fitness_domain, features_domain=features_domain, storage_type=list)
  else:
    grid = _grid

def plot(filename: str):
  global grid
  global behaviour_features
  nb_features = len(behaviour_features)
  features_domain = [(0., 1.)] * nb_features
  if nb_features <= 2:
    plotGrid(grid.quality_array[...,0], filename, plt.get_cmap("nipy_spectral_r"), featuresBounds=features_domain, fitnessBounds=(0., 1.))
  else:
    plotGridSubplots(grid.quality_array[...,0], filename, plt.get_cmap("nipy_spectral_r"), featuresBounds=features_domain, fitnessBounds=(0., 1.))