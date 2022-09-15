import numpy as np

class Genome:

  def __init__(self, id, nb_inputs, nb_hiddens, nb_outputs):
    self.id = id
    self.fitness = None
    self.weights = None
    self.nb_inputs = nb_inputs
    self.nb_hiddens = nb_hiddens
    self.nb_outputs = nb_outputs

  def get_id(self):
    return self.id

  def get_dimensions(self):
    return (self.nb_inputs, self.nb_hiddens, self.nb_outputs)

  def nb_weights(self):
    return np.sum([np.prod(layer.shape) for layer in self.weights])

  def init_weights(self):
    self.weights = [np.random.choice([0, 1], size = (self.nb_inputs, self.nb_hiddens)),
                    np.random.choice([0, 1], size = (self.nb_hiddens, self.nb_outputs))]

  def get_weights(self):
    return self.weights

  def get_flat_weights(self):
    all_layers = []
    for layer in self.weights:
      all_layers.append(layer.reshape(-1))
    flat_layers = np.concatenate(all_layers)
    assert (flat_layers.shape == (self.nb_weights(),))
    return flat_layers.tolist()

  def set_flat_weights(self, weights):
    self.weights = []
    self.weights.append(np.reshape(weights[:(self.nb_inputs * self.nb_hiddens):], (self.nb_inputs, self.nb_hiddens)))
    self.weights.append(np.reshape(weights[(self.nb_inputs * self.nb_hiddens)::], (self.nb_hiddens, self.nb_outputs)))

  def evaluate_network(self, inputs):
    assert len(inputs) == self.nb_inputs
    assert self.weights is not None
    outputs = inputs
    for elem in self.weights[:-1]:
      outputs = np.tanh(outputs @ elem)
    outputs = outputs @ self.weights[-1]  # linear output for last layer
    return outputs # note that outputs are not constrained to a particular range (use util.clamp for range constraints)
  
  def set_fitness(self, score):
    self.fitness = score

  def get_fitness(self):
    return self.fitness