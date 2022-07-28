# (1) SSGA: Steady State Genetic Algorithm (homogenous, only use best-performing controller in list) - https://www.geeksforgeeks.org/steady-state-genetic-algorithm-ssga/
# (2) NSGA: N-State Genetic Algorithm (heterogenous, use n best-performing controllers in list where n is population size) - https://www.geeksforgeeks.org/steady-state-genetic-algorithm-ssga/
# (3) EDQD: Embodied Distributed Quality Diversity
# (4) QED: Quality-Environment Diversity

import numpy as np
from genome import Genome
import random
import functions.genetic as genetic

class EvolutionManager:

  def __init__(self, method, config, dimensions):
    if method == "SSGA":
      self.manager = SSEvolutionManager(config, dimensions)

  def select(self, n):
    return self.manager.select(n)

  def assess(self, id, score):
    self.manager.assess(id, score)

  def propagate(self):
    self.manager.propagate()


class SSEvolutionManager:

  def __init__(self, config, dimensions):
    self.next_id = 0
    self.max_genomes = config.get("pGenomePoolSize", "int")
    self.parents = [] # genome pool
    self.children = []
    self.nb_inputs = dimensions[0]
    self.nb_hiddens = dimensions[1]
    self.nb_outputs = dimensions[2]

  def select(self, n):
    if len(self.children) == 0:
      self.propagate()
    return np.repeat(self.children[0], n)

  def assess(self, id, score):
    genome = next((g for g in self.children if g.get_id() == id), None)
    if genome != None:
      genome.set_fitness(score)
      self.children.remove(genome)
      self.parents.append(genome)
      self.parents.sort(key = lambda genome: genome.get_fitness(), reverse = True)

  def propagate(self):
    if len(self.parents) >= 2:
      genome_indices = [*range(len(self.parents))]
      parent_idx1 = random.choice(genome_indices)
      parent_idx2 = random.choice([i for i in genome_indices if i != parent_idx1])
      parent_genome1 = self.parents[parent_idx1]
      parent_genome2 = self.parents[parent_idx2]
    elif len(self.parents) == 1:
      parent_genome1 = self.parents[0]
      parent_genome2 = Genome(self.next_id, self.nb_inputs, self.nb_hiddens, self.nb_outputs)
      parent_genome2.init_weights()
      self.next_id += 1
    else:
      parent_genome1 = Genome(self.next_id, self.nb_inputs, self.nb_hiddens, self.nb_outputs)
      parent_genome1.init_weights()
      self.next_id += 1
      parent_genome2 = Genome(self.next_id, self.nb_inputs, self.nb_hiddens, self.nb_outputs)
      parent_genome2.init_weights()
      self.next_id += 1
    child_id = self.next_id
    self.next_id += 1
    child_genome = genetic.crossover("double", child_id, parent_genome1, parent_genome2)
    child_genome = genetic.mutation("bitflip", child_id, child_genome, 0.05)
    self.children.append(child_genome)
    

      


#class NSEvolutionManager:


#class EDQDEvolutionManager:


#class QEDEvolutionManager:


