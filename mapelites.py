from qdpy.phenotype import *
from qdpy.containers import *
from qdpy.benchmarks import *
from qdpy.plots import *

def init():
  global grid
  maxBins = 1000
  nbFeatures = 3
  nbBinsPerDim = int(pow(maxBins, 1./nbFeatures))
  nbBins = (nbBinsPerDim,) * nbFeatures
  max_items_per_bin = 1
  fitness_domain = ((0., 1.),)
  features_domain = [(0., 1.)] * nbFeatures
  grid = Grid(shape=nbBins, max_items_per_bin=max_items_per_bin, fitness_domain=fitness_domain, features_domain=features_domain, storage_type=list)