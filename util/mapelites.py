from qdpy.containers import Grid

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