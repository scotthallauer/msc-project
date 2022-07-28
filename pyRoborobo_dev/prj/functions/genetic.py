import random
from genome import Genome

# reference: https://www.geeksforgeeks.org/crossover-in-genetic-algorithm/
def crossover(method, child_id, parent_genome1, parent_genome2):
  weights1 = parent_genome1.get_flat_weights()
  dimensions1 = parent_genome1.get_dimensions()
  weights2 = parent_genome2.get_flat_weights()
  dimensions2 = parent_genome2.get_dimensions()
  assert len(weights1) == len(weights2)
  assert dimensions1 == dimensions2
  n = len(weights1)
  if method == "single":
    cut = random.randint(1, n - 1)
    weights3 = weights1[:cut] + weights2[cut:]
  elif method == "double":
    cut1 = random.randint(1, n - 2)
    cut2 = random.randint(cut1 + 1, n - 1)
    if random.randint(0, 1) == 0:
      weights3 = weights1[:cut1:] + weights2[cut1:cut2] + weights1[cut2:]
    else:
      weights3 = weights2[:cut1:] + weights1[cut1:cut2] + weights2[cut2:]
  elif method == "uniform":
    weights3 = []
    for i in range(n):
      if random.randint(0,1) == 0:
        weights3.append(weights1[i])
      else:
        weights3.append(weights2[i])
  else:
    raise Exception("Unsupported method code for genetic crossover")
  genome = Genome(child_id, *dimensions1)
  genome.set_flat_weights(weights3)
  return genome

# reference: https://www.tutorialspoint.com/genetic_algorithms/genetic_algorithms_mutation.htm
def mutation(method, child_id, parent_genome, probability):
  assert probability > 0 and probability <= 1
  weights = parent_genome.get_flat_weights()
  dimensions = parent_genome.get_dimensions()
  for i in range(len(weights)):
    if random.random() < probability:
      if method == "bitflip":
        weights[i] = 0 if weights[i] == 1 else 1
      else:
        raise Exception("Unsupported method code for genetic mutation")
  genome = Genome(child_id, *dimensions)
  genome.set_flat_weights(weights)
  return genome
